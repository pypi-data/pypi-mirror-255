#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Dataclasses for a Tenable integration """
import collections
import gc
import glob
import pickle
import shutil
import tempfile
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from logging import Logger
from pathlib import Path
from typing import Any, List, Optional, Set, Tuple, Union
from uuid import UUID

import nessus_file_reader as nfr
from pydantic import BaseModel
from tenable.io.exports.iterator import ExportsIterator

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import (
    check_file_path,
    convert_datetime_to_regscale_string,
    create_progress_object,
    epoch_to_datetime,
    error_and_exit,
    get_current_datetime,
    log_memory,
)
from regscale.core.app.utils.nessus_utils import (
    IteratorConsumptionError,
    determine_available_space,
    determine_identifier,
    filter_severity,
    get_cpe_data,
    get_due_delta,
    get_minimum_severity,
    lookup_kev,
    software,
)
from regscale.core.app.utils.regscale_utils import check_module_id
from regscale.integrations.public.cisa import pull_cisa_kev
from regscale.models.integration_models.tenable import (
    Plugin,
    TenableBasicAsset,
    TenablePort,
    TenableScan,
)
from regscale.models.regscale_models import (
    Asset,
    File,
    Issue,
    Link,
    Scan,
    SoftwareInventory,
    Vulnerability,
)


class NessusReport(BaseModel):
    """
    Tenable Nessus Report (maps to regscale vuln)
    """

    asset: TenableBasicAsset
    output: Optional[str]
    plugin: Plugin
    port: TenablePort
    scan: TenableScan
    severity: Optional[str] = None
    severity_id: int
    severity_default_id: int
    severity_modification_type: str
    first_found: Optional[datetime] = None
    last_fixed: Optional[datetime] = None
    last_found: Optional[datetime] = None
    state: Optional[str] = None
    indexed: Optional[datetime] = None

    @staticmethod
    def create_asset(config, asset_properties: dict) -> Asset:
        """
        Create an asset

        :param dict config: The configuration dictionary
        :param dict asset_properties: A dictionary of asset properties
        :return: An Asset object
        :rtype: Asset
        """
        aws_ident = [
            aws
            for aws in asset_properties["all_tags"]
            if "aws-instance-instanceId" == aws["name"]
        ]
        aws_identifier = aws_ident[0]["val"] if aws_ident else ""

        return Asset(
            **{
                "id": 0,
                "name": asset_properties["name"],
                "ipAddress": asset_properties["host_ip"],
                "isPublic": True,
                "status": "Active (On Network)",
                "assetCategory": "Hardware",
                "tenableId": asset_properties[
                    "tenable_id"
                ],  # UUID from Nessus HostProperties tag
                "bLatestScan": True,
                "bAuthenticatedScan": True,
                "scanningTool": "Tenable",
                "assetOwnerId": asset_properties["user_id"],
                "netBIOS": asset_properties["netbios_name"],
                "macAddress": asset_properties["mac_address"],
                "assetType": "Other",
                "fqdn": asset_properties["fqdn"],
                "awsIdentifier": aws_identifier,
                "VLANId": asset_properties["vlan_id"],
                "location": asset_properties["location"],
                "operatingSystem": Asset.find_os(asset_properties["operating_system"]),
                "systemAdministratorId": config["userId"],
                "parentId": asset_properties["parent_id"],
                "parentModule": "securityplans",
            }
        )

    @staticmethod
    def get_vulnerability_data(file_vuln) -> dict:
        """
        Get the vulnerability data

        :param file_vuln: A file vulnerability xml element
        :return: dict of vulnerability data
        :rtype: dict
        """

        def get(field_name: str) -> Optional[str]:
            """
            Get the field value

            :param str field_name: The field name to get
            :return: Field value
            :rtype: Optional[str]
            """
            try:
                result = file_vuln.find(field_name).text
            except AttributeError:
                result = None
            return result

        description = get("description")
        plugin_text = get("plugin_output")
        base = get("cvss_base_score")
        if base:
            cve_base_score = float(base)
        else:
            cve_base_score = 0.0
        cve = get("cve")
        synopsis = get("synopsis")
        solution = get("solution")
        severity = Vulnerability.determine_cvss3_severity_text(cve_base_score)
        return {
            "description": description,
            "synopsis": synopsis,
            "plugin_text": plugin_text,
            "cve": cve,
            "cve_base_score": cve_base_score,
            "severity": severity,
            "solution": solution,
        }

    @staticmethod
    def create_vulnerability(
        file_vuln, asset_properties, vulnerability_data
    ) -> Vulnerability:
        """Create a Vulnerability object

        :param file_vuln: File Vulnerability xml element
        :param asset_properties: A dictionary of asset properties
        :param vulnerability_data: A dictionary of vulnerability data
        :return: Vulnerability object
        :rtype: Vulnerability
        """
        extra_data = {
            "synopsis": vulnerability_data["synopsis"],
            "solution": vulnerability_data["solution"],
            "report_uuid": asset_properties["nessus_report_uuid"],
        }
        return Vulnerability(
            id=0,
            extra_data=extra_data,
            queryId=0,
            firstSeen="",
            cve=vulnerability_data["cve"],
            cvsSv3BaseScore=vulnerability_data["cve_base_score"],
            lastSeen=epoch_to_datetime(asset_properties["last_scan"]),
            dns=asset_properties["name"],
            title=file_vuln.attrib.get("pluginName"),
            ipAddress=asset_properties["scanner_ip"],
            createdById=asset_properties["user_id"],
            name=file_vuln.attrib.get("pluginName"),
            description=vulnerability_data["description"],
            severity=vulnerability_data["severity"],
            port=file_vuln.attrib.get("port"),
            protocol=file_vuln.attrib.get("protocol"),
            plugInId=file_vuln.attrib.get("pluginID"),
            plugInText=vulnerability_data["plugin_text"],
            plugInName=file_vuln.attrib.get("pluginName"),
            asset_name=asset_properties["name"],
            parentId=asset_properties["asset_id"],
            parentModule="assets",
        )

    @staticmethod
    def create_scan(
        asset_properties: dict,
        count_low: int,
        count_medium: int,
        count_high: int,
        count_critical: int,
    ) -> dict:
        """
        Create a scan

        :param dict asset_properties: A dictionary of asset properties
        :param int count_low: Scan count low
        :param int count_medium: Scan count medium
        :param int count_high: Scan count high
        :param int count_critical: Scan count critical
        :return: dict of scan data
        :rtype: dict
        """
        return {
            "id": 0,
            "scanningTool": "NESSUS",
            "scanDate": epoch_to_datetime(asset_properties["last_scan"]),
            "scannedIPs": asset_properties["asset_count"],
            "checks": count_low + count_medium + count_high + count_critical,
            "vInfo": 0,
            "vLow": count_low,
            "vMedium": count_medium,
            "vHigh": count_high,
            "vCritical": count_critical,
            "parentId": asset_properties["asset_id"],
            "parentModule": "assets",
            "createdById": asset_properties["user_id"],
            "lastUpdatedById": asset_properties["user_id"],
            "isPublic": True,
            "tenantsId": None,
            "tenableId": asset_properties["nessus_report_uuid"],
            "dateCreated": get_current_datetime(),
            "dateLastUpdated": get_current_datetime(),
        }

    @staticmethod
    def get_vulnerabilities(
        root, file_asset, asset_properties
    ) -> Tuple[List[Vulnerability], dict]:
        """
        Get the vulnerabilities of an asset

        :param root: XML Root
        :param file_asset: XML file asset
        :param asset_properties: A dictionary of asset properties
        :return: Tuple of vulnerabilities and scan
        :rtype: Tuple[List[Vulnerability], dict]
        """
        asset_name = file_asset.attrib.get("name")
        vulnerabilities = []
        counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for file_vuln in root.iterfind(
            f"./Report/ReportHost[@name='{asset_name}']/ReportItem"
        ):
            vulnerability_data = NessusReport.get_vulnerability_data(file_vuln)
            counts[vulnerability_data["severity"]] += 1
            vulnerability = NessusReport.create_vulnerability(
                file_vuln,
                asset_properties,
                vulnerability_data,
            )
            vulnerabilities.append(vulnerability)
        # Create a scan
        scan = NessusReport.create_scan(
            asset_properties,
            counts["low"],
            counts["medium"],
            counts["high"],
            counts["critical"],
        )
        return vulnerabilities, scan

    @staticmethod
    def update_vulnerability_scans(
        app: Application, scans: List[dict], vulnerabilities: List[dict]
    ) -> Tuple[List[Vulnerability], List[dict]]:
        """
        Update the vulnerability scans

        :param Application app: The application instance
        :param List[dict] scans: The scans
        :param List[dict] vulnerabilities: The vulnerabilities to be updated
        :return: The updated vulnerabilities and scans
        :rtype: Tuple[List[Vulnerability], List[dict]]
        """
        api = Api()
        res = api.post(
            url=app.config["domain"] + "/api/scanhistory/batchcreate", json=scans
        )
        inserted_scans = []
        updated_vulnerabilities: List[Vulnerability] = []
        if res.ok and res.status_code == 200:
            inserted_scans = res.json()
            for posted_scan in res.json():
                scan_id = posted_scan["id"]
                asset_id = posted_scan["parentId"]
                vulns = next(
                    (
                        item
                        for item in vulnerabilities
                        if item["scan_asset"] == asset_id
                    ),
                    None,
                )

                for vulnerability in vulns["vulns"]:
                    vulnerability.scanId = scan_id
                    updated_vulnerabilities.append(vulnerability)
        return updated_vulnerabilities, inserted_scans

    @staticmethod
    def process_file_asset(*args: Any) -> Tuple[dict, dict, dict]:
        """
        Process a file asset

        :param args: Additional arguments
        :return: A tuple of dictionaries
        :rtype: Tuple[dict, dict, dict]
        """
        (
            app,
            root,
            regscale_ssp_id,
            cpe_list,
            file_asset,
            existing_assets,
            existing_assets_in_scan,
        ) = args[0]
        logger = create_logger()
        logger.debug("Processing asset: %s", file_asset.attrib.get("name"))
        asset_properties = NessusReport.get_asset_properties(
            app, (root, cpe_list, file_asset, regscale_ssp_id)
        )
        asset = NessusReport.create_asset(app.config, asset_properties)
        if asset not in existing_assets:
            res = asset.create()
        else:
            existing_asset = [
                existing_asset
                for existing_asset in existing_assets
                if asset == existing_asset
            ][0]
            asset.id = existing_asset["id"]
            res = asset.save()

        if asset.id:
            asset_id = asset.id
        else:
            asset_id = res.json()["id"] if res.ok else 0
        asset_properties["asset_id"] = asset_id
        vulnerabilities, scan = NessusReport.get_vulnerabilities(
            root,
            file_asset,
            asset_properties=asset_properties,
        )
        dat = {"scan_asset": asset_id, "vulns": vulnerabilities}
        existing_assets_in_scan.add(asset_id)
        return scan, dat, asset_properties

    @staticmethod
    def get_asset_properties(app: Application, *args: Any) -> dict:
        """
        Get the asset properties

        :param Application app: The application instance
        :param args: Additional arguments
        :return: dict of asset properties
        :rtype: dict
        """
        logger = create_logger()
        (root, cpe_items, file_asset, regscale_ssp_id) = args[0]

        start = time.time()
        nessus_report_uuid = nfr.scan.server_preference_value(root, "report_task_id")
        nfr_start = time.time()
        asset_name = nfr.host.report_host_name(file_asset)
        temp = f"./Report/ReportHost[@name='{asset_name}']/HostProperties/tag"
        operating_system = nfr.host.detected_os(file_asset)
        netbios = nfr.host.netbios_network_name(root, file_asset)
        resolved_ip = nfr.host.resolved_ip(file_asset)
        scanner_ip = nfr.host.scanner_ip(root, file_asset)
        nfr_end = time.time()
        logger.debug("NFR functions ran in %s seconds", nfr_end - nfr_start)
        software_inventory = software(
            cpe_items, file_asset
        )  # Placeholder for CPE lookup,
        tag_map = {
            "id": "tenable_id",
            "host-ip": "host_ip",
            "host-fqdn": "fqdn",
            "mac-address": "macaddress",
            "HOST_START_TIMESTAMP": "begin_scan",
            "HOST_END_TIMESTAMP": "last_scan",
            "aws-instance-instanceId": "aws_instance_id",
            "aws-instance-vpc-id": "vlan_id",
            "aws-instance-region": "location",
        }

        tag_values = {tag_map[key]: "" for key in tag_map}

        for file_asset_tag in root.iterfind(temp):
            tag_name = file_asset_tag.attrib.get("name")
            tag_value = file_asset_tag.text
            if tag_name in tag_map:
                variable_name = tag_map[tag_name]
                tag_values[variable_name] = tag_value
        end = time.time()
        logger.debug("Time to process asset properties: %s", end - start)
        return {
            "name": asset_name,
            "operating_system": operating_system,
            "tenable_id": (
                tag_values["tenable_id"] if "tenable_id" in tag_values else ""
            ),
            "netbios_name": netbios["netbios_computer_name"],
            "all_tags": [
                {"name": attrib.attrib["name"], "val": attrib.text}
                for attrib in root.iterfind(temp)
            ],
            "mac_address": tag_values["macaddress"],
            "last_scan": tag_values["last_scan"],
            "user_id": app.config["userId"],
            "parent_id": regscale_ssp_id,
            "resolved_ip": resolved_ip,
            "asset_count": len(list(root.iter("ReportHost"))),
            "scanner_ip": scanner_ip,
            "host_ip": tag_values["host_ip"],
            "fqdn": tag_values["fqdn"],
            "software_inventory": software_inventory,
            "nessus_report_uuid": nessus_report_uuid,
            "aws_identifier": tag_values["aws_instance_id"],
            "vlan_id": tag_values["vlan_id"],
            "location": tag_values["location"],
        }

    @staticmethod
    def build_software_inventory(
        app: Application, asset_id: int, inventory: List[dict]
    ) -> Tuple[List[SoftwareInventory], List[SoftwareInventory]]:
        """
        Build and insert the software inventory

        :param Application app: The application instance
        :param int asset_id: The ID of the asset
        :param List[dict] inventory: The software inventory
        :return: A tuple of lists of inventory objects
        :rtype: Tuple[List[SoftwareInventory], List[SoftwareInventory]]
        """
        existing_inventory = []
        insert_inventory = []
        update_inventory = []
        res = Api().get(
            url=app.config["domain"]
            + f"/api/softwareInventory/getAllByParent/{asset_id}"
        )
        if res.ok and res.status_code == 200:
            existing_inventory = res.json()
        for soft in inventory:
            software_inv = SoftwareInventory(
                **{
                    "id": 0,
                    "UUID": "",
                    "name": soft["title"],
                    "version": soft["version"],
                    "function": "",
                    "patchLevel": "",
                    "parentHardwareAssetId": asset_id,
                    "parentSoftwareAssetId": None,
                    "dateLastUpdated": None,
                    "createdById": app.config["userId"],
                    "dateCreated": None,
                    "lastUpdatedById": "",
                    "isPublic": True,
                }
            )
            if software_inv.name not in {
                inv["name"] for inv in existing_inventory if "name" in inv.keys()
            }:
                insert_inventory.append(software_inv)
            else:
                software_inv.id = [
                    inv
                    for inv in existing_inventory
                    if software_inv.name == inv["name"]
                ][0]["id"]
                update_inventory.append(software_inv)
        return insert_inventory, update_inventory

    @staticmethod
    def process_nessus_file(
        file: str, regscale_ssp_id: int, app: Application, logger: Logger
    ) -> Tuple[Set[Issue], Set[str]]:
        """
        Process a Nessus file

        :param str file: The path to the Nessus file to be processed
        :param int regscale_ssp_id: The ID of the parent security plan
        :param Application app: The application instance
        :param Logger logger: The logger instance
        :return: A tuple containing three sets: new issues, updated issues,
            and existing assets in the scan.
        :rtype: Tuple[Set[Issue], Set[Issue], Set[str]]
        """
        job_progress = create_progress_object()
        root = nfr.file.nessus_scan_file_root_element(file)
        _, cpe_list = get_cpe_data()

        logger.info("Processing Nessus file: %s", file)
        assets = nfr.scan.report_hosts(root)
        existing_assets = Asset.find_assets_by_parent(
            app=app, parent_id=regscale_ssp_id, parent_module="securityplans"
        )
        inventory_to_insert: List[SoftwareInventory] = []
        inventory_to_update: List[SoftwareInventory] = []
        existing_assets_in_scan = set()
        vulns_to_post = []
        scans_to_post = []
        inserted_scans = []
        asset_props = []
        with job_progress:
            asset_task = job_progress.add_task(
                f"[#ba1d49]Processing {len(assets)} assets from {Path(file).name}...",
                total=len(assets),
            )
            with ThreadPoolExecutor() as executor:
                futures = []
                start = time.time()
                end = time.time()
                for file_asset in assets:
                    logger.debug("CPE element list created in %s seconds", end - start)
                    future = executor.submit(
                        NessusReport.process_file_asset,
                        (
                            app,
                            root,
                            regscale_ssp_id,
                            cpe_list,
                            file_asset,
                            existing_assets,
                            existing_assets_in_scan,
                        ),
                    )
                    futures.append(future)
                for future in as_completed(futures):
                    scans, vuln_data, asset_properties = future.result()
                    vulns_to_post.append(vuln_data)
                    scans_to_post.append(scans)
                    asset_props.append(asset_properties)
                    job_progress.update(asset_task, advance=1)
            build_inventory_task = job_progress.add_task(
                "[#1f88f6]Building software inventory..",
                total=len(asset_props),
            )
            for asset in asset_props:
                (
                    insert_inventory,
                    update_inventory,
                ) = NessusReport.build_software_inventory(
                    app=app,
                    asset_id=asset["asset_id"],
                    inventory=asset["software_inventory"],
                )
                inventory_to_insert.extend(insert_inventory)
                inventory_to_update.extend(update_inventory)
                job_progress.update(build_inventory_task, advance=1)
            vulns, scans = NessusReport.update_vulnerability_scans(
                app, scans_to_post, vulns_to_post
            )
            Vulnerability.post_vulnerabilities(app=app, vulnerabilities=vulns)
            inventory_task = job_progress.add_task(
                "[#f68d1f]Processing software inventory..",
                total=len(insert_inventory) + len(update_inventory),
            )
            with ThreadPoolExecutor() as executor:
                futures: List[Future] = []
                for inventory in inventory_to_insert:
                    futures.append(
                        executor.submit(
                            SoftwareInventory.insert,
                            app=app,
                            obj=inventory,
                        )
                    )
                for inventory in inventory_to_update:
                    futures.append(
                        executor.submit(
                            SoftwareInventory.update,
                            app=app,
                            obj=inventory,
                        )
                    )
                for future in as_completed(futures):
                    future.result()
                    job_progress.update(inventory_task, advance=1)
            inserted_scans.extend(scans)
        # Make pylint happy
        return (
            NessusReport.generate_issues(app, logger, regscale_ssp_id, vulns_to_post),
            existing_assets_in_scan,
        )

    @staticmethod
    def process_nessus_files(regscale_ssp_id: int, folder_path: Path) -> None:
        """
        Process multiple Nessus files

        :param int regscale_ssp_id: The ID of the parent security plan
        :param Path folder_path: The full path to the folder of Nessus files
        :return: None
        """

        def move_files(ssp_id: int) -> None:
            """
                    Move files to processed directory

            :return: None
            """
            for file in file_collection:
                api = Api()
                # Create processed directory if it doesn't exist, and copy file to it.
                file_path = Path(file)
                new_file_path = ""
                processed_dir = file_path.parent / "processed"
                check_file_path(str(processed_dir.absolute()))
                logger.debug("Moving %s to %s", file, processed_dir / file)
                try:
                    if ssp_id:
                        file_name = f"{file_path.stem}_{get_current_datetime('%Y_%m_%d-%I_%M_%S_%p')}".replace(
                            " ", "_"
                        )
                        # Rename to friendly file name and post to Regscale
                        new_file_path = file_path.rename(
                            file_path.parent / (file_name + ".nessus")
                        )
                        logger.info(
                            "Renaming %s to %s, and posting to RegScale...",
                            file_path.name,
                            new_file_path.name,
                        )
                        File.upload_file_to_regscale(
                            file_name=str(new_file_path.absolute()),
                            parent_id=ssp_id,
                            parent_module="securityplans",
                            api=api,
                        )
                        shutil.move(new_file_path, processed_dir)
                except shutil.Error:
                    logger.debug(
                        "File %s already exists in %s",
                        new_file_path.name,
                        processed_dir,
                    )

        app = Application()
        api = Api()
        logger = create_logger()
        mod_check = check_module_id(
            parent_id=regscale_ssp_id, parent_module="securityplans"
        )
        if not mod_check:
            raise ValueError(
                "Invalid SSP ID, please make sure the SSP exists "
                + "on your RegScale system."
            )
        if isinstance(folder_path, str):
            folder_path = Path(folder_path)
        file_collection = glob.glob(str(folder_path / "*.nessus"))
        if len(file_collection) == 0:
            error_and_exit("No Nessus files found in folder path.")
        # Loop through nessus files in folder_path
        insert_issues: Set[Issue] = set()
        assets_scanned: Set[int] = set()
        for file in file_collection:
            (
                new_issues,
                existing_asset_in_scan,
            ) = NessusReport.process_nessus_file(file, regscale_ssp_id, app, logger)
            insert_issues.update(new_issues)
            assets_scanned.update(existing_asset_in_scan)

        # Save
        issues = Issue.bulk_insert(app=app, issues=list(insert_issues))
        logger.info("Generating Issue Links")
        new_links = []
        # Update links
        for iss in issues:
            if iss.id:
                # Create Link
                link = Link(
                    title=f"Tenable Plugin {iss.pluginId}",
                    url=f"https://www.tenable.com/plugins/nessus/{iss.pluginId}",
                    parentID=iss.id,
                    parentModule="issues",
                )
                new_links.append(link)

        Link.bulk_insert(api, new_links)
        # move files
        move_files(ssp_id=regscale_ssp_id)

    @staticmethod
    def prepare_tenable_data(
        existing_assets: List[dict],
        vulns: Union[ExportsIterator, UUID],
        logger: Logger,
        **kwargs,
    ) -> Tuple[Any, List[Scan]]:
        """
        Prepares Tenable data for download

        :param List[dict] existing_assets: A list of existing Asset objects to compare against
        :param Union[ExportsIterator, UUID] vulns: An iterable of NessusReport objects to prepare for download
        :param Logger logger: The logger object to use for logging
        :param kwargs: The keyword arguments for this function
        :return: A tuple containing a file wrapper and a list of scans.
        :rtype: Tuple[Any, List[Scan]]
        """
        log_memory()
        tmp_dir = tempfile.TemporaryDirectory()
        logger.info("Preparing to download Tenable Data ...")
        report_vulns, count, saved_count, file_count = [], 0, 0, 0
        index = 0
        has_data = False
        job_progress = create_progress_object()
        # give the user a progress object so they know it is working
        with job_progress:
            fetching_task = job_progress.add_task(
                "[#f8b737]Fetching vulnerability data from Tenable...",
                total=100,
            )
            for index, tenable_data in enumerate(vulns):
                # don't let the user the process is done prematurely
                if index and job_progress.tasks[fetching_task].completed < 95:
                    job_progress.update(fetching_task, advance=0.05)
                if vulns.page:
                    has_data = True
                (
                    report_vulns,
                    count,
                    saved_count,
                    file_count,
                ) = NessusReport.process_tenable_data(
                    index,
                    tenable_data,
                    vulns,
                    report_vulns,
                    count,
                    saved_count,
                    file_count,
                    tmp_dir,
                    **kwargs,
                )
            # mark the task complete
            job_progress.update(fetching_task, advance=100)
        if has_data and index == 0:
            raise IteratorConsumptionError(
                "There was a problem downloading Tenable data, please try again."
            )

        logger.info(
            "%i of %i records saved for processing.",
            saved_count,
            index + 1,
        )
        logger.info("Processing scan data from Tenable...")
        existing_scans = Scan.convert_from_tenable(
            tmp_dir.name,
            existing_assets=existing_assets,
        )
        report_vulns.clear()
        gc.collect()
        log_memory()

        return tmp_dir, existing_scans

    @staticmethod
    def process_tenable_data(
        index: int,
        tenable_data: Any,
        vulns: ExportsIterator,
        report_vulns: List["NessusReport"],
        count: int,
        filtered: int,
        file_count: int,
        tmp_dir: Any,
        **kwargs,
    ):
        """
        Process Tenable data

        :param int index: The index of the current record
        :param Any tenable_data: The Tenable data to process
        :param ExportsIterator vulns: The Tenable data iterator
        :param List[NessusReport] report_vulns: The list of NessusReport objects
        :param int count: The count of records processed
        :param int filtered: The count of records filtered
        :param int file_count: The count of files processed
        :param Any tmp_dir: The temporary directory
        :param kwargs: The keyword arguments for this function
        """

        report = NessusReport(**tenable_data)
        report_vulns.append(report)
        count += 1
        filtered += 1

        if index and len(report_vulns) == len(vulns.page):
            # when count matches size of vulns.page, dump to disk
            report_vulns, file_count = NessusReport.dump_report_to_disk(
                report_vulns, file_count, tmp_dir, vulns, **kwargs
            )
            NessusReport.log_download_progress(index=index, saved_count=filtered)
            # reset the count and start a new page
            count = 0

        return report_vulns, count, filtered, file_count

    @staticmethod
    def log_download_progress(**kwargs):
        """
        Log the download progress

        :param kwargs The keyword arguments for this function
        :return: None
        """
        app = Application()
        saved_count = kwargs.get("saved_count", 0)
        if saved_count > 0 and saved_count % 500 == 0:
            app.logger.info("Processed  %i records ..", saved_count)

    @staticmethod
    def dump_report_to_disk(
        report_vulns, file_count, tmp_dir, vulns, **kwargs
    ) -> Tuple[List["NessusReport"], int]:
        """
        Dump report to disk

        :param List[NessusReport] report_vulns: The list of NessusReport objects
        :param int file_count: The count of files processed
        :param Any tmp_dir: The temporary directory
        :param ExportsIterator vulns: The Tenable data iterator
        :param kwargs: The keyword arguments for this function
        :return: A tuple containing the report_vulns list and the file count
        :rtype: Tuple[List[NessusReport], int]
        """
        vuln_file = tempfile.NamedTemporaryFile(dir=tmp_dir.name, delete=False)
        if report_vulns:
            try:
                with open(vuln_file.name, "wb") as vuln_file_wrapper:
                    pickle.dump(report_vulns, vuln_file_wrapper)
                    file_count += 1
                    if file_count == 1:
                        NessusReport.check_disk_space(
                            vuln_file_wrapper, vulns, **kwargs
                        )
                    vuln_file.close()
                report_vulns.clear()
                gc.collect()
            except OSError as e:
                error_and_exit(f"Error saving file: {e}")

        return report_vulns, file_count

    @staticmethod
    def check_disk_space(vuln_file_wrapper, vulns, **kwargs):
        """Check if there is enough disk space to process Tenable data

        :param Any vuln_file_wrapper: The file wrapper for the vulnerability file
        :param ExportsIterator vulns: The Tenable data iterator
        :param kwargs: The keyword arguments for this function
        """
        client = kwargs.get("client")
        app = kwargs.get("app")
        total_chunks = (
            client.exports.status(export_uuid=vulns.uuid, export_type="vulns")
        )["total_chunks"]
        file_size = vuln_file_wrapper.tell()
        app.logger.debug("Space needed: %i", file_size * total_chunks)
        if file_size * total_chunks > determine_available_space():
            error_and_exit(
                "The estimated space to process Tenable data is below the current available space."
            )

    @staticmethod
    def create_regscale_vuln(**kwargs) -> Optional[Vulnerability]:
        """
        Prepares Tenable data for download

        :param kwargs: The keyword arguments for this function
        :return: A tuple containing two lists: NessusReport objects and Scan objects
        :rtype: Tuple[List[NessusReport], List[Scan]]
        """
        app = kwargs.get("app")
        parent_id = kwargs.get("parent_id")
        parent_module = kwargs.get("parent_module")
        existing_assets = kwargs.get("existing_assets")
        report = kwargs.get("report")
        existing_scans = kwargs.get("existing_scans")
        existing_vulns = kwargs.get("existing_vulns")
        asset = None
        res = [
            asset
            for asset in existing_assets
            if asset["otherTrackingNumber"] == report.asset.uuid
        ]
        if res:
            asset = res[0]
            parent_id = asset.id if isinstance(asset, Asset) else asset["id"]
            parent_module = "assets"

        # refresh existing scans
        if scans := [
            scan
            for scan in existing_scans
            if scan.tenableId == report.scan.uuid and scan.parentId == parent_id
        ]:
            regscale_vuln = Vulnerability(
                id=0,
                uuid=report.scan.uuid,
                scanId=scans[0].id,
                parentId=parent_id,
                parentModule=parent_module,
                lastSeen=convert_datetime_to_regscale_string(report.last_found),
                firstSeen=convert_datetime_to_regscale_string(report.first_found),
                daysOpen=None,
                dns=report.asset.hostname,
                ipAddress=report.asset.ipv4,
                mitigated=None,
                operatingSystem=(
                    report.asset.operating_system[0]
                    if report.asset.operating_system
                    else None
                ),
                port=report.port.port,
                protocol=report.port.protocol,
                severity="moderate" if report.severity == "medium" else report.severity,
                plugInName=report.plugin.name,
                plugInId=report.plugin.id,
                cve=None,
                vprScore=None,
                tenantsId=0,
                exploitAvailable=report.plugin.exploit_available,
                cvss3BaseScore=report.plugin.cvss3_base_score,
                title=f"{report.output} on asset {report.asset.hostname}",
                description=report.output,
                plugInText=report.plugin.description,
                createdById=app.config["userId"],
                lastUpdatedById=app.config["userId"],
                dateCreated=convert_datetime_to_regscale_string(datetime.now()),
            )
            if regscale_vuln not in existing_vulns:
                return regscale_vuln
            if existing_vulns:
                regscale_vuln.id = [
                    vuln for vuln in existing_vulns if vuln == regscale_vuln
                ][0].id
                return regscale_vuln

        return None

    @staticmethod
    def sync_to_regscale(
        vulns: Union[ExportsIterator, UUID],
        parent_id: int,
        parent_module="securityplans",
        **kwargs,
    ) -> None:
        """
        Synchronizes Tenable vulns to RegScale

        :param Union[ExportsIterator, UUID] vulns: An iterable of NessusReport objects to prepare for download
        :param int parent_id: The ID of the parent object associated with the data
        :param str parent_module: The name of the parent module associated with the data, defaults to "securityplans"
        :param kwargs: The keyword arguments for this function
        :return: None
        """
        logger = create_logger()
        app = Application()
        existing_assets = Asset.get_all_by_parent(
            parent_id=parent_id, parent_module="securityplans"
        )
        if len(existing_assets) == 0:
            error_and_exit(
                "In order to sync vulnerabilities, you must have assets for the provided Security Plan in RegScale."
            )
        tmp_dir, existing_scans = NessusReport.prepare_tenable_data(
            existing_assets, vulns, logger, client=kwargs.get("client"), app=app
        )
        existing_vulns = NessusReport.existing_vulns(
            existing_scans=existing_scans, app=app
        )
        logger.info("Saving Tenable Vulnerabilities to RegScale...")
        threads = 100
        filelst = list(Path(tmp_dir.name).glob("*"))
        asset_vuln_tmp_dir = NessusReport.convert_to_asset_vuln_files(filelst)
        count_posted = 0
        logger.info("Iterating through cached data to update RegScale ..")
        for file in Path(asset_vuln_tmp_dir.name).glob("*"):
            file_vulns = []
            with open(file, "rb") as fp:
                file_vulns.extend(pickle.load(fp))
            with ThreadPoolExecutor(max_workers=threads) as executor:
                futures = [
                    executor.submit(
                        NessusReport.create_regscale_vuln,
                        parent_id=parent_id,
                        parent_module=parent_module,
                        report=report,
                        existing_assets=existing_assets,
                        existing_scans=existing_scans,
                        existing_vulns=existing_vulns,
                        app=app,
                    )
                    for report in file_vulns
                ]
            new_vulns = NessusReport.process_vuln_results(
                futures, file_vulns, existing_vulns, logger
            )
            logger.debug("Found %s new vulnerabilities", len(new_vulns))
            log_memory()
            responses = Vulnerability.post_vulnerabilities(
                app=app, vulnerabilities=new_vulns
            )
            count_posted += len([res for res in responses if isinstance(res, bytes)])
        asset_vuln_tmp_dir.cleanup()
        if count_posted:
            logger.info("Successfully posted %i new vulnerabilities", count_posted)

    @staticmethod
    def convert_to_asset_vuln_files(filelst: List):
        """
        Convert a List of pickle files representing pages of Tenable IO to a dict of asset hostnames with Tenable IO vulns as the payload.

        :param List filelst: A list of file paths to pickle files
        :return None
        """
        res = {}
        for file in filelst:
            with open(file, "rb") as fp:
                vulns = pickle.load(fp)
                for host in {vuln.asset.hostname for vuln in vulns}:
                    if host not in res:
                        res[host] = []
                    # Filter out the info vulns
                    res[host].extend(
                        [vuln.dict() for vuln in vulns if vuln.asset.hostname == host]
                    )
                del vulns
                gc.collect()
        # tmp_dir.close()
        log_memory()
        host_temp = tempfile.TemporaryDirectory()
        for host in res.keys():
            # Pickle every host list, this will make it easier to process and not have to worry about memory
            with tempfile.NamedTemporaryFile(
                dir=host_temp.name, delete=False
            ) as host_file:
                try:
                    with open(host_file.name, "wb") as fp:
                        # We can be assured that every item in the list contains all the reports for a given host
                        pickle.dump([NessusReport(**vuln) for vuln in res[host]], fp)
                        # clear data from dictionary after dump
                        res[host].clear()
                except OSError as e:
                    error_and_exit(f"Error saving file: {e}")
        del res
        gc.collect()
        log_memory()
        return host_temp

    @staticmethod
    def process_vuln_results(
        futures: List[Future],
        vulns: List["NessusReport"],
        existing_vulns: List[Vulnerability],
        logger: Logger,
    ) -> list[Vulnerability]:
        """
        Processes the results of the vulnerability futures

        :param List[Future] futures: A list of Future objects representing the vulnerability futures
        :param List["NessusReport"] vulns: A list of NessusReport objects representing vulnerabilities
        :param List[Vulnerability] existing_vulns: A list of existing Vulnerability objects to compare against
        :param Logger logger: The logger object to use for logging
        :return: list[Vulnerability]
        """
        app = Application()
        new_vulns = []
        count = 0
        for future in as_completed(futures):
            count += 1
            if count % 5000 == 0:
                logger.info(
                    "Processed %i of %i %s.",
                    count,
                    len(vulns),
                    "vulnerability" if len(new_vulns) == 1 else "vulnerabilities",
                )
            regscale_vuln = future.result()
            if regscale_vuln is not None and (regscale_vuln not in existing_vulns):
                new_vulns.append(regscale_vuln)
        counters = collections.Counter(
            [
                v.severity
                for v in [fut.result() for fut in as_completed(futures) if fut.result()]
            ]
        )
        if len(new_vulns) > 0:
            logger.info("Vuln Breakdown: %s", dict(counters))
            logger.info(
                "Found %i new %s with a severity > %s.",
                len(new_vulns),
                "vulnerability" if len(new_vulns) == 1 else "vulnerabilities",
                app.config["tenableMinimumSeverityFilter"],
            )
        return new_vulns

    @staticmethod
    def existing_vulns(
        existing_scans: List[Scan], app: Application
    ) -> List[Vulnerability]:
        """Existing Vulns

        :param List[Scan] existing_scans: A list of existing scans
        :param Application app: Application Instance
        :return: List of Vulns
        :rtype: List[Vulnerability]
        """
        results = []
        api = Api()
        for scan_id in {scan.id for scan in existing_scans}:
            results.extend(
                api.get(
                    url=app.config["domain"]
                    + f"/api/vulnerability/getAllByParent/{scan_id}"
                ).json()
            )
        return [Vulnerability(**vuln) for vuln in results]

    @staticmethod
    def generate_issues(
        app: Application,
        logger: Logger,
        regscale_ssp_id: int,
        vulns_to_post: List[Vulnerability],
    ) -> Set[Issue]:
        """
        Generate issues from a Nessus file

        :param Application app: The RegScale application instance
        :param Logger logger: The logger instance
        :param int regscale_ssp_id: The ID of the parent security plan
        :param List[Vulnerability] vulns_to_post: A list of vulnerabilities to be posted
        :return: A tuple containing : new issues and updated issues
        :rtype: Set[Issue]
        """
        # Update the issues in the SSP
        logger.info("Generating issues...")

        # Get all assets in SSP
        existing_issues = Issue.fetch_issues_by_parent(
            app=app, regscale_id=regscale_ssp_id, regscale_module="securityplans"
        )
        # Filter tenable issues
        tenable_issues = [
            iss for iss in existing_issues if iss.pluginId or iss.tenableId
        ]
        # Create issues
        issues = NessusReport.create_issues(app, vulns_to_post, regscale_ssp_id)

        # create updated issues
        new_issues = NessusReport.update_issue_sets(issues, tenable_issues)

        return new_issues

    @staticmethod
    def update_issue_sets(
        issues: List[Issue], tenable_issues: List[Issue]
    ) -> Set[Issue]:
        """
        Update issue sets

        :param List[Issue] issues: A list of issue sets to be updated
        :param List[Issue] tenable_issues: A list of tenable issues
        :return: A tuple containing two sets of issues: new issues and updated issues
        :rtype: Tuple[Set[Issue], Set[Issue]]
        """

        def is_new_issue() -> bool:
            """
            Check if an issue is new.

            :return: True if the issue is new, False otherwise.
            :rtype: bool
            """
            return issue.title not in {iss.title for iss in tenable_issues}

        new_issues: Set[Issue] = set()

        for issue in issues:
            if is_new_issue():
                new_issues.add(issue)

        return new_issues

    @staticmethod
    def create_issue(
        app: Application,
        item: List[Vulnerability],
        asset: Asset,
        severity: str,
        plugin_id: int,
        regscale_ssp_id: int,
        kev_due_date: str,
        kev_list: Any,
    ) -> Issue:
        """Create RegScale Issue

        :param app: The application instance
        :param item: The NessusReport object
        :param asset: The related asset
        :param severity: The severity of the issue
        :param plugin_id: The plugin ID
        :param regscale_ssp_id: The ID of the parent security plan
        :param kev_due_date: The due date of the issue (from the KEV)
        :param kev_list: The list of CVEs (from the KEV)
        :return: An Issue object
        """
        fmt = "%Y-%m-%d %H:%M:%S"
        poam = severity.lower() in ["low", "moderate", "high", "critical"]
        iss = Issue(
            isPoam=poam,
            title=item.title,
            description=item.description,
            status="Open",
            severityLevel=Issue.assign_severity(severity),
            issueOwnerId=app.config["userId"],
            pluginId=plugin_id,
            assetIdentifier=determine_identifier(asset),
            securityPlanId=regscale_ssp_id,
            recommendedActions=item.extra_data["solution"],
            cve=item.cve,
            kevList=kev_list,
            autoApproved="No",
        )
        iss.originalRiskRating = iss.assign_risk_rating(severity)
        iss.dateFirstDetected = item.lastSeen
        if kev_due_date and (datetime.strptime(kev_due_date, fmt) > datetime.now()):
            iss.dueDate = kev_due_date
        elif kev_due_date and (datetime.strptime(kev_due_date, fmt) <= datetime.now()):
            iss.dueDate = datetime.strftime(datetime.now() + timedelta(days=1), fmt)
        else:
            due_dt = datetime.strptime(iss.dateFirstDetected, fmt) + timedelta(
                get_due_delta(app, severity)
            )
            iss.dueDate = datetime.strftime(due_dt, fmt)
            if due_dt < datetime.now():
                iss.dueDate = datetime.strftime(
                    datetime.now() + timedelta(get_due_delta(app, severity)), fmt
                )
        iss.identification = "Vulnerability Assessment"
        iss.tenableNessusId = item.extra_data["report_uuid"]
        iss.parentId = regscale_ssp_id
        iss.parentModule = "securityplans"
        iss.basisForAdjustment = "Tenable Nessus import."
        return iss

    @staticmethod
    def create_issues(
        app: Application, vulns: List[dict], regscale_ssp_id: int
    ) -> List[Issue]:
        """
        Create RegScale issues

        :param app: The application instance
        :param vulns: The list of vulnerabilities
        :param regscale_ssp_id: The ID of the parent security plan
        :return: A list of issues
        """
        logger = create_logger()
        minimum_severity = get_minimum_severity(app)
        list_of_vulns = NessusReport.get_vuln_list(vulns)
        issues = []
        existing_assets = Asset.get_all_by_parent(
            parent_id=regscale_ssp_id, parent_module="securityplans"
        )
        kev_data = pull_cisa_kev()
        kev_due_date = None
        kev_list = None
        for item in filter_severity(list_of_vulns, minimum_severity):
            asset = next(
                asset for asset in existing_assets if asset.id == item.parentId
            )
            severity = {
                dat.severity for dat in list_of_vulns if dat.plugInName == item.title
            }.pop()
            plugin_id = {
                dat.plugInId for dat in list_of_vulns if dat.plugInName == item.title
            }.pop()
            if app.config["issues"]["tenable"]["useKev"]:
                kev, kev_due_date = lookup_kev(item.cve, kev_data)
                kev_list = kev["cveID"] if kev else None
            iss = NessusReport.create_issue(
                app,
                item,
                asset,
                severity,
                plugin_id,
                regscale_ssp_id,
                kev_due_date,
                kev_list,
            )
            if (iss.assetIdentifier, iss.title) not in {
                (issue.assetIdentifier, issue.title) for issue in issues
            }:
                issues.append(iss)
        logger.debug(len(issues))
        return issues

    @staticmethod
    def get_vuln_list(vulns: List[dict]) -> List[Vulnerability]:
        """
        Convert a list of data to a list of Vulnerability objects

        :param List[dict] vulns: A list of vulnerabilities
        :return: A list of vulnerabilities
        :rtype: List[Vulnerability]
        """
        list_of_vulns = []
        for dat in vulns:
            if "vulns" in dat.keys():
                list_of_vulns.extend(dat["vulns"])
        return list_of_vulns
