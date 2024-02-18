""" Container Scan Abstract """

import ast
import csv
import shutil
from abc import ABC, abstractmethod
from collections import namedtuple
from datetime import datetime, timedelta
from typing import Any, Optional, Sequence

from openpyxl.reader.excel import load_workbook

from regscale.core.app.api import Api
from regscale.core.app.utils.app_utils import (
    check_file_path,
    convert_datetime_to_regscale_string,
    creation_date,
    get_current_datetime,
)
from regscale.integrations.public.cisa import pull_cisa_kev
from regscale.models.regscale_models.asset import Asset
from regscale.models.regscale_models.files import File
from regscale.models.regscale_models.issue import Issue
from regscale.models.regscale_models.scan import Scan
from regscale.models.regscale_models.vulnerability import Vulnerability


class ContainerScan(ABC):
    """
    Abstract class for container scan integration

    :param ABC: Abstract Base Class
    :type ABC: ABC

    """

    def __init__(self, **kwargs):
        """
        Initialize Scan
        """
        _attributes = namedtuple(
            "Attributes",
            [
                "logger",
                "headers",
                "app",
                "file_path",
                "name",
                "parent_id",
                "parent_module",
                "asset_func",
                "vuln_func",
                "issue_func",
            ],
        )
        self.attributes = _attributes(**kwargs)
        self.attributes.logger.info("Processing %s...", self.attributes.file_path.name)
        self.formatted_headers = None
        self.config = self.attributes.app.config
        self.cisa_kev = pull_cisa_kev()
        self.header, self.file_data = self.file_to_list_of_dicts()
        self.data = {
            "assets": [],
            "issues": [],
            "scans": [],
            "vulns": [],
        }
        self.create_epoch = str(int(creation_date(self.attributes.file_path)))
        self.create_assets(
            kwargs["asset_func"]
        )  # Pass in the function to create an asset
        self.create_vulns(kwargs["vuln_func"])  # Pass in the function to create a vuln
        self.create_scan()
        self.create_issues(
            kwargs["issue_func"]
        )  # Pass in the function to create an issue
        self.clean_up()

    def file_to_list_of_dicts(self) -> tuple[Optional[Sequence[str]], list[Any]]:
        """
        Converts a csv file to a list of dictionaries

        :raises AssertionError: If the headers in the csv file do not match the expected headers
        :return: Tuple of header and data from csv file
        :rtype: tuple[Optional[Sequence[str]], list[Any]]
        """
        header = []
        data = []
        with open(self.attributes.file_path, newline="", encoding="utf-8") as file:
            if file.name.endswith(".csv"):
                data, header = self.convert_csv_to_dict(file)
            elif file.name.endswith(".xlsx"):
                header, data = self.convert_xlsx_to_dict(file)
            else:
                raise AssertionError("Unsupported file type")
        return header, data

    def convert_csv_to_dict(self, file) -> tuple:
        """
        Converts a csv file to a list of dictionaries

        :param file: The csv file to convert
        :return: Tuple of header and data from csv file
        :rtype: tuple
        """
        reader = csv.DictReader(file)
        header = reader.fieldnames
        if self.attributes.headers != header:  # Make sure the expected headers match
            raise AssertionError(
                "The headers in the csv file do not match the expected "
                + f"headers, is this a valid {self.attributes.name} csv file?"
            )
        data = list(reader)
        return data, header

    def convert_xlsx_to_dict(self, file) -> tuple:
        """
        Converts a xlsx file to a list of dictionaries

        :param file: The xlsx file to convert
        :return: Tuple of header and data from xlsx file
        :rtype: tuple
        """
        # Load the workbook
        workbook = load_workbook(filename=file.name)

        # Select the first sheet
        sheet = workbook.active

        # Get the data from the sheet
        data = list(sheet.values)

        # Get the header from the first row
        header = list(data[0])

        # Get the rest of the data
        data = data[1:]

        # Convert the data to a dictionary
        data_dict = [dict(zip(header, row)) for row in data]

        # Loop through the data and convert any string lists to lists
        for dat in data_dict:
            for key, val in dat.items():
                if isinstance(val, str) and val.startswith("["):
                    dat[key] = ast.literal_eval(dat[key])
        return header, data_dict

    def count_vuln_by_severity(self, severity: str, asset_id: int) -> int:
        """
        Count the number of vulnerabilities by the provided severity

        :param str severity: The severity to count
        :param int asset_id: The asset id to match the vulnerability's parentId
        :return: The number of vulnerabilities
        :rtype: int
        """
        return len(
            [
                vuln
                for vuln in self.data["vulns"]
                if vuln.parentId == asset_id and vuln.severity == severity
            ]
        )

    def create_scan(self) -> None:
        """
        Create scans in RegScale from Nexpose csv file

        :return: None
        """
        insert_vulns = []
        scanned_assets = [
            asset
            for asset in self.data["assets"]
            if asset.id in {vuln.parentId for vuln in self.data["vulns"]}
        ]

        for asset in scanned_assets:
            count_low = self.count_vuln_by_severity("low", asset.id)
            count_medium = self.count_vuln_by_severity("moderate", asset.id)
            count_high = self.count_vuln_by_severity("high", asset.id)
            count_critical = self.count_vuln_by_severity("critical", asset.id)
            # Create a scan
            scan = Scan(
                **{
                    "id": 0,
                    "scanningTool": self.name,
                    "scanDate": get_current_datetime(),
                    "scannedIPs": len(
                        [
                            ass
                            for ass in scanned_assets
                            if ass.ipAddress == asset.ipAddress
                        ]
                    ),
                    "checks": count_low + count_medium + count_high + count_critical,
                    "vInfo": 0,
                    "vLow": count_low,
                    "vMedium": count_medium,
                    "vHigh": count_high,
                    "vCritical": count_critical,
                    "parentId": asset.id,
                    "parentModule": "assets",
                    "createdById": self.attributes.app.config["userId"],
                    "lastUpdatedById": self.attributes.app.config["userId"],
                    "isPublic": True,
                    "tenantsId": 0,
                    "dateCreated": get_current_datetime(),
                    "dateLastUpdated": get_current_datetime(),
                }
            )

            posted_scan = Scan.post_scan(self.attributes.app, Api(), scan)

            if isinstance(posted_scan, Scan):
                asset_vulns = [
                    vuln for vuln in self.data["vulns"] if vuln.parentId == asset.id
                ]
                # update vuln scan id
                for vuln in asset_vulns:
                    vuln.scanId = posted_scan.id
                    insert_vulns.append(vuln)
        Vulnerability.post_vulnerabilities(
            self.attributes.app, insert_vulns, output_to_console=True
        )

    def create_assets(self, func) -> None:
        """
        Create assets in RegScale from csv file

        :param func: Function to create asset
        :return: None
        """
        existing_assets = Asset.find_assets_by_parent(
            self.attributes.app,
            self.attributes.parent_id,
            self.attributes.parent_module,
        )

        for dat in self.file_data:
            asset = func(dat)
            if asset not in self.data["assets"]:
                self.data["assets"].append(asset)
        insert_assets = [
            asset for asset in self.data["assets"] if asset not in existing_assets
        ]
        self.attributes.logger.info(
            "Inserting %i unique assets into RegScale...", len(insert_assets)
        )
        self.check_status_codes(Asset.bulk_insert(self.attributes.app, insert_assets))

        for asset in self.data["assets"]:
            if asset in existing_assets:
                asset.id = existing_assets[existing_assets.index(asset)].id
        update_assets = [
            asset for asset in self.data["assets"] if asset in existing_assets
        ]
        self.attributes.logger.info(
            "Updating %i unique assets into RegScale...", len(update_assets)
        )
        self.check_status_codes(Asset.bulk_update(self.attributes.app, update_assets))

        # Refresh assets
        self.data["assets"] = Asset.find_assets_by_parent(
            self.attributes.app,
            self.attributes.parent_id,
            self.attributes.parent_module,
        )

    def check_status_codes(self, response_list):
        """
        Check if any of the responses are not 200

        :param response_list: List of responses
        """
        for response in response_list:
            if response.status_code != 200:
                raise AssertionError(
                    f"Unable to {response.request.method} asset to RegScale.\n"
                    f"Code: {response.status_code}\nReason: {response.reason}"
                    f"\nPayload: {response.text}"
                )

    def lookup_kev(self, cve: str) -> str:
        """
        Determine if the cve is part of the published CISA KEV list

        :param str cve: The CVE to lookup.
        :return: A string containing the KEV CVE due date.
        :rtype: str
        """
        kev_data = None
        kev_date = None
        if self.cisa_kev:
            try:
                # Update kev and date
                kev_data = next(
                    dat
                    for dat in self.cisa_kev["vulnerabilities"]
                    if "vulnerabilities" in self.cisa_kev
                    and cve
                    and dat["cveID"].lower() == cve.lower()
                )
            except (StopIteration, ConnectionRefusedError):
                kev_data = None
        if kev_data:
            # Convert YYYY-MM-DD to datetime
            kev_date = convert_datetime_to_regscale_string(
                datetime.strptime(kev_data["dueDate"], "%Y-%m-%d")
            )
        return kev_date

    def update_due_dt(
        self, iss: Issue, kev_due_date: str, scanner: str, severity: str
    ) -> Issue:
        """
        Find the due date for the issue

        :param Issue iss: RegScale Issue object
        :param str kev_due_date: The KEV due date
        :param str scanner: The scanner
        :param str severity: The severity of the issue
        :return: RegScale Issue object
        """
        fmt = "%Y-%m-%d %H:%M:%S"
        if severity == "medium":
            severity = "moderate"
        if kev_due_date and (datetime.strptime(kev_due_date, fmt) > datetime.now()):
            iss.dueDate = kev_due_date
        else:
            iss.dueDate = datetime.strftime(
                datetime.now()
                + timedelta(
                    days=self.attributes.app.config["issues"][scanner][severity]
                ),
                fmt,
            )
        return iss

    def create_issues(self, func) -> None:
        """
        Create an issue in RegScale from csv file

        :param func: Function to create issue
        :return: None
        """
        existing_issues = Issue.fetch_issues_by_parent(
            app=self.attributes.app,
            regscale_id=self.attributes.parent_id,
            regscale_module=self.attributes.parent_module,
        )
        for dat in self.file_data:
            issue = func(dat)
            if issue and issue not in self.data["issues"]:
                self.data["issues"].append(issue)
        insert_issues = [
            issue for issue in self.data["issues"] if issue not in existing_issues
        ]
        self.attributes.logger.info(
            "Creating %i unique issue(s) in RegScale...", len(insert_issues)
        )
        Issue.bulk_insert(self.attributes.app, insert_issues)

        for issue in self.data["issues"]:
            if issue in existing_issues:
                issue.id = existing_issues[existing_issues.index(issue)].id
        update_issues = [
            issue for issue in self.data["issues"] if issue in existing_issues
        ]
        self.attributes.logger.info(
            "Updating %i unique issue(s) in RegScale...", len(update_issues)
        )
        Issue.bulk_update(self.attributes.app, update_issues)

    def create_vulns(self, func) -> None:
        """
        Create vulns in RegScale from csv file

        :param func: Function to create vuln
        :return: None
        """
        # Highs and Criticals are critical
        for dat in self.file_data:
            vuln = func(dat)
            if vuln and vuln not in self.data["vulns"]:
                self.data["vulns"].append(vuln)

    def clean_up(self) -> None:
        """
        Move the Nexpose file to the processed folder

        :return: None
        """
        processed_dir = self.attributes.file_path.parent / "processed"
        check_file_path(str(processed_dir.absolute()))
        api = Api()
        try:
            if self.attributes.parent_id:
                file_name = (
                    f"{self.attributes.file_path.stem}_"
                    + f"{get_current_datetime('%Y%m%d-%I%M%S%p')}"
                ).replace(" ", "_")
                # Rename to friendly file name and post to Regscale
                new_file_path = self.attributes.file_path.rename(
                    self.attributes.file_path.parent / (file_name + ".csv")
                )
                self.attributes.logger.info(
                    "Renaming %s to %s, and uploading it to RegScale...",
                    self.attributes.file_path.name,
                    new_file_path.name,
                )
                File.upload_file_to_regscale(
                    file_name=str(new_file_path.absolute()),
                    parent_id=self.attributes.parent_id,
                    parent_module=self.attributes.parent_module,
                    api=api,
                )
                shutil.move(new_file_path, processed_dir)
        except shutil.Error:
            self.attributes.logger.debug(
                "File %s already exists in %s",
                new_file_path.name,
                processed_dir,
            )

    @abstractmethod
    def create_asset(self):
        """Create an asset"""

    @abstractmethod
    def create_issue(self):
        """Create a scan"""

    @abstractmethod
    def create_vuln(self):
        """Create a Vulnerability"""
