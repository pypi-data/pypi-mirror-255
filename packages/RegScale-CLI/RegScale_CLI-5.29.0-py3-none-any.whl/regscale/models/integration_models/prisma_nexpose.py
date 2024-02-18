"""
Prisma Scan information
"""

from pathlib import Path
from typing import Optional

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import (
    creation_date,
    epoch_to_datetime,
    get_current_datetime,
    is_valid_fqdn,
)
from regscale.models.integration_models.container_scan import ContainerScan
from regscale.models.regscale_models.asset import Asset
from regscale.models.regscale_models.issue import Issue
from regscale.models.regscale_models.scan import Scan
from regscale.models.regscale_models.vulnerability import Vulnerability


class PrismaNexpose(ContainerScan):
    """Prisma/Nexpose Scan information"""

    def __init__(
        self, name: str, app: Application, file_path: str, regscale_ssp_id: int
    ):
        """
        Initialize Scan

        :param str name: Name of the scan
        :param Application app: RegScale Application object
        :param str file_path: Path to the csv files
        :param int regscale_ssp_id: RegScale System Security Plan ID
        """
        self.name = name
        self.vuln_title = "Vulnerability Title"
        self.vuln_id = "Vulnerability ID"
        self.cvss3_score = "CVSSv3 Score"
        self.headers = [
            "IP Address",
            "Hostname",
            "OS",
            self.vuln_title,
            self.vuln_id,
            "CVSSv2 Score",
            self.cvss3_score,
            "Description",
            "Proof",
            "Solution",
            "CVEs",
        ]
        logger = create_logger()
        super().__init__(
            logger=logger,
            app=app,
            file_path=Path(file_path),
            name=self.name,
            headers=self.headers,
            parent_id=regscale_ssp_id,
            parent_module="securityplans",
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            issue_func=self.create_issue,
        )

    def create_issue(self, dat: dict = None) -> Issue:
        """
        Create an issue from a row in the Prisma/Nexpose csv file

        :param dict dat: Data row from CSV file
        :return: RegScale Issue object
        :rtype: Issue
        """

        severity = (
            Vulnerability.determine_cvss3_severity_text(float(dat[self.cvss3_score]))
            if dat[self.cvss3_score]
            else "low"
        )
        kev_due_date = None
        if self.attributes.app.config["issues"][self.name.lower()]["useKev"]:
            kev_due_date = self.lookup_kev(dat["CVEs"])
        iss = Issue(
            isPoam=severity in ["low", "moderate", "high", "critical"],
            title=dat[self.vuln_title],
            description=dat["Description"],
            status="Open",
            severityLevel=Issue.assign_severity(severity),
            issueOwnerId=self.attributes.app.config["userId"],
            pluginId=dat[self.vuln_id],
            assetIdentifier=dat["Hostname"],
            securityPlanId=(
                self.attributes.parent_id
                if self.attributes.parent_module == "securityplans"
                else None
            ),
            recommendedActions=dat["Solution"],
            cve=dat["CVEs"],
            autoApproved="No",
            parentId=self.attributes.parent_id,
            parentModule=self.attributes.parent_module,
            # Set issue due date to the kev date if it is in the kev list
        )
        iss.originalRiskRating = iss.assign_risk_rating(severity)
        # Date not provided, we must use the creation date of the file
        iss.dateFirstDetected = epoch_to_datetime(self.create_epoch)
        iss.basisForAdjustment = f"{self.name} import"
        iss = self.update_due_dt(
            iss=iss, kev_due_date=kev_due_date, scanner="prisma", severity=severity
        )

        return iss

    def create_asset(self, dat: Optional[dict] = None) -> Asset:
        """
        Create an asset from a row in the Nexpose csv file

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :return: RegScale Asset object
        :rtype: Asset
        """
        return Asset(
            **{
                "id": 0,
                "name": dat["Hostname"],
                "ipAddress": dat["Hostname"],
                "isPublic": True,
                "status": "Active (On Network)",
                "assetCategory": "Hardware",
                "bLatestScan": True,
                "bAuthenticatedScan": True,
                "scanningTool": self.name,
                "assetOwnerId": self.config["userId"],
                "assetType": "Other",
                "fqdn": is_valid_fqdn(dat["Hostname"]),
                "operatingSystem": Asset.find_os(dat["OS"]),
                "systemAdministratorId": self.config["userId"],
                "parentId": self.attributes.parent_id,
                "parentModule": self.attributes.parent_module,
            }
        )

    def create_vuln(self, dat: Optional[dict] = None) -> Optional[Vulnerability]:
        """
        Create a vulnerability from a row in the Prisma/Nexpose csv file

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :return: RegScale Vulnerability object or None
        :rtype: Optional[Vulnerability]
        """
        regscale_vuln = None
        severity = (
            Vulnerability.determine_cvss3_severity_text(float(dat[self.cvss3_score]))
            if dat[self.cvss3_score]
            else "low"
        )
        config = self.attributes.app.config
        asset_match = [
            asset for asset in self.data["assets"] if asset.name == dat["Hostname"]
        ]
        asset = asset_match[0] if asset_match else None
        if asset_match:
            regscale_vuln = Vulnerability(
                id=0,
                scanId=0,  # set later
                parentId=asset.id,
                parentModule="assets",
                ipAddress="0.0.0.0",  # No ip address available
                lastSeen=get_current_datetime(),
                firstSeen=epoch_to_datetime(self.create_epoch),
                daysOpen=None,
                dns=dat["Hostname"],
                mitigated=None,
                operatingSystem=(
                    Asset.find_os(dat["OS"]) if Asset.find_os(dat["OS"]) else None
                ),
                severity=severity,
                plugInName=dat[self.vuln_title],
                plugInId=dat[self.vuln_id],
                cve=dat["CVEs"],
                vprScore=None,
                tenantsId=0,
                title=f"{dat['Description']} on asset {asset.name}",
                description=dat["Description"],
                plugInText=dat[self.vuln_title],
                createdById=config["userId"],
                lastUpdatedById=config["userId"],
                dateCreated=get_current_datetime(),
                extra_data={"solution": dat["Solution"], "proof": dat["Proof"]},
            )
        return regscale_vuln
