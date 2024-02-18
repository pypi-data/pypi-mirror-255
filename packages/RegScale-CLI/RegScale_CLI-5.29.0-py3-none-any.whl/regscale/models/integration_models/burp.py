#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Pydantic model for a Burp Scan """
import os
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, List, Optional, Tuple
from xml.etree.ElementTree import Element, ParseError, fromstring, parse

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import check_file_path, get_current_datetime
from regscale.core.app.utils.regscale_utils import create_new_data_submodule
from regscale.models.integration_models.burp_models import (
    BurpRequest,
    BurpResponse,
    Issue,
    RequestResponse,
)
from regscale.models.regscale_models.asset import Asset
from regscale.models.regscale_models import File
from regscale.models.regscale_models.issue import Issue as RegscaleIssue
from regscale.models.regscale_models.link import Link
from regscale.models.regscale_models.scan import Scan
from regscale.models.regscale_models.vulnerability import Vulnerability

# standard python imports


class Burp:
    """Burp Scan information"""

    def __init__(
        self, app: Application, file_path: str, encoding="utf-8", **kwargs
    ) -> "Burp":
        """
        Initialize Burp Scan
        """
        logger = create_logger("Burp")
        logger.info("Now processing %s", file_path)
        self.logger = logger
        self.app = app
        self.api = Api()
        self.parent_id = 0
        self.parent_module = "assets"
        if "parentId" in kwargs and kwargs["parentId"]:
            self.parent_id = kwargs["parentId"]
        if "parentModule" in kwargs and kwargs["parentModule"]:
            self.parent_module = kwargs["parentModule"]
        self.encoding = encoding
        self.file_path = Path(file_path)
        self.version = None
        self.export_time = None
        self.burp_issues = []
        self.regscale_issues = set()
        self.assets = []
        self.vulnerabilities = set()
        self.existing_issues = []
        self.existing_assets = []
        self.existing_vulnerabilities = []
        self.links = set()
        self.from_file()
        self.scan = {}
        self.move_files()

    def move_files(self) -> None:
        """
        Move files to processed directory

        :return: None
        """
        api = Api()
        # Create processed directory if it doesn't exist, and copy file to it.
        new_file_path = ""
        processed_dir = self.file_path.parent / "processed"
        check_file_path(str(processed_dir.absolute()))
        try:
            if self.parent_id:
                file_name = f"{self.file_path.stem}_{get_current_datetime('%Y_%m_%d-%I_%M_%S_%p')}".replace(
                    " ", "_"
                )
                # Rename to friendly file name and post to Regscale
                new_file_path = self.file_path.rename(
                    self.file_path.parent / (file_name + ".xml")
                )
                self.logger.info(
                    "Renaming %s to %s, and posting to RegScale...",
                    self.file_path.name,
                    new_file_path.name,
                )
                File.upload_file_to_regscale(
                    file_name=str(new_file_path.absolute()),
                    parent_id=self.parent_id,
                    parent_module="securityplans",
                    api=api,
                )
                shutil.move(new_file_path, processed_dir)
        except shutil.Error:
            self.logger.debug(
                "File %s already exists in %s",
                new_file_path.name,
                processed_dir,
            )

    def from_file(self) -> None:
        """
        Read Burp Scan file

        :return: None
        """
        self.logger.debug(os.getcwd())
        try:
            with open(file=self.file_path, mode="r", encoding=self.encoding) as file:
                root = self.file_root_element(file)
                self.version = root.attrib["burpVersion"]
                self.export_time = root.attrib["exportTime"]
                self.gen_issues(root)
                self.gen_assets()
                self.post_issues()
                self.gen_scans()
                self.gen_vulnerabilities()
                self.gen_links()
        except (FileNotFoundError, ParseError):
            self.logger.error("File not found: %s", self.file_path)

    @staticmethod
    def file_root_element(file) -> Element:
        """
        Function returns the root element for tree of given file with scan results

        :return: root element for this tree
        :rtype: Element
        """

        scan_file_parsed = parse(file)
        root = scan_file_parsed.getroot()
        return root

    def create_issue(self, xml) -> Issue:
        """
        Create an issue from the XML

        :param xml: XML
        :return: Issue object from XML
        :rtype: Issue
        """
        issue = Issue()
        issue.serialNumber = self.get(xml, "serialNumber")
        issue.type = self.get(xml, "type")
        issue.host = self.get(xml, "host")
        issue.path = self.get(xml, "path")
        issue.name = self.get(xml, "name")
        issue.location = self.get(xml, "location")
        issue.severity = self.get(xml, "severity")
        issue.confidence = self.get(xml, "confidence")
        issue.background = self.get(xml, "issueBackground")
        issue.detail = self.get(xml, "issueDetail")
        issue.remediation_background = self.get(xml, "remediationBackground")
        issue.remediation_detail = self.get(xml, "remediationDetail")
        issue.links = self.extract_links(self.get(xml, "vulnerabilityClassifications"))
        issue.cwes = self.extract_classifications(
            self.get(xml, "vulnerabilityClassifications")
        )
        issue.request_response = self.get_io(xml)
        return issue

    def create_regscale_issue(
        self, issue: Issue, scan_time: datetime, fmt: str
    ) -> Optional[RegscaleIssue]:
        """
        Create a RegScale Issue from a Burp Issue

        :param Issue issue: Burp Issue
        :param datetime scan_time: Scan time
        :param str fmt: Format for datetime object
        :return: RegScale Issue
        :rtype: Optional[RegscaleIssue]
        """

        if issue.severity.lower() == "info":
            return None
        due_date = self.get_due_delta(issue.severity)
        try:
            response_data = issue.request_response.response.convert_to_json()
        except AttributeError:
            response_data = None
        regscale_issue = RegscaleIssue(
            isPoam=True,
            title=issue.name,
            description=(
                issue.background if issue.background else ""
            ),  # issueBackground only
            status="Open",
            severityLevel=RegscaleIssue.assign_severity(issue.severity),
            issueOwnerId=self.app.config["userId"],
            assetIdentifier=issue.host,
            securityPlanId=self.parent_id,
            recommendedActions=(
                issue.detail + "<br>" + issue.remediation_background
                if issue.detail
                else issue.remediation_background
            ),
            autoApproved="No",
            parentId=self.parent_id,
            parentModule=self.parent_module,
            cveList="",
            cve="",
            sourceReport="Burp Suite",
            pluginId=issue.serialNumber,
            # Set issue due date to the kev date if it is in the kev list
        )
        if issue.detail:
            regscale_issue.description = (
                regscale_issue.description + "<br>" + issue.detail
            )
        if issue.cwes:
            regscale_issue.description = (
                regscale_issue.description + "<br>" + ", ".join(issue.cwes)
            )
        regscale_issue.originalRiskRating = regscale_issue.assign_risk_rating(
            issue.severity
        )
        regscale_issue.dateFirstDetected = datetime.strftime(scan_time, fmt)
        if scan_time + timedelta(days=due_date) < datetime.now():
            regscale_issue.dueDate = datetime.strftime(
                datetime.now() + timedelta(days=due_date), fmt
            )
        else:
            regscale_issue.dueDate = datetime.strftime(
                scan_time + timedelta(days=due_date), fmt
            )
        regscale_issue.identification = "Vulnerability Assessment"
        regscale_issue.sourceReport = self.file_path.name
        regscale_issue.basisForAdjustment = "Burp Scan import"
        regscale_issue.extra_data = {
            "host": issue.host,
            "links": [self.cwe_to_mitre_link(link) for link in issue.cwes],
        }
        if response_data:
            regscale_issue.extra_data["response"] = response_data
            regscale_issue.extra_data["response"]["source"] = str(
                self.file_path.absolute()
            )

        return regscale_issue

    def gen_issues(self, root) -> None:
        """
        Generate issues

        :param root: Root
        :return: None
        """
        issues = []
        self.existing_issues = RegscaleIssue.fetch_issues_by_ssp(
            self.app, self.parent_id
        )
        root_issues = root.findall("issue")
        fmt = "%Y-%m-%d %H:%M:%S"
        scan_time = datetime.strptime(
            root.attrib["exportTime"], "%a %b %d %H:%M:%S %Z %Y"
        )
        for xml in root_issues:
            issue = self.create_issue(xml)
            issues.append(issue)
            regscale_issue = self.create_regscale_issue(issue, scan_time, fmt)
            if regscale_issue and regscale_issue not in self.existing_issues:
                self.regscale_issues.add(regscale_issue)
        self.burp_issues = issues

    def get_due_delta(self, severity: str) -> int:
        """
        Find the due delta from the config file

        :param str severity: The severity level
        :return: Due date delta
        :rtype: int
        """
        # Leave at Tenable for now
        due_delta = self.app.config["issues"]["tenable"]["low"]
        if severity.lower() in ["medium", "moderate"]:
            due_delta = self.app.config["issues"]["tenable"]["moderate"]
        elif severity.lower() == "high":
            due_delta = self.app.config["issues"]["tenable"]["high"]
        elif severity.lower() == "critical":
            due_delta = self.app.config["issues"]["tenable"]["critical"]
        return due_delta

    @classmethod
    def get(cls, item: Any, key: Any) -> Optional[Any]:
        """
        Get item

        :param Any item: Object to try and get value from
        :param Any key: The key to get the value with
        :return: item stored at the provided key, or None if not found
        :rtype: Optional[Any]
        """
        try:
            return item.find(key).text
        except (AttributeError, KeyError):
            return None

    @staticmethod
    def extract_numbers(string: str) -> List[int]:
        """
        Extract numbers from string

        :param str string: string with numbers
        :return: List of numbers found in provided string
        :rtype: List[int]
        """
        return [int(num) for num in re.findall(r"\b\d+\b", string)]

    def cwe_to_mitre_link(self, cwe_id: str) -> Link:
        """
        Generate a link to the MITRE CWE site for the given CWE

        :param str cwe_id: CWE ID
        :return: Link object
        :rtype: Link
        """
        base_url = "https://cwe.mitre.org/data/definitions/"
        url = base_url + str(self.extract_numbers(cwe_id)[0]) + ".html"
        return Link(
            url=url,
            title=f"MITRE {cwe_id} CWE",
            parentId=self.parent_id,
            parentModule=self.parent_module,
        )

    @staticmethod
    def get_request_response(item) -> RequestResponse:
        """
        Get the Request/Response object

        :param item: item
        :return: The Request/Response object
        :rtype: RequestResponse
        """
        request_data = item.find(".//request")
        response_data = item.find(".//response")
        base64_dat = (
            bool(request_data.attrib["base64"]) if "base64" in item.attrib else False
        )
        response_data_is_base64 = BurpResponse.is_base64(response_data.text)
        method = request_data.attrib["method"] if "method" in item.attrib else "GET"
        request = (
            BurpRequest(dataString=request_data.text, base64=base64_dat, method=method)
            if BurpRequest.is_base64(request_data.text)
            else None
        )
        response = BurpResponse(
            dataString=response_data.text if response_data_is_base64 else None,
            base64=(
                bool(item.find(".//response").attrib["base64"])
                if response_data_is_base64
                else False
            ),
        )
        return RequestResponse(request=request, response=response)

    def get_io(self, xml) -> RequestResponse:
        """
        Generate the Response Request object

        :param xml: xml
        :return: The Request/Response object
        :rtype: RequestResponse
        """
        for item in xml.findall("requestresponse"):
            dat = item.find(".//request")
            if dat.tag == "request":
                return self.get_request_response(item)

    def gen_scans(self) -> None:
        """
        Generate a RegScale Scan

        :return: None
        """

        scans = []
        for asset in self.existing_assets:
            count_low, count_medium, count_high, count_critical = self.gen_counts(asset)
            checks = count_low + count_medium + count_high + count_critical
            fmt = "%a %b %d %H:%M:%S %Z %Y"
            if checks:
                scan = {
                    "id": 0,
                    "scanningTool": "BURP",
                    "scanDate": str(datetime.strptime(self.export_time, fmt)),
                    "scannedIPs": 0,
                    "checks": checks,
                    "vInfo": 0,
                    "vLow": count_low,
                    "vMedium": count_medium,
                    "vHigh": count_high,
                    "vCritical": count_critical,
                    "parentId": asset.id,
                    "parentModule": "assets",
                    "createdById": self.app.config["userId"],
                    "lastUpdatedById": self.app.config["userId"],
                    "isPublic": True,
                    "dateCreated": get_current_datetime(),
                    "dateLastUpdated": get_current_datetime(),
                }
                scans.append(Scan(**scan))
        _ = Scan.bulk_insert(self.app, scans)

    def gen_counts(self, asset: Asset) -> Tuple[int, int, int, int]:
        """
        Generate counts from Burp Scan for a specific asset

        :param Asset asset: RegScale Asset
        :return: Counts for low, medium, high, and critical issues for the given asset
        :rtype: Tuple[int, int, int, int]
        """
        filtered_issues = [
            iss
            for iss in self.burp_issues
            if self.extract_ip_address(iss.host) == self.extract_ip_address(asset.name)
        ]
        count_low = len(
            {
                (iss.name, iss.severity)
                for iss in filtered_issues
                if iss.severity.lower() == "low"
            }
        )
        count_medium = len(
            {
                (iss.name, iss.severity)
                for iss in filtered_issues
                if iss.severity.lower() in ["moderate", "medium"]
            }
        )
        count_high = len(
            {
                (iss.name, iss.severity)
                for iss in filtered_issues
                if iss.severity.lower() == "high"
            }
        )
        count_critical = len(
            {
                (iss.name, iss.severity)
                for iss in filtered_issues
                if iss.severity.lower() == "critical"
            }
        )
        return count_low, count_medium, count_high, count_critical

    def gen_assets(self) -> None:
        """
        Generate RegScale Assets from Burp Issues

        :return: None
        """
        assets = set()
        self.existing_assets = Asset.find_assets_by_parent(
            app=self.app, parent_id=self.parent_id, parent_module=self.parent_module
        )
        for issue in self.burp_issues:
            host_name = None
            hosts = self.extract_ip_address(issue.host)
            host_name = issue.host
            if hosts:
                host_name = hosts[0]
            asset = Asset(
                host_name=host_name,
                name=host_name,
                type="Other",
                ipAddress=host_name if hosts else None,
                parentId=self.parent_id,
                parentModule=self.parent_module,
                assetOwnerId=self.app.config["userId"],
                status="Active (On Network)",
                assetType="Virtual Machine (VM)",
                dateCreated=get_current_datetime(),
                dateLastUpdated=get_current_datetime(),
                createdById=self.app.config["userId"],
                lastUpdatedById=self.app.config["userId"],
                assetCategory="Hardware",
                scanningTool="Burp Scanner",
                isPublic=True,
                tenantsId=0,
            )
            if asset not in self.existing_assets:
                assets.add(asset)
        self.logger.info("Inserting %i assets into RegScale...", len(assets))
        Asset.bulk_insert(self.app, list(assets))
        self.existing_assets = Asset.find_assets_by_parent(
            app=self.app, parent_id=self.parent_id, parent_module=self.parent_module
        )

    @staticmethod
    def extract_ip_address(string: str) -> List[str]:
        """
        Extract IP address from string

        :param str string: string to extract IP address from
        :return: List of IP addresses found in provided string
        :rtype: List[str]
        """
        ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        return re.findall(ip_pattern, string)

    def post_issues(self) -> None:
        """
        Post issues to RegScale

        :return: None
        """
        for index, issue in enumerate(self.regscale_issues):
            issue_ip = None
            # Map issue to asset
            ip_map = self.extract_ip_address(issue.extra_data["host"])
            if ip_map:
                issue_ip = ip_map[0]
            res = [asset for asset in self.existing_assets if issue_ip == asset.name]
            if res:
                issue.assetIdentifier = res[0].name
                self.regscale_issues.remove(issue)
                self.regscale_issues.add(issue)

        new_issues = RegscaleIssue.bulk_insert(self.app, list(self.regscale_issues))
        for issue in new_issues:
            reg_issue = [
                iss for iss in self.regscale_issues if iss.title == issue.title
            ][0]
            if "response" in reg_issue.extra_data:
                try:
                    raw_data = reg_issue.extra_data["response"]
                    create_new_data_submodule(
                        api=self.api,
                        parent_id=issue.id,
                        parent_module="issues",
                        file_path="",
                        raw_data=raw_data,
                        is_file=False,
                    )

                except (IndexError, KeyError):
                    raw_data = None

    def gen_links(self) -> None:
        """
        Post links to RegScale via API

        :return: None
        """
        existing_issues = RegscaleIssue.fetch_issues_by_parent(
            app=self.app, regscale_id=self.parent_id, regscale_module=self.parent_module
        )
        for issue in self.regscale_issues:
            for link in issue.extra_data["links"]:
                if existing_issues:
                    link.parentModule = "issues"
                    link.parentID = [
                        iss for iss in existing_issues if iss.title == issue.title
                    ][0].id
                self.links.add(link)
        Link.bulk_insert(Api(), list(self.links))

    def gen_vulnerabilities(self) -> None:
        """
        Generate RegScale Vulnerabilities from Burp Issues
        and sync to RegScale

        :return: None
        """
        for asset in self.existing_assets:
            scans = Scan.get_existing_scan_history(self.app, asset)
            if scans:
                scan = scans[len(scans) - 1]
                filtered_issues = [
                    iss
                    for iss in self.burp_issues
                    if self.extract_ip_address(iss.host)
                    == self.extract_ip_address(asset.name)
                ]
                for issue in filtered_issues:
                    ip_address = "Unknown"
                    dns_name = "Unknown"
                    if self.extract_ip_address(issue.host):
                        ip_address = self.extract_ip_address(issue.host)[0]
                    else:
                        dns_name = issue.host
                    vuln = Vulnerability(
                        title=issue.name,
                        description=issue.detail,
                        severity=issue.severity,
                        confidence=issue.confidence,
                        remediationBackground=issue.remediation_background,
                        remediationDetail=issue.remediation_detail,
                        parentId=asset.id,
                        parentModule="assets",
                        createdById=self.app.config["userId"],
                        lastUpdatedById=self.app.config["userId"],
                        dateCreated=get_current_datetime(),
                        dateLastUpdated=get_current_datetime(),
                        isPublic=True,
                        tenantsId=0,
                        ipAddress=ip_address,
                        dns=dns_name,
                        scanId=scan["id"],
                        plugInId=issue.type,
                        plugInName=issue.cwes[0] if issue.cwes else "Unknown",
                    )
                    self.vulnerabilities.add(vuln)
        Vulnerability.post_vulnerabilities(self.app, list(self.vulnerabilities))

    @staticmethod
    def extract_links(html: str) -> List[str]:
        """
        Extract links from html with standard library

        :param str html: HTML
        :return: List containing links found in the provided HTML string
        :rtype: List[str]
        """
        root = fromstring(html)
        return [link.attrib["href"] for link in root.iter("a")]

    @staticmethod
    def extract_classifications(html: str) -> list[str]:
        """
        Extract classifications from html with standard library

        :param str html: HTML to parse classifications from
        :return: List containing classifications found in the provided HTML string
        :rtype: List[str]
        """
        root = fromstring(html)
        return [link.text.strip() for link in root.iter("a")]
