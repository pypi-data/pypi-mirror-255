#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Model for Scan in the application """
import pickle
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field
from requests import JSONDecodeError, Response

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import (
    convert_datetime_to_regscale_string,
    get_current_datetime,
    create_progress_object,
)
from regscale.core.utils.date import normalize_date


class Scan(BaseModel):
    id: int
    uuid: Optional[str] = None
    scanningTool: Optional[str] = None
    sicuraId: Optional[str] = None
    tenableId: Optional[str] = None
    scanDate: Optional[str] = None
    scannedIPs: Optional[int] = None
    checks: Optional[int] = None
    vInfo: Optional[int] = None
    vLow: Optional[int] = None
    vMedium: Optional[int] = None
    vHigh: Optional[int] = None
    vCritical: Optional[int] = None
    parentId: Optional[int] = None
    parentModule: Optional[str] = None
    createdById: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    isPublic: bool = True
    dateCreated: str = Field(default_factory=get_current_datetime)
    tenantsId: Optional[int] = 1

    def __hash__(self) -> int:
        """
        Hash items in Scan class

        :return: Hashed Scan
        :rtype: int
        """
        fmt = "%Y-%m-%dT%H:%M:%S"
        return hash(
            (
                self.tenableId,
                self.parentId,
                self.parentModule,
                normalize_date(self.scanDate, fmt),
            )
        )

    def __eq__(self, other) -> bool:
        """
        Compare two Scan objects if they are equal

        :param other: Other Scan to compare
        :return: True if equal, False otherwise
        :rtype: bool
        """
        fmt = "%Y-%m-%dT%H:%M:%S"
        if isinstance(other, Scan):
            return (
                self.tenableId == other.tenableId
                and self.parentId == other.parentId
                and self.parentModule == other.parentModule
                and normalize_date(self.scanDate, fmt)
                == normalize_date(other.scanDate, fmt)
            )

        return (
            self.tenableId == other["tenableId"]
            and self.parentId == other["parentId"]
            and self.parentModule == other["parentModule"]
            and normalize_date(self.scanDate, fmt)
            == normalize_date(other["scanDate"], fmt)
        )

    @staticmethod
    def post_scan(app: Application, api: Api, scan: "Scan") -> "Scan":
        """
        Post a Scan to RegScale.

        :param Application app: Application Instance
        :param Api api: Api Instance
        :param Scan scan: Scan Object
        :return: RegScale Scan
        :rtype: Scan
        """
        res = api.post(url=app.config["domain"] + "/api/scanhistory", json=scan.dict())
        if res.status_code != 200:
            api.logger.error(res)
        return Scan(**res.json())

    @staticmethod
    def group_vulns_by_severity(associated_vulns: List[dict]) -> Dict[str, List[dict]]:
        """
        Groups vulnerabilities by severity

        :param List[dict] associated_vulns: A list of associated vulnerabilities
        :return: Dictionary of vulnerabilities grouped by severity
        :rtype: Dict[str, List[dict]]
        """
        return {
            vuln["severity"]: [
                v for v in associated_vulns if v["severity"] == vuln["severity"]
            ]
            for vuln in associated_vulns
        }

    @staticmethod
    def get_existing_scan_history(app: Application, reg_asset: dict) -> List[dict]:
        """
        Gets existing scan history for a RegScale asset

        :param Application app: Application Instance
        :param dict reg_asset: RegScale Asset
        :return: List of existing scan history
        :rtype: List[dict]
        """
        api = Api()
        res = api.get(
            url=app.config["domain"]
            + f"/api/scanhistory/getAllByParent/{reg_asset.id}/assets"
        )
        if not res.raise_for_status():
            return res.json()

    @staticmethod
    def create_scan_from_tenable(
        associated_vulns: List[dict], reg_asset: dict, config: dict, tenant_id: int
    ) -> "Scan":
        """
        Creates a Scan object from a Tenable scan

        :param List[dict] associated_vulns: List of associated vulnerabilities
        :param dict reg_asset: RegScale Asset
        :param dict config: Application Config
        :param int tenant_id: Tenant ID
        :return: Scan object
        :rtype: Scan
        """
        grouped_vulns = Scan.group_vulns_by_severity(associated_vulns)
        return Scan(
            id=0,
            uuid=associated_vulns[0]["scan"]["uuid"],
            scanningTool="NESSUS",
            tenableId=associated_vulns[0]["scan"]["uuid"],
            scanDate=convert_datetime_to_regscale_string(
                associated_vulns[0]["scan"]["started_at"]
            ),
            scannedIPs=1,
            checks=len(associated_vulns),
            vInfo=len(grouped_vulns["info"]) if "info" in grouped_vulns else 0,
            vLow=len(grouped_vulns["low"]) if "low" in grouped_vulns else 0,
            vMedium=len(grouped_vulns["medium"]) if "medium" in grouped_vulns else 0,
            vHigh=len(grouped_vulns["high"]) if "high" in grouped_vulns else 0,
            vCritical=(
                len(grouped_vulns["critical"]) if "critical" in grouped_vulns else 0
            ),
            parentId=reg_asset.id,
            parentModule="assets",
            createdById=config["userId"],
            lastUpdatedById=config["userId"],
            dateCreated=convert_datetime_to_regscale_string(datetime.now()),
            tenantsId=tenant_id,
        )

    @staticmethod
    def prepare_scan_history_for_sync(
        app: Application,
        nessus_list: List[dict],
        existing_assets: List[dict],
    ) -> List["Scan"]:
        """
        Prepares scan history data for synchronization.

        :param Application app: The Application object to use for database operations.
        :param List[dict] nessus_list: A list of Nessus scan history data.
        :param List[dict] existing_assets: A list of existing Asset objects to compare against.
        :return: A tuple containing three lists: new Scan objects, updated Scan objects, and a list of Asset objects.
        :rtype: Tuple[List[Scan], List[Scan], List[Asset]]
        """
        new_scan_history = []
        assets = {asset["asset"]["uuid"] for asset in nessus_list}
        asset_count = 0
        api = Api()
        config = app.config
        tenant_id = api.get(url=api.config["domain"] + "/api/tenants/config").json()[
            "id"
        ]

        def process_asset(asset) -> None:
            """
            Process an asset from the Nessus scan history data.

            :param str asset: Asset UUID
            :return: None
            """
            nonlocal asset_count
            asset_count += 1
            if asset_count % 100 == 0:
                app.logger.debug(f"Processing asset {asset_count} of {len(assets)}")
            associated_vulns = [
                ness for ness in nessus_list if ness["asset"]["uuid"] == asset
            ]
            reg_assets = [reg for reg in existing_assets if reg["tenableId"] == asset]
            if reg_assets:
                reg_asset = reg_assets[0] if reg_assets else None
                existing_scans = Scan.get_existing_scan_history(app, reg_asset)
                scan = Scan.create_scan_from_tenable(
                    associated_vulns, reg_asset, config, tenant_id
                )
                if scan not in existing_scans:
                    new_scan_history.append(scan)

        with ThreadPoolExecutor(max_workers=30) as executor:
            executor.map(process_asset, assets)

        return new_scan_history

    @staticmethod
    def sync_scan_history_to_regscale(
        app: Application,
        new_scan_history: List["Scan"],
    ) -> List["Scan"]:
        """
        Synchronizes scan history to RegScale

        :param Application app: Application Instance
        :param List[Scan] new_scan_history: List of new scan history items
        :return: Tuple of Response and Scan
        :rtype: Tuple[List[Response], List[Scan]]
        """
        tup_res = []
        if new_scan_history:
            app.logger.info(
                f"Inserting {len(new_scan_history)} new scan history item(s)"
            )
            tup_res = Scan.bulk_insert(app, new_scan_history)
            app.logger.info("Done!")
        return tup_res

    @staticmethod
    def convert_from_tenable(
        str_path: str,
        existing_assets: List[dict],
    ) -> List["Scan"]:
        """
        Converts a TenableScan object to a RegScale Scan object

        :param str str_path: A path to a temporary directory to store the Nessus scan history data.
        :param List[dict] existing_assets: Existing RegScale Assets
        :return: List of RegScale Scans
        :rtype: List[Scan]
        """
        app = Application()
        existing_scan_history_list = []
        file_list = list(Path(str_path).glob("*"))
        with create_progress_object() as progress:
            processing_pages = progress.add_task(
                f"[#ef5d23]Processing {len(file_list)} pages from Tenable...",
                total=len(file_list),
            )
            for index, file in enumerate(file_list):
                app.logger.debug(f"Processing page {index + 1} of {len(file_list)}")
                with open(file, "rb") as vuln_file_wrapper:
                    new_scan_data = []
                    # import dict from json file
                    nessus_list = [
                        vuln.dict() for vuln in pickle.load(vuln_file_wrapper)
                    ]
                    new_scan_data.extend(
                        Scan.prepare_scan_history_for_sync(
                            app, nessus_list, existing_assets
                        )
                    )
                existing_scan_history_list.extend(
                    Scan.sync_scan_history_to_regscale(app, new_scan_data)
                )
                progress.update(processing_pages, advance=1)

        return existing_scan_history_list

    @staticmethod
    def bulk_insert(
        app: Application, scans: List["Scan"], max_workers: Optional[int] = 10
    ) -> List["Scan"]:
        """Bulk insert assets using the RegScale API and ThreadPoolExecutor

        :param Application app: Application Instance
        :param List[Scan] scans: List of Scans
        :param Optional[int] max_workers: Max Workers, defaults to 10
        :return: List of Tuples containing Response and Scan
        :rtype: List[Tuple[Response, Scan]]"""
        api = Api()
        res = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(
                    Scan.insert_scan,
                    app,
                    api,
                    scan,
                )
                for scan in scans
            ]
        for future in as_completed(futures):
            res.append(future.result()[1])
        return res

    @staticmethod
    def bulk_update(
        app: Application, scans: List["Scan"], max_workers: Optional[int] = 10
    ) -> List["Scan"]:
        """
        Bulk update assets using the RegScale API and ThreadPoolExecutor

        :param Application app: Application Instance
        :param List[Scan] scans: List of Scans
        :param Optional[int] max_workers: Max Workers, defaults to 10
        :return: List of Scan
        :rtype: List[Scan]
        """
        api = Api()
        res = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(
                    Scan.update_scan,
                    app,
                    api,
                    scan,
                )
                for scan in scans
            ]
        for future in as_completed(futures):
            res.append(future.result()[1])
        return res

    @staticmethod
    def update_scan(
        app: Application, api: Api, regscale_scan: "Scan"
    ) -> Tuple[Response, "Scan"]:
        """
        Api wrapper to update a scan

        :param Application app: Application Instance
        :param Api api: Api Instance
        :param Scan regscale_scan: Regscale Scan
        :return: RegScale Scan and Response
        :rtype: Tuple[Response, Scan]
        """
        scan_res = api.put(
            url=app.config["domain"]
            + "/api/scanHistory",  # no ID needed on this endpoint
            json=regscale_scan.model_dump(),
        )
        regscale_scan.id = scan_res.json()["id"]
        return scan_res, regscale_scan

    @staticmethod
    def insert_scan(
        app: Application, api: Api, regscale_scan: "Scan"
    ) -> Tuple[Response, "Scan"]:
        """
        Api wrapper to insert a scan

        :param Application app: Application Instance
        :param Api api: Api Instance
        :param Scan regscale_scan: Regscale Scan
        :return: RegScale Scan and Response
        :rtype: Tuple[Response, Scan]
        """
        scan_res = api.post(
            url=app.config["domain"] + "/api/scanHistory",
            json=regscale_scan.model_dump(),
        )
        if not scan_res.ok:
            api.logger.error(
                f"Unable to insert scan: {scan_res.status_code}: {scan_res.reason}. {scan_res.text}"
            )
        else:
            try:
                regscale_scan.id = scan_res.json()["id"]
            except (KeyError, JSONDecodeError) as ex:
                api.logger.error(f"Unable to insert scan: {ex}")
        return scan_res, regscale_scan
