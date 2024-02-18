"""
Prisma Scan information
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import (
    epoch_to_datetime,
    get_current_datetime,
    is_valid_fqdn,
)
from regscale.models.integration_models.container_scan import ContainerScan
from regscale.models.regscale_models.asset import Asset
from regscale.models.regscale_models.issue import Issue
from regscale.models.regscale_models.vulnerability import Vulnerability


class Snyk(ContainerScan):
    """Snyk Scan information"""

    def __init__(
        self, name: str, app: Application, file_path: str, regscale_ssp_id: int
    ):
        """
        Initialize Scan

        :param str name: Name of the scan
        :param Application app: RegScale Application object
        :param str file_path: Path to the data files
        :param int regscale_ssp_id: RegScale System Security Plan ID
        """
        self.name = name
        self.vuln_title = "PROBLEM_TITLE"
        self.fmt = "%Y-%m-%d"
        self.dt_format = "%Y-%m-%d %H:%M:%S"
        self.headers = [
            "ISSUE_SEVERITY",
            "PRIORITY_SCORE",
            "PROBLEM_TITLE",
            "CVE",
            "CWE",
            "PROJECT_NAME",
            "PROJECT_URL",
            "EXPLOIT_MATURITY",
            "AUTOFIXABLE",
            "FIRST_INTRODUCED",
            "PRODUCT_NAME",
            "ISSUE_URL",
            "ISSUE_STATUS_INDICATOR",
            "ISSUE_TYPE",
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
        Create an issue from a row in the Snyk file

        :param dict dat: Data row from CSV file
        :return: RegScale Issue object
        :rtype: Issue
        """

        severity = dat["ISSUE_SEVERITY"].lower()
        kev_due_date = None
        if self.attributes.app.config["issues"][self.name.lower()]["useKev"]:
            kev_due_date = self.lookup_kev(dat["CVE"][0] if dat.get("CVE") else None)
        iss = Issue(
            isPoam=severity in ["low", "medium", "high", "critical"],
            title=dat[self.vuln_title],
            description=dat["PROBLEM_TITLE"],
            status="Open",
            severityLevel=Issue.assign_severity(severity),
            issueOwnerId=self.attributes.app.config["userId"],
            pluginId=dat["PROBLEM_TITLE"],
            assetIdentifier=self.extract_host(dat["PROJECT_NAME"]),
            securityPlanId=(
                self.attributes.parent_id
                if self.attributes.parent_module == "securityplans"
                else None
            ),
            recommendedActions=dat["AUTOFIXABLE"],
            cve=", ".join(dat["CVE"]) if dat.get("CVE") else "",
            autoApproved="No",
            parentId=self.attributes.parent_id,
            parentModule=self.attributes.parent_module,
            # Set issue due date to the kev date if it is in the kev list
        )
        iss.originalRiskRating = iss.assign_risk_rating(severity)
        # Date not provided, we must use the creation date of the file
        iss.dateFirstDetected = datetime.combine(
            datetime.strptime(epoch_to_datetime(self.create_epoch, self.fmt), self.fmt),
            dat["FIRST_INTRODUCED"],
        ).strftime(self.dt_format)
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
        name = self.extract_host(dat["PROJECT_NAME"])
        return Asset(
            **{
                "id": 0,
                "name": name,
                "ipAddress": "0.0.0.0",
                "isPublic": True,
                "status": "Active (On Network)",
                "assetCategory": "Software",
                "bLatestScan": True,
                "bAuthenticatedScan": True,
                "scanningTool": self.name,
                "assetOwnerId": self.config["userId"],
                "assetType": "Other",
                "fqdn": is_valid_fqdn(name),
                "systemAdministratorId": self.config["userId"],
                "parentId": self.attributes.parent_id,
                "parentModule": self.attributes.parent_module,
            }
        )

    def create_vuln(self, dat: Optional[dict] = None) -> Optional[Vulnerability]:
        """
        Create a vulnerability from a row in the Snyk csv file

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :return: RegScale Vulnerability object or None
        :rtype: Optional[Vulnerability]
        """
        regscale_vuln = None
        severity = dat["ISSUE_SEVERITY"].lower()
        hostname = self.extract_host(dat["PROJECT_NAME"])
        description = dat["PROBLEM_TITLE"]
        solution = dat["AUTOFIXABLE"]
        config = self.attributes.app.config
        asset_match = [asset for asset in self.data["assets"] if asset.name == hostname]
        asset = asset_match[0] if asset_match else None
        if asset_match:
            regscale_vuln = Vulnerability(
                id=0,
                scanId=0,  # set later
                parentId=asset.id,
                parentModule="assets",
                ipAddress="0.0.0.0",  # No ip address available
                lastSeen=get_current_datetime(),
                # ¯\_(ツ)_/
                firstSeen=(
                    datetime.combine(
                        datetime.strptime(
                            epoch_to_datetime(self.create_epoch, self.fmt), self.fmt
                        ),
                        dat["FIRST_INTRODUCED"],
                    )
                ).strftime(self.dt_format),
                daysOpen=None,
                dns=hostname,
                mitigated=None,
                operatingSystem=None,
                severity=severity,
                plugInName=description,
                cve=", ".join(dat["CVE"]) if dat.get("CVE") else "",
                vprScore=None,
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

    def extract_host(self, s: str) -> str:
        """
        Extract the host from the project name

        :param str s: The project name
        :return: The host
        :rtype: str
        """
        try:
            res = (s.split("|"))[1].split("/")[0]
        except IndexError:
            res = s
        return res
