#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Model for a RegScale Component """
# standard python imports
from typing import Optional, Any, Union
from enum import Enum

from pydantic import ConfigDict

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.models.regscale_models.regscale_model import RegScaleModel


class ComponentType(str, Enum):
    """Component Type Enum"""

    Hardware = "hardware"
    Software = "software"
    Service = "service"
    Policy = "policy"
    Process = "process"
    Procedure = "procedure"
    ComplianceArtifact = "compliance artifact"


class ComponentStatus(str, Enum):
    """Component Status Enum"""

    DraftPending = "Draft/Pending"
    Active = "Active"
    InactiveRetired = "Inactive/Retired"
    Cancelled = "Cancelled"
    UndergoingMajorModification = "Undergoing Major Modification"
    Other = "Other"


class Component(RegScaleModel):
    """Component Model"""

    _module_slug = "components"

    title: str
    description: str
    componentType: Union[ComponentType, str]
    componentOwnerId: str = ""
    status: Union[ComponentStatus, str] = ComponentStatus.Active
    id: int = 0
    defaultAssessmentDays: int = 0
    purpose: Optional[str] = None
    securityPlansId: Optional[int] = None
    cmmcAssetType: Optional[str] = None
    createdBy: Optional[str] = None
    createdById: Optional[str] = None
    dateCreated: Optional[str] = None
    lastUpdatedBy: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    dateLastUpdated: Optional[str] = None
    uuid: Optional[str] = None
    componentOwner: Optional[str] = None
    cmmcExclusion: bool = False
    isPublic: bool = True

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Components model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_list="/api/{model_slug}/getList",
            get_all_by_parent="/api/{model_slug}/getAllByParent/{intParentID}",
            get_count="/api/{model_slug}/getCount",
            graph="/api/{model_slug}/graph",
            graph_by_date="/api/{model_slug}/graphByDate/{strGroupBy}",
            report="/api/{model_slug}/report/{strReport}",
            filter_components="/api/{model_slug}/filterComponents",
            filter_component_dashboard="/api/{model_slug}/filterComponentDashboard",
            query_by_custom_field="/api/{model_slug}/queryByCustomField/{strFieldName}/{strValue}",
            get="/api/{model_slug}/find/{id}",
            evidence="/api/{model_slug}/evidence/{intID}",
            find_by_guid="/api/{model_slug}/findByGUID/{strGUID}",
            find_by_external_id="/api/{model_slug}/findByExternalId/{strID}",
            get_titles="/api/{model_slug}/getTitles",
            main_dashboard="/api/{model_slug}/mainDashboard/{intYear}",
            component_dashboard="/api/{model_slug}/componentDashboard/{intYear}",
            oscal="/api/{model_slug}/oscal/{intID}",
            statusboard="/api/{model_slug}/statusboard/{intID}/{strSearch}/{intPage}/{pageSize}",
            emass_export="/api/{model_slug}/emassExport/{intID}",
            mega_api="/api/{model_slug}/megaAPI/{intId}",
        )

    def __eq__(self, other) -> bool:
        """
        Check if two Component objects are equal

        :param other: Component object to compare
        :return: True if equal, False if not
        :rtype: bool
        """
        return (
            self.title == other.title
            and self.description == other.description
            and self.componentType == other.componentType
        )

    def __hash__(self) -> int:
        """
        Hash a Component object

        :return: Hashed Component object
        :rtype: int
        """
        return hash((self.title, self.description, self.componentType))

    def __getitem__(self, key: Any) -> Any:
        """
        Get attribute from Pipeline

        :param Any key: Key to get value for
        :return: value of provided key
        :rtype: Any
        """
        if getattr(self, key) == "None":
            return None
        return getattr(self, key)

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set attribute in Pipeline with provided key

        :param Any key: Key to change to provided value
        :param Any value: New value for provided Key
        :return: None
        """
        return setattr(self, key, value)

    @staticmethod
    def get_components_from_ssp(app: Application, ssp_id: int) -> list[dict]:
        """
        Get all components for a given SSP

        :param Application app: Application instance
        :param int ssp_id: RegScale SSP
        :return: List of component dictionaries
        :rtype: list[dict]
        """
        api = Api()
        existing_res = api.get(
            app.config["domain"] + f"/api/components/getAllByParent/{ssp_id}"
        )
        existing_res.raise_for_status()
        return existing_res.json()
