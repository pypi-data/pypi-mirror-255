#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Model for a RegScale Issue """
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union
from urllib.parse import urljoin

from requests import JSONDecodeError
from rich.progress import Progress

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import check_file_path, save_data_to
from regscale.models.regscale_models import File
from regscale.models.regscale_models.regscale_model import RegScaleModel

ISSUE_FIELDS = """
items {
    id
    title
    dateCreated
    description
    severityLevel
    issueOwnerId
    costEstimate
    levelOfEffort
    dueDate
    identification
    securityChecks
    recommendedActions
    sourceReport
    status
    capStatus
    dateCompleted
    facilityId
    orgId
    controlId
    assessmentId
    requirementId
    securityPlanId
    projectId
    supplyChainId
    policyId
    componentId
    burpId
    incidentId
    jiraId
    serviceNowId
    wizId
    prismaId
    tenableId
    tenableNessusId
    qualysId
    defenderId
    defenderCloudId
    salesforceId
    pluginId
    assetIdentifier
    falsePositive
    operationalRequirement
    autoApproved
    dateFirstDetected
    changes
    vendorDependency
    vendorName
    vendorLastUpdate
    vendorActions
    deviationRationale
    parentId
    parentModule
    createdById
    lastUpdatedById
    dateLastUpdated
    isPublic
    isPoam
    dependabotId
    originalRiskRating
    adjustedRiskRating
    bRiskAdjustment
},
"""


class IssueSeverity(str, Enum):
    """Issue Severity"""

    NotAssigned = "IV - Not Assigned"
    Low = "III - Low - Other Weakness"
    Moderate = "II - Moderate - Reportable Condition"
    High = "I - High - Significant Deficiency"


class IssueStatus(str, Enum):
    """Issue Status"""

    Draft = "Draft"
    PendingScreening = "Pending Screening"
    Open = "Open"
    PendingVerification = "Pending Verification"
    Closed = "Closed"
    Cancelled = "Cancelled"
    PendingDecommission = "Pending Decommission"
    SupplyChainProcurementDependency = "Supply Chain/Procurement Dependency"
    VendorDependency = "Vendor Dependency for Fix"
    Delayed = "Delayed"
    ExceptionWaiver = "Exception/Waiver"
    PendingApproval = "Pending Approval"


class Issue(RegScaleModel):
    """Issue Model"""

    _module_slug = "issues"

    title: Optional[str] = ""
    severityLevel: Union[IssueSeverity, str] = IssueSeverity.NotAssigned
    issueOwnerId: Optional[str] = ""
    dueDate: Optional[str] = ""
    id: int = 0
    uuid: Optional[str] = None
    dateCreated: Optional[str] = None
    description: Optional[str] = None
    issueOwner: Optional[str] = None
    costEstimate: Optional[int] = None
    levelOfEffort: Optional[int] = None
    identification: Optional[str] = (
        ""  # Has to be an empty string or else it will fail to create
    )
    capStatus: Optional[str] = None
    sourceReport: Optional[str] = None
    status: Optional[Union[IssueStatus, str]] = None
    dateCompleted: Optional[str] = None
    activitiesObserved: Optional[str] = None
    failuresObserved: Optional[str] = None
    requirementsViolated: Optional[str] = None
    safetyImpact: Optional[str] = None
    securityImpact: Optional[str] = None
    qualityImpact: Optional[str] = None
    facility: Optional[str] = None
    facilityId: Optional[int] = None
    org: Optional[str] = None
    orgId: Optional[int] = None
    controlId: Optional[int] = None
    assessmentId: Optional[int] = None
    requirementId: Optional[int] = None
    securityPlanId: Optional[int] = None
    projectId: Optional[int] = None
    supplyChainId: Optional[int] = None
    policyId: Optional[int] = None
    componentId: Optional[int] = None
    incidentId: Optional[int] = None
    jiraId: Optional[str] = None
    serviceNowId: Optional[str] = None
    wizId: Optional[str] = None
    burpId: Optional[str] = None
    defenderId: Optional[str] = None
    defenderAlertId: Optional[str] = None
    defenderCloudId: Optional[str] = None
    salesforceId: Optional[str] = None
    prismaId: Optional[str] = None
    tenableId: Optional[str] = None
    tenableNessusId: Optional[str] = None
    qualysId: Optional[str] = None
    pluginId: Optional[str] = None
    cve: Optional[str] = None
    assetIdentifier: Optional[str] = None
    falsePositive: Optional[str] = None
    operationalRequirement: Optional[str] = None
    autoApproved: Optional[str] = None
    kevList: Optional[str] = None
    dateFirstDetected: Optional[str] = None
    changes: Optional[str] = None
    vendorDependency: Optional[str] = None
    vendorName: Optional[str] = None
    vendorLastUpdate: Optional[str] = None
    vendorActions: Optional[str] = None
    deviationRationale: Optional[str] = None
    parentId: Optional[int] = None
    parentModule: Optional[str] = None
    createdBy: Optional[str] = None
    createdById: Optional[str] = None
    lastUpdatedBy: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    dateLastUpdated: Optional[str] = None
    securityChecks: Optional[str] = None
    recommendedActions: Optional[str] = None
    isPublic: Optional[bool] = True
    dependabotId: Optional[str] = None
    isPoam: Optional[bool] = False
    originalRiskRating: Optional[str] = None
    adjustedRiskRating: Optional[str] = None
    bRiskAdjustment: Optional[bool] = False
    basisForAdjustment: Optional[str] = None

    def __hash__(self) -> int:
        """
        Enable object to be hashable

        :return: Hashed TenableAsset
        :rtype: int
        """
        return hash(
            (
                self.title,
                self.parentId,
                self.parentModule,
                self.description,
            )
        )

    def __eq__(self, other) -> bool:
        """
        Return True if the two objects are equal

        :param other: Object to compare to
        :return: Updated Issue
        :rtype: bool
        """
        return (
            self.title == other.title
            and self.parentId == other.parentId
            and self.parentModule == other.parentModule
            and self.description == other.description
        )

    @classmethod
    def assign_risk_rating(cls, value: Any) -> Optional[str]:
        """
        Function to assign risk rating for an issue in RegScale using the provided value

        :param Any value: The value to analyze to determine the issue's risk rating
        :return: String of risk rating for RegScale issue, or "" if not found
        :rtype: str
        """
        if isinstance(value, str):
            if value.lower() == "low":
                return "Low"
            if value.lower() in ["medium", "moderate"]:
                return "Moderate"
            if value.lower() in ["high", "critical"]:
                return "High"
        return ""

    @staticmethod
    def assign_severity(value: Optional[Any] = None) -> str:
        """
        Function to assign severity for an issue in RegScale using the provided value

        :param Optional[Any] value: The value to analyze to determine the issue's severity, defaults to None
        :return: String of severity level for RegScale issue
        :rtype: str
        """
        severity_levels = {
            "low": "III - Low - Other Weakness",
            "moderate": "II - Moderate - Reportable Condition",
            "high": "I - High - Significant Deficiency",
        }
        severity = "IV - Not Assigned"
        # see if the value is an int or float
        if isinstance(value, (int, float)):
            # check severity score and assign it to the appropriate RegScale severity
            if value >= 7:
                severity = severity_levels["high"]
            elif 4 <= value < 7:
                severity = severity_levels["moderate"]
            else:
                severity = severity_levels["low"]
        elif isinstance(value, str):
            if value.lower() in ["low", "lowest"]:
                severity = severity_levels["low"]
            elif value.lower() in ["medium", "moderate"]:
                severity = severity_levels["moderate"]
            elif value.lower() in ["high", "critical", "highest"]:
                severity = severity_levels["high"]
            elif value in list(severity_levels.values()):
                severity = value
        return severity

    @staticmethod
    def update_issue(app: Application, issue: "Issue") -> Optional["Issue"]:
        """
        Update an issue in RegScale

        :param Application app: Application Instance
        :param Issue issue: Issue to update in RegScale
        :return: Updated issue in RegScale
        :rtype: Issue
        """
        if isinstance(issue, dict):
            issue = Issue(**issue)
        api = Api()
        issue_id = issue.id

        response = api.put(
            app.config["domain"] + f"/api/issues/{issue_id}", json=issue.dict()
        )
        if response.status_code == 200:
            try:
                issue = Issue(**response.json())
            except JSONDecodeError:
                return None
        return issue

    @staticmethod
    def insert_issue(app: Application, issue: "Issue") -> Optional["Issue"]:
        """
        Update an issue in RegScale

        :param Application app: Application Instance
        :param Issue issue: Issue to insert to RegScale
        :return: Newly created issue in RegScale
        :rtype: Issue
        """
        if isinstance(issue, dict):
            issue = Issue(**issue)
        api = Api()
        logger = create_logger()
        response = api.post(app.config["domain"] + "/api/issues", json=issue.dict())
        if response.status_code == 200:
            try:
                issue = Issue(**response.json())
            except JSONDecodeError as jex:
                logger.error("Unable to read issue:\n%s", jex)
                return None
        else:
            logger.warning("Unable to insert issue: %s", issue.title)
        return issue

    @staticmethod
    def bulk_insert(
        app: Application,
        issues: List["Issue"],
        max_workers: Optional[int] = 10,
        batch_size: int = 100,
        batch: bool = False,
    ) -> List["Issue"]:
        """
        Bulk insert assets using the RegScale API and ThreadPoolExecutor

        :param Application app: Application Instance
        :param List["Issue"] issues: List of issues to insert
        :param Optional[int] max_workers: Max Workers, defaults to 10
        :param int batch_size: Number of issues to insert per batch, defaults to 100
        :param bool batch: Insert issues in batches, defaults to False
        :return: List of Issues from RegScale
        :rtype: List[Issue]
        """
        api = Api()
        url = urljoin(app.config["domain"], "/api/issues/batchcreate")
        results = []
        with Progress(transient=False) as progress:
            task = progress.add_task(
                f"Inserting {len(issues)} new issues", total=len(issues)
            )
            if batch:
                # Chunk list into batches
                batches = [
                    issues[i : i + batch_size]
                    for i in range(0, len(issues), batch_size)
                ]
                for my_batch in batches:
                    res = api.post(url=url, json=[iss.dict() for iss in my_batch])
                    if not res.ok:
                        app.logger.error(
                            "%i: %s\nError inserting batch of issues: %s",
                            res.status_code,
                            res.text,
                            my_batch,
                        )
                    results.append(res)
                    progress.update(task, advance=len(my_batch))
            else:
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = [
                        executor.submit(
                            Issue.insert_issue,
                            app,
                            issue,
                        )
                        for issue in issues
                    ]
                    for future in as_completed(futures):
                        issue = future.result()
                        results.append(issue)
                        progress.update(task, advance=1)
        return results

    @staticmethod
    def bulk_update(
        app: Application,
        issues: List["Issue"],
        max_workers: int = 10,
        batch_size: int = 100,
        batch: bool = False,
    ) -> List["Issue"]:
        """Bulk insert assets using the RegScale API and ThreadPoolExecutor

        :param Application app: Application Instance
        :param List["Issue"] issues: List of issues to update
        :param Optional[int] max_workers: Max Workers, defaults to 10
        :param Optional[int] batch_size: Number of issues to update per batch, defaults to 100
        :param Optional[bool] batch: Insert issues in batches, defaults to False
        :return: List of Issues from RegScale
        :rtype: List[Issue]
        """
        api = Api()
        url = urljoin(app.config["domain"], "/api/issues/batchupdate")
        results = []
        with Progress(transient=False) as progress:
            task = progress.add_task(
                f"Updating {len(issues)} new issues", total=len(issues)
            )
            if batch:
                # Chunk list into batches
                batches = [
                    issues[i : i + batch_size]
                    for i in range(0, len(issues), batch_size)
                ]
                for my_batch in batches:
                    res = api.put(url=url, json=[iss.dict() for iss in my_batch])
                    if not res.ok:
                        app.logger.error(
                            "%i: %s\nError inserting batch of issues: %s",
                            res.status_code,
                            res.text,
                            my_batch,
                        )
                    results.append(res)
                    progress.update(task, advance=len(my_batch))
            else:
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = [
                        executor.submit(
                            Issue.update_issue,
                            app,
                            issue,
                        )
                        for issue in issues
                    ]
                    for future in as_completed(futures):
                        issue = future.result()
                        results.append(issue)
                        progress.update(task, advance=1)

        return results

    @staticmethod
    def fetch_issues_by_parent(
        app: Application,
        regscale_id: int,
        regscale_module: str,
    ) -> List["Issue"]:
        """
        Find all issues by parent id and parent module

        :param Application app: Application Instance
        :param int regscale_id: Parent ID
        :param str regscale_module: Parent Module
        :return: List of issues from RegScale
        :rtype: List[issues]
        """
        api = Api()
        body = f"""
                query {{
                    issues(take: 50, skip: 0, where: {{ parentModule: {{eq: "{regscale_module}"}} parentId: {{
                      eq: {regscale_id}
                    }}}}) {{
                    {ISSUE_FIELDS}
                    pageInfo {{
                        hasNextPage
                    }}
                    ,totalCount}}
                }}
                """
        try:
            existing_issues = api.graph(query=body)["issues"]["items"]
        except (JSONDecodeError, TypeError, KeyError):
            existing_issues = []
        return [Issue(**issue) for issue in existing_issues]

    @staticmethod
    def fetch_issues_by_ssp(
        app: Application,
        ssp_id: int,
    ) -> List["Issue"]:
        """
        Find all issues by parent id and parent module

        :param Application app: Application Instance
        :param int ssp_id: RegScale SSP Id
        :return: List of Issues from RegScale SSP
        :rtype: List[Issue]
        """
        api = Api()
        body = f"""
                query {{
                    issues(take: 50, skip: 0, where: {{ securityPlanId: {{eq: {ssp_id}}}}}) {{
                    {ISSUE_FIELDS}
                    pageInfo {{
                        hasNextPage
                    }}
                    ,totalCount}}
                }}
                """
        try:
            existing_issues = api.graph(query=body)["issues"]["items"]
        except (JSONDecodeError, TypeError, KeyError):
            existing_issues = []
        return [Issue(**issue) for issue in existing_issues]

    @staticmethod
    def fetch_all_issues(
        app: Application,
    ) -> List["Issue"]:
        """
        Find all issues by parent id and parent module

        :param Application app: Application Instance
        :return: List of Issues from RegScale SSP
        :rtype: List[Issue]
        """
        api = Api()
        body = f"""
                    query {{
                        issues(take: 50, skip: 0) {{
                        {ISSUE_FIELDS}
                        pageInfo {{
                            hasNextPage
                        }}
                        ,totalCount}}
                    }}
                    """
        try:
            logger = create_logger()
            logger.info("Retrieving all issues from RegScale...")
            existing_issues = api.graph(query=body)["issues"]["items"]
            logger.info("Retrieved %i issue(s) from RegScale.", len(existing_issues))
        except JSONDecodeError:
            existing_issues = []
        return [Issue(**issue) for issue in existing_issues]

    @staticmethod
    def fetch_issue_by_id(
        app: Application,
        issue_id: int,
    ) -> Optional["Issue"]:
        """
        Find a RegScale issue by its id

        :param Application app: Application Instance
        :param int issue_id: RegScale Issue Id
        :return: Issue from RegScale or None if it doesn't exist
        :rtype: Optional[Issue]
        """
        api = Api()
        issue_response = api.get(url=f"{app.config['domain']}/api/issues/{issue_id}")
        issue = None
        try:
            issue = Issue(**issue_response.json())
        except JSONDecodeError:
            logger = create_logger()
            logger.warning("Unable to find issue with id %i", issue_id)
        return issue

    @staticmethod
    def fetch_issues_and_attachments_by_parent(
        app: Application,
        parent_id: int,
        parent_module: str,
        fetch_attachments: Optional[bool] = True,
        save_issues: Optional[bool] = True,
    ) -> Tuple[list["Issue"], Optional[list[File]]]:
        """
        Fetch all issues from RegScale for the provided parent record

        :param Application app: Application object
        :param int parent_id: Parent record ID in RegScale
        :param str parent_module: Parent record module in RegScale
        :param Optional[bool] fetch_attachments: Whether to fetch attachments from RegScale, defaults to True
        :param Optional[bool] save_issues: Save RegScale issues to a .json in artifacts, defaults to True
        :return: List of RegScale issues, dictionary of issue's attachments as File objects
        :rtype: Tuple[list[Issue], Optional[list[File]]]
        """
        attachments: Optional[dict] = None
        logger = create_logger()
        # get the existing issues for the parent record that are already in RegScale
        logger.info(
            "Fetching full issue list from RegScale %s #%i.", parent_module, parent_id
        )
        issues_data = Issue().fetch_issues_by_parent(
            app=app,
            regscale_id=parent_id,
            regscale_module=parent_module,
        )

        # check for null/not found response
        if len(issues_data) == 0:
            logger.warning(
                "No existing issues for this RegScale record #%i in %s.",
                parent_id,
                parent_module,
            )
        else:
            if fetch_attachments:
                # get the attachments for the issue
                api = Api()
                attachments = {
                    issue.id: files
                    for issue in issues_data
                    if (
                        files := File.get_files_for_parent_from_regscale(
                            api, issue.id, "issues"
                        )
                    )
                }
            logger.info(
                "Found %i issue(s) from RegScale %s #%i for processing.",
                len(issues_data),
                parent_module,
                parent_id,
            )
            if save_issues:
                # write issue data to a json file
                check_file_path("artifacts")
                save_data_to(
                    file=Path("./artifacts/existingRegScaleIssues.json"),
                    data=[issue.dict() for issue in issues_data],
                    output_log=False,
                )
                logger.info(
                    "Saved RegScale issue(s) for %s #%i, see /artifacts/"
                    + "existingRegScaleIssues.json",
                    parent_module,
                    parent_id,
                )
        return issues_data, attachments
