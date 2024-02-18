#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Model for Control Test Results in the application """
from enum import Enum
from typing import Optional

from pydantic import ConfigDict

from . import RegScaleModel


class ControlTestResultStatus(str, Enum):
    """Control Test Statuses"""

    FAIL = "Fail"
    PASS = "Pass"


class ControlTestResult(RegScaleModel):
    """Control Test Results model"""

    _module_slug = "controltestresults"

    id: Optional[int] = None
    is_public: bool = True
    result: ControlTestResultStatus
    uuid: Optional[str] = None
    observations: Optional[str] = None
    gaps: Optional[str] = None
    evidence: Optional[str] = None
    bIssue: Optional[bool] = None
    originalRisk: Optional[str] = None
    identifiedRisk: Optional[str] = None
    likelihood: Optional[str] = None
    impact: Optional[str] = None
    recommendationForMitigation: Optional[str] = None
    dateAssessed: Optional[str] = None
    assessedById: Optional[str] = None
    parentTestId: Optional[int] = None
    parentAssessmentId: Optional[int] = None

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the ControlTestResults model

        :return: Additional endpoints for the ControlTestResults model
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_by_parent="/api/{model_slug}/getByAssessment/{intParentID}"
        )
