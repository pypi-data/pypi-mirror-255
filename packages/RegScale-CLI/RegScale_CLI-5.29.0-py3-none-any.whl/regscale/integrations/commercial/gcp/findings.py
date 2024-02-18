#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Sync GCP Findings with RegScale Findings """

import json
import logging

from google.api_core.exceptions import InvalidArgument
from google.cloud.securitycenter_v1 import Finding
from google.cloud.securitycenter_v1.services.security_center.pagers import (
    ListFindingsPager,
)

from regscale.core.app.utils.api_handler import APIHandler
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.integrations.commercial.gcp.auth import get_gcp_security_center_client
from regscale.integrations.commercial.gcp.variables import GcpVariables
from regscale.models import regscale_models

logger = logging.getLogger(__name__)


def fetch_gcp_findings() -> ListFindingsPager:
    """
    Fetches GCP findings using the SecurityCenterClient

    :raises NameError: If gcpFindingSources is set incorrectly
    :return: A pager to iterate over GCP's findings
    :rtype: ListFindingsPager
    """
    logger.info("Fetching GCP findings...")
    sources = f"projects/{GcpVariables.gcpProjectId}/sources/-"
    try:
        client = get_gcp_security_center_client()
        findings = client.list_findings(request={"parent": sources})
        logger.info("Fetched GCP findings.")
    except InvalidArgument:
        error_msg = f"gcpFindingSources is set incorrectly: {sources}."
        logger.error(error_msg)
        raise NameError(error_msg)
    return findings


def update_regscale_findings(findings: ListFindingsPager, plan_id: int) -> None:
    """
    Updates RegScale findings with the provided GCP findings

    :param ListFindingsPager findings: A pager to iterate over GCP's findings
    :param int plan_id: The ID of the security plan to update in RegScale
    :return: None
    """
    logger.info("Updating RegScale findings...")
    ci_map = regscale_models.ControlImplementation.get_control_map_by_plan(
        plan_id=plan_id
    )

    api_handler = APIHandler()
    user_id = api_handler.get_user_id()

    for i, finding_result in enumerate(findings):
        finding_data = Finding.to_json(finding_result.finding)
        fd = json.loads(finding_data)
        for control_id in (
            fd.get("sourceProperties", {})
            .get("compliance_standards", {})
            .get("nist", [{}])[0]
            .get("ids", [])
        ):
            if ci_id := ci_map.get(control_id.lower()):
                ci = regscale_models.ControlImplementation.get_object(id=ci_id)
                assessment = regscale_models.Assessment(
                    plannedStart=get_current_datetime(),
                    plannedFinish=get_current_datetime(),
                    status=regscale_models.AssessmentStatuses.COMPLETE.value,
                    assessmentResult=regscale_models.AssessmentResultsStatuses.FAIL.value,
                    actualFinish=get_current_datetime(),
                    leadAssessorId=user_id,
                    parentId=ci.id,
                    parentName="controlimplmentations",
                    parentModule="controls",
                    title="GCP Control Assessment",
                    assessmentType=regscale_models.AssessmentTypes.QA_SURVEILLANCE.value,
                    summaryOfResults=(
                        f"<h1>Summary of Results</h1>"
                        f"<p><strong>Name:</strong> {fd.get('name', '')}</p>"
                        f"<p><strong>Resource Name:</strong> {fd.get('resourceName', '')}</p>"
                        f"<p><strong>State:</strong> {fd.get('state', '')}</p>"
                        f"<p><strong>Category:</strong> {fd.get('category', '')}</p>"
                        f"<p><strong>External URI:</strong> <a href='{fd.get('externalUri', '')}'>{fd.get('externalUri', '')}</a></p>"
                        f"<p><strong>Recommendation:</strong> {fd.get('sourceProperties', {}).get('Recommendation', '')}</p>"
                        f"<p><strong>Explanation:</strong> {fd.get('sourceProperties', {}).get('Explanation', '')}</p>"
                        f"<p><strong>Exception Instructions:</strong> {fd.get('sourceProperties', {}).get('ExceptionInstructions', '')}</p>"
                        f"<p><strong>Severity:</strong> {fd.get('severity', '')}</p>"
                        f"<p><strong>Mute:</strong> {fd.get('mute', '')}</p>"
                        f"<p><strong>Finding Class:</strong> {fd.get('findingClass', '')}</p>"
                        f"<p><strong>Description:</strong> {fd.get('description', '')}</p>"
                    ),
                ).create()
                control_test = regscale_models.ControlTest(
                    uuid=fd.get("name", ""),
                    parentControlId=ci.id,
                    testCriteria=fd.get("description", ""),
                ).get_or_create()
                regscale_models.ControlTestResults(
                    parentTestId=control_test.id,
                    parentAssessmentId=assessment.id,
                    uuid=fd.get("name", ""),
                    result=fd.get("state", ""),
                    dateAssessed=fd.get("createTime", ""),
                    assessedById=user_id,
                    gaps=fd.get("description", ""),
                    observations=fd.get("sourceProperties", {}).get("Explanation", ""),
                    evidence=json.dumps(
                        fd.get("sourceProperties", {}).get("OffendingIamRolesList", [])
                    ),
                    identifiedRisk=fd.get("sourceProperties", {}).get(
                        "Recommendation", ""
                    ),
                    impact=str(fd.get("severity", "")),
                    likelihood=str(fd.get("mute", "")),
                    recommendationForMitigation=fd.get("sourceProperties", {}).get(
                        "Recommendation", ""
                    ),
                    originalRisk=fd.get("sourceProperties", {}).get(
                        "Recommendation", ""
                    ),
                ).create()
                logger.info(
                    f"Created assessment #{assessment.id} in RegScale for control {control_id}."
                )
            else:
                logger.info(f"Control {control_id} not found.")

    logger.info("Updated RegScale findings.")


def sync_gcp_findings(plan_id: int) -> None:
    """
    Syncs GCP findings with RegScale findings

    :param int plan_id: The ID of the security plan to update
    :return: None
    """
    logger.info("Syncing GCP findings...")
    update_regscale_findings(findings=fetch_gcp_findings(), plan_id=plan_id)
    logger.info("Synced GCP findings.")
