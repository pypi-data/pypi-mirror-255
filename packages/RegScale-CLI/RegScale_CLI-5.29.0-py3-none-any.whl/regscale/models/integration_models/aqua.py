"""
Aqua Scan information
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from itertools import groupby
from operator import attrgetter
from pathlib import Path
from typing import List, Optional

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import get_current_datetime, is_valid_fqdn
from regscale.models.integration_models.container_scan import ContainerScan
from regscale.models.regscale_models import SoftwareInventory
from regscale.models.regscale_models.asset import Asset
from regscale.models.regscale_models.issue import Issue
from regscale.models.regscale_models.vulnerability import Vulnerability


class Aqua(ContainerScan):
    """Aqua Scan information"""

    def __init__(self, name: str, app: Application, **kwargs):
        """
        Initialize Scan

        :param str name: Name of the scan
        :param Application app: RegScale Application object
        :param str file_path: Path to the data files
        :param int parent_id: RegScale System Security Plan ID
        :param str parent_module: RegScale parent module
        """
        self.name = name
        self.vuln_title = "Vulnerability Name"
        self.fmt = "%m/%d/%y"
        self.dt_format = "%Y-%m-%d %H:%M:%S"
        self.image_name = "Image Name"
        self.ffi = "First Found on Image"
        self.headers = [
            "Registry",
            self.image_name,
            "Image Build Date",
            "Image Digest",
            "OS",
            "Resource",
            "Resource Type",
            "Installed Version",
            "Vulnerability Name",
            "Publish Date",
            "Referenced By",
            "Vendor CVSS v2 Severity",
            "Vendor CVSS v2 Score",
            "Vendor CVSS v2 Vectors",
            "Vendor CVSS v3 Severity",
            "Vendor CVSS v3 Score",
            "Vendor CVSS v3 Vectors",
            "Vendor URL",
            "NVD CVSS v2 Severity",
            "NVD CVSS v2 Score",
            "NVD CVSS v2 Vectors",
            "NVD CVSS v3 Severity",
            "NVD CVSS v3 Score",
            "NVD CVSS v3 Vectors",
            "NVD URL",
            "Fix Version",
            "Solution",
            "Qualys IDs",
            "Description",
            "Applied By",
            "Applied On",
            "Reverted By",
            "Reverted On",
            "Enforced By",
            "Enforced On",
            "vShield Status",
            "Suppression Date",
            "Base Image Vulnerability",
            "Base Image Name",
            "Aqua score",
            "Aqua severity",
            "Aqua Vectors",
            "Aqua custom severity",
            "Aqua custom notes",
            self.ffi,
            "Last Image Scan",
            "Exploit Availability",
            "Temporal Vector",
            "Exploit Type",
            "Namespace",
            "Resource Path",
        ]

        file_path = kwargs.get("file_path")
        parent_id = kwargs.get("parent_id")
        parent_module = kwargs.get("parent_module")
        logger = create_logger()
        super().__init__(
            logger=logger,
            app=app,
            file_path=Path(file_path),
            name=self.name,
            headers=self.headers,
            parent_id=parent_id,
            parent_module=parent_module,
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            issue_func=self.create_issue,
        )
        self.create_software_inventory()

    def create_issue(self, dat: dict = None) -> Optional[Issue]:
        """
        Create an issue from a row in the Snyk file

        :param dict dat: Data row from CSV file
        :return: RegScale Issue object or None
        :rtype: Optional[Issue]
        """

        severity = self.determine_cvss_severity(dat)
        if severity == "info":
            return None
        kev_due_date = None
        if self.attributes.app.config["issues"][self.name.lower()]["useKev"]:
            kev_due_date = self.lookup_kev(dat["CVE"][0] if dat.get("CVE") else None)
        iss = Issue(
            isPoam=severity in ["low", "medium", "high", "critical"],
            title=dat[self.vuln_title],
            description=dat["Description"],
            status="Open",
            severityLevel=Issue.assign_severity(severity),
            issueOwnerId=self.attributes.app.config["userId"],
            assetIdentifier=dat[self.image_name],
            securityPlanId=(
                self.attributes.parent_id
                if self.attributes.parent_module == "securityplans"
                else None
            ),
            recommendedActions=dat["Solution"],
            cve=dat[self.vuln_title],
            autoApproved="No",
            parentId=self.attributes.parent_id,
            parentModule=self.attributes.parent_module,
            # Set issue due date to the kev date if it is in the kev list
        )
        iss.originalRiskRating = iss.assign_risk_rating(severity)
        # Date not provided, we must use the creation date of the file
        iss.dateFirstDetected = datetime.strptime(dat[self.ffi], self.fmt).strftime(
            self.dt_format
        )

        iss.basisForAdjustment = f"{self.name} import"
        iss = self.update_due_dt(
            iss=iss, kev_due_date=kev_due_date, scanner="snyk", severity=severity
        )

        return iss

    def create_asset(self, dat: Optional[dict] = None) -> Asset:
        """
        Create an asset from a row in the Snyk file

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :return: RegScale Asset object
        :rtype: Asset
        """
        name = dat[self.image_name]
        return Asset(
            **{
                "id": 0,
                "name": name,
                "description": "",
                "operatingSystem": Asset.find_os(dat["OS"]),
                "operatingSystemVersion": dat["OS"],
                "ipAddress": "0.0.0.0",
                "isPublic": True,
                "status": "Active (On Network)",
                "assetCategory": "Hardware",
                "bLatestScan": True,
                "bAuthenticatedScan": True,
                "scanningTool": self.name,
                "assetOwnerId": self.config["userId"],
                "assetType": "Other",
                "fqdn": name if is_valid_fqdn(name) else None,
                "systemAdministratorId": self.config["userId"],
                "parentId": self.attributes.parent_id,
                "parentModule": self.attributes.parent_module,
            }
        )

    def create_software_inventory(self) -> List[SoftwareInventory]:
        """
        Create and post a list of software inventory for a given asset

        :return: List of software inventory
        :rtype: List[SoftwareInventory]
        """
        scanned_assets = [
            asset
            for asset in self.data["assets"]
            if asset.id in {vuln.parentId for vuln in self.data["vulns"]}
        ]
        self.attributes.logger.info(
            f"Processing inventory for {len(scanned_assets)} scanned assets."
        )
        software_inventory = []
        for asset in scanned_assets:
            software_inventory.extend(
                SoftwareInventory.fetch_by_asset(self.attributes.app, asset.id)
            )
        hardware = sorted(
            [asset for asset in scanned_assets if asset.assetCategory == "Hardware"],
            key=attrgetter("name"),
        )
        grouping = {
            key: list(group) for key, group in groupby(hardware, key=attrgetter("name"))
        }

        def process_group(key, group):
            """
            Process a group of assets and create a software inventory for each asset

            :param key: Key for the group
            :param group: Group of assets
            :return: None
            """
            # Do something
            group_rows = [row for row in self.file_data if row[self.image_name] == key]
            for software in group_rows:
                inv = SoftwareInventory(
                    name=software["Resource"],
                    version=software["Installed Version"],
                    createdById=self.config["userId"],
                    dateCreated=get_current_datetime(),
                    lastUpdatedById=self.config["userId"],
                    isPublic=True,
                )
                inv.parentHardwareAssetId = group[0].id
                if inv not in software_inventory:
                    software_inventory.append(
                        SoftwareInventory.insert(self.attributes.app, inv)
                    )

        with ThreadPoolExecutor() as executor:
            for key, group in grouping.items():
                executor.submit(process_group, key, group)

        return software_inventory

    def create_vuln(self, dat: Optional[dict] = None) -> Optional[Vulnerability]:
        """
        Create a vulnerability from a row in the Snyk csv file

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :return: RegScale Vulnerability object or None
        :rtype: Optional[Vulnerability]
        """
        regscale_vuln = None
        severity = self.determine_cvss_severity(dat)
        hostname = dat[self.image_name]
        description = dat["Description"]
        solution = (
            dat["Solution"] if dat.get("Solution") else "Upgrade affected package"
        )
        config = self.attributes.app.config
        asset_match = [asset for asset in self.data["assets"] if asset.name == hostname]
        asset = asset_match[0] if asset_match else None
        if asset_match:
            regscale_vuln = Vulnerability(
                id=0,
                scanId=0,
                parentId=asset.id,
                parentModule="assets",
                ipAddress="0.0.0.0",
                lastSeen=datetime.strptime(dat["Last Image Scan"], self.fmt).strftime(
                    self.dt_format
                ),
                firstSeen=datetime.strptime(dat[self.ffi], self.fmt).strftime(
                    self.dt_format
                ),
                daysOpen=None,
                dns=hostname,
                mitigated=None,
                operatingSystem=asset.operatingSystem,
                severity=severity,
                plugInName=description,
                cve=dat[self.vuln_title],
                cvsSv3BaseScore=dat["Vendor CVSS v3 Score"],
                tenantsId=0,
                title=f"{description} on asset {asset.name}",
                description=description,
                plugInText=dat[self.vuln_title],
                createdById=config["userId"],
                lastUpdatedById=config["userId"],
                dateCreated=get_current_datetime(),
                extra_data={"solution": solution},
            )
        return regscale_vuln

    def determine_cvss_severity(self, dat: dict) -> str:
        """
        Determine the CVSS severity of the vulnerability

        :param dict dat: Data row from CSV file
        :return: A severity derived from the CVSS scores
        :rtype: str
        """
        precedence_order = [
            "NVD CVSS v3 Severity",
            "NVD CVSS v2 Severity",
            "Vendor CVSS v3 Severity",
            "Vendor CVSS v2 Severity",
        ]
        severity = "info"
        for key in precedence_order:
            if dat.get(key):
                severity = dat[key].lower()
                break
        # remap crits to highs
        if severity == "critical":
            severity = "high"
        return severity
