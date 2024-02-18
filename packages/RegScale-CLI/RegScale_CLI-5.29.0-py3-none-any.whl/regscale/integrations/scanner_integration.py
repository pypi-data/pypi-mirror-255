#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Scanner Integration Class """

import dataclasses
import logging
from abc import ABC, abstractmethod
from typing import List, Optional

from regscale.core.app.utils.api_handler import APIHandler
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models import regscale_models

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class IntegrationAsset:
    """
    Dataclass for integration assets
    """

    name: str
    identifier: str
    asset_type: str
    asset_owner_id: str
    parent_id: int
    parent_module: str
    asset_category: str
    date_last_updated: str
    status: str


@dataclasses.dataclass
class IntegrationFinding:
    """
    Dataclass for integration findings

    """

    control_ids: List[int]
    title: str
    category: str
    severity: regscale_models.IssueSeverity
    description: str
    status: regscale_models.ControlTestResultStatus
    priority: str = "Medium"
    issue_type: str = "Risk"
    date_created: str = dataclasses.field(default_factory=get_current_datetime)
    date_last_updated: str = dataclasses.field(default_factory=get_current_datetime)
    external_id: str = ""
    gaps: str = ""
    observations: str = ""
    evidence: str = ""
    identified_risk: str = ""
    impact: str = ""
    recommendation_for_mitigation: str = ""


class ScannerIntegration(ABC):
    """
    Abstract class for scanner integrations

    :param int plan_id: The ID of the security plan
    """

    title = "Scanner Integration"
    asset_identifier_field = ""
    severity_map = {
        0: regscale_models.IssueSeverity.Low,
        1: regscale_models.IssueSeverity.High,
        2: regscale_models.IssueSeverity.High,
        3: regscale_models.IssueSeverity.Moderate,
        4: regscale_models.IssueSeverity.Low,
    }

    def __init__(self, plan_id):
        """
        Initializes the scanner integration

        :param int plan_id: The ID of the security plan
        """
        self.plan_id = plan_id
        self.ci_map = regscale_models.ControlImplementation.get_control_map_by_plan(
            plan_id=plan_id
        )
        self.control_map = {v: k for k, v in self.ci_map.items()}
        self.assessment_map = {}
        self.assessor_id = self.get_assessor_id()
        if not self.asset_identifier_field:
            raise NotImplementedError(
                f"asset_identifier_field must be implemented for {self.__class__.__name__}"
            )

    @staticmethod
    def get_assessor_id() -> Optional[str]:
        """
        Gets the ID of the assessor

        :return: The ID of the assessor
        :rtype: Optional[str]
        """

        api_handler = APIHandler()
        return api_handler.get_user_id()

    @abstractmethod
    def fetch_findings(self) -> List[IntegrationFinding]:
        """
        Fetches findings from the integration

        :return: A list of findings
        :rtype: List[IntegrationFinding]
        """
        pass

    @abstractmethod
    def fetch_assets(self) -> List[IntegrationAsset]:
        """
        Fetches assets from the integration

        :return: A list of assets
        :rtype: List[IntegrationAsset]
        """
        pass

    def get_or_create_assessment(
        self, control_implementation_id: int
    ) -> regscale_models.Assessment:
        """
        Gets or creates a RegScale assessment

        :param int control_implementation_id: The ID of the control implementation
        :return: The assessment
        :rtype: regscale_models.Assessment
        """
        logger.info(
            f"Getting or creating assessment for control implementation {control_implementation_id}"
        )
        assessment: regscale_models.Assessment | None = self.assessment_map.get(
            control_implementation_id
        )
        if assessment:
            logger.debug(
                f"Found cached assessment {assessment.id} for control implementation {control_implementation_id}"
            )
        else:
            logger.debug(
                f"Assessment not found for control implementation {control_implementation_id}"
            )
            assessment = regscale_models.Assessment(
                plannedStart=get_current_datetime(),
                plannedFinish=get_current_datetime(),
                status=regscale_models.AssessmentStatus.COMPLETE.value,
                assessmentResult=regscale_models.AssessmentResultsStatus.FAIL.value,
                actualFinish=get_current_datetime(),
                leadAssessorId=self.assessor_id,
                parentId=control_implementation_id,
                parentModule=regscale_models.ControlImplementation.get_module_string(),
                title=f"{self.title} Assessment",
                assessmentType=regscale_models.AssessmentType.QA_SURVEILLANCE.value,
            ).create()
        self.assessment_map[control_implementation_id] = assessment
        return assessment

    def create_issue_from_finding(
        self, control_implementation_id: int, finding: IntegrationFinding
    ) -> regscale_models.Issue:
        """
        Creates a RegScale issue from a finding

        :param int control_implementation_id: The ID of the control implementation
        :param IntegrationFinding finding: The finding data
        :return: The Issue create from the finding
        :rtype: regscale_models.Issue
        """
        return regscale_models.Issue(
            parentId=control_implementation_id,
            parentModule=regscale_models.ControlImplementation.get_module_string(),
            title=finding.title,
            dateCreated=finding.date_created,
            status=finding.status,
            severityLevel=finding.severity,
            issueOwnerId=self.assessor_id,
            securityPlanId=self.plan_id,
            identification=finding.external_id,
            dueDate=get_current_datetime(),
            description=finding.description,
        ).create()

    @staticmethod
    def update_issues_from_finding(
        issue: regscale_models.Issue, finding: IntegrationFinding
    ) -> regscale_models.Issue:
        """
        Updates RegScale issues based on the integration findings

        :param regscale_models.Issue issue: The issue to update
        :param IntegrationFinding finding: The integration findings
        :return: The updated issue
        :rtype: regscale_models.Issue
        """
        issue.status = finding.status
        issue.severityLevel = finding.severity
        issue.dateLastUpdated = finding.date_last_updated
        issue.description = finding.description
        return issue.save()

    def handle_passing_finding(
        self,
        existing_issues: List[regscale_models.Issue],
        finding: IntegrationFinding,
        control_implementation_id: int,
    ) -> None:
        """
        Handles findings that have passed by closing any open issues associated with the finding.

        :param List[regscale_models.Issue] existing_issues: The list of existing issues to check against
        :param IntegrationFinding finding: The finding data that has passed
        :param int control_implementation_id: The ID of the control implementation associated with the finding
        :return: None
        """
        for issue in existing_issues:
            if (
                issue.identification == finding.external_id
                and issue.status != regscale_models.IssueStatus.Closed
            ):
                logger.info(
                    f"Closing issue {issue.id} for control {self.control_map[control_implementation_id]}"
                )
                issue.status = regscale_models.IssueStatus.Closed
                issue.dateCompleted = finding.date_last_updated
                issue.save()

    def handle_failing_finding(
        self,
        existing_issues: List[regscale_models.Issue],
        finding: IntegrationFinding,
        control_implementation_id: int,
    ) -> None:
        """
        Handles findings that have failed by updating an existing open issue or creating a new one.

        :param List[regscale_models.Issue] existing_issues: The list of existing issues to check against
        :param IntegrationFinding finding: The finding data that has failed
        :param int control_implementation_id: The ID of the control implementation associated with the finding
        :return: None
        """
        found_issue = None
        for issue in existing_issues:
            if (
                issue.identification == finding.external_id
                and issue.status != regscale_models.IssueStatus.Closed
            ):
                logger.info(
                    f"Updating issue {issue.id} for control {self.control_map[control_implementation_id]}"
                )
                found_issue = self.update_issues_from_finding(
                    issue=issue, finding=finding
                )
                break
        if not found_issue:
            # Create a new issue if one doesn't exist
            logger.info(
                f"Creating issue for control {self.control_map[control_implementation_id]}"
            )
            self.create_issue_from_finding(control_implementation_id, finding)

    def update_regscale_findings(self, findings: List[IntegrationFinding]) -> None:
        """
        Updates RegScale findings based on the integration findings

        :param List[IntegrationFinding] findings: The integration findings
        :return: None
        """
        for finding in findings:
            if finding:
                for control_implementation_id in finding.control_ids:
                    assessment = self.get_or_create_assessment(
                        control_implementation_id
                    )
                    control_test = regscale_models.ControlTest(
                        uuid=finding.external_id,
                        parentControlId=control_implementation_id,
                        testCriteria=finding.description,
                    ).get_or_create()
                    regscale_models.ControlTestResult(
                        parentTestId=control_test.id,
                        parentAssessmentId=assessment.id,
                        uuid=finding.external_id,
                        result=finding.status,
                        dateAssessed=finding.date_created,
                        assessedById=self.assessor_id,
                        gaps=finding.gaps,
                        observations=finding.observations,
                        evidence=finding.evidence,
                        identifiedRisk=finding.identified_risk,
                        impact=finding.impact,
                        recommendationForMitigation=finding.recommendation_for_mitigation,
                    ).create()
                    logger.info(
                        f"Created or Updated assessment {assessment.id} for control "
                        f"{self.control_map[control_implementation_id]}"
                    )
                    existing_issues: list[regscale_models.Issue] = (
                        regscale_models.Issue.get_all_by_parent(
                            parent_id=control_implementation_id,
                            parent_module=regscale_models.ControlImplementation.get_module_string(),
                        )
                    )
                    if finding.status == regscale_models.ControlTestResultStatus.PASS:
                        self.handle_passing_finding(
                            existing_issues, finding, control_implementation_id
                        )
                    else:
                        self.handle_failing_finding(
                            existing_issues, finding, control_implementation_id
                        )

    def update_regscale_assets(self, assets: List[IntegrationAsset]) -> None:
        """
        Updates RegScale assets based on the integration assets

        :param List[IntegrationAsset] assets: The integration assets
        :return: None
        """
        logger.info("Updating RegScale assets...")

        if any(assets):
            existing_assets: list[regscale_models.Asset] = (
                regscale_models.Asset.get_all_by_parent(
                    parent_id=assets[0].parent_id,
                    parent_module=assets[0].parent_module,
                )
            )

            for asset in assets:
                self.update_or_create_asset(asset, existing_assets)

    def update_or_create_asset(
        self, asset: IntegrationAsset, existing_assets: List[regscale_models.Asset]
    ) -> None:
        """
        Updates an existing asset or creates a new one

        :param IntegrationAsset asset: The integration asset
        :param List[regscale_models.Asset] existing_assets: The existing assets
        :return: None
        """
        found_asset = self.find_existing_asset(asset, existing_assets)

        if found_asset:
            self.update_asset_if_needed(asset, found_asset)
        else:
            self.create_new_asset(asset)

    def find_existing_asset(
        self, asset: IntegrationAsset, existing_assets: List[regscale_models.Asset]
    ) -> Optional[regscale_models.Asset]:
        """
        Finds an existing asset that matches the integration asset

        :param IntegrationAsset asset: The integration asset
        :param List[regscale_models.Asset] existing_assets: The existing assets
        :return: The matching existing asset, or None if no match is found
        :rtype: Optional[regscale_models.Asset]
        """
        for existing_asset in existing_assets:
            if asset.identifier == getattr(existing_asset, self.asset_identifier_field):
                return existing_asset
        return None

    @staticmethod
    def update_asset_if_needed(
        asset: IntegrationAsset, existing_asset: regscale_models.Asset
    ) -> None:
        """
        Updates an existing asset if any of its fields differ from the integration asset

        :param IntegrationAsset asset: The integration asset
        :param regscale_models.Asset existing_asset: The existing asset
        :return: None
        """
        is_updated = False
        if existing_asset.assetOwnerId != asset.asset_owner_id:
            existing_asset.assetOwnerId = asset.asset_owner_id
            is_updated = True
        if existing_asset.parentId != asset.parent_id:
            existing_asset.parentId = asset.parent_id
            is_updated = True
        if existing_asset.parentModule != asset.parent_module:
            existing_asset.parentModule = asset.parent_module
            is_updated = True
        if existing_asset.assetType != asset.asset_type:
            existing_asset.assetType = asset.asset_type
            is_updated = True
        if existing_asset.status != asset.status:
            existing_asset.status = asset.status
            is_updated = True
        if existing_asset.assetCategory != asset.asset_category:
            existing_asset.assetCategory = asset.asset_category
            is_updated = True

        if is_updated:
            existing_asset.dateLastUpdated = asset.date_last_updated
            existing_asset.save()
            logger.info(f"Updated asset {asset.identifier}")
        else:
            logger.info(f"Asset {asset.identifier} is already up to date")

    def create_new_asset(self, asset: IntegrationAsset) -> None:
        """
        Creates a new asset based on the integration asset

        :param IntegrationAsset asset: The integration asset
        :return: None
        """
        new_asset = regscale_models.Asset(
            name=asset.name,
            assetOwnerId=asset.asset_owner_id,
            parentId=asset.parent_id,
            parentModule=asset.parent_module,
            assetType=asset.asset_type,
            dateLastUpdated=asset.date_last_updated,
            status=asset.status,
            assetCategory=asset.asset_category,
        )
        setattr(new_asset, self.asset_identifier_field, asset.identifier)
        new_asset.create()
        logger.info(f"Created asset {asset.identifier}")

    @classmethod
    def sync_findings(cls, plan_id: int) -> None:
        """
        Syncs findings from the integration to RegScale

        :param int plan_id: The ID of the security plan
        :return: None
        """
        logger.info(f"Syncing {cls.title} findings...")
        instance = cls(plan_id)
        instance.update_regscale_findings(findings=instance.fetch_findings())

    @classmethod
    def sync_assets(cls, plan_id: int) -> None:
        """
        Syncs assets from the integration to RegScale

        :param int plan_id: The ID of the security plan
        :return: None
        """
        logger.info(f"Syncing {cls.title} assets...")
        instance = cls(plan_id)
        instance.update_regscale_assets(assets=instance.fetch_assets())
