#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Model for Control Test in the application """

from pydantic import ConfigDict

from regscale.models.regscale_models import RegScaleModel


class ControlTest(RegScaleModel):
    """Properties plan model"""

    _module_slug = "controltests"
    _unique_fields = ["uuid"]

    id: int = 0
    isPublic: bool = True
    uuid: str
    testCriteria: str
    parentControlId: int
    parentRequirementId: int = 0

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Function to get additional endpoints for the ControlTest model

        :return: Additional endpoints for the ControlTest model
        :rtype: ConfigDict
        """
        return ConfigDict(get_by_parent="/api/{model_slug}/getByControl/{intParentID}")  # type: ignore
