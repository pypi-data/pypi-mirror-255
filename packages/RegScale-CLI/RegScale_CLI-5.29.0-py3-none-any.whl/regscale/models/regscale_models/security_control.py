#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Dataclass for Security Control in the application """

from dataclasses import asdict, dataclass
from typing import Any, List, Optional

from regscale.core.app.api import Api
from regscale.core.app.application import Application


@dataclass
class SecurityControl:
    """Security Control

    :return: A RegScale Security Control instance
    """

    id: int
    isPublic: bool
    uuid: str
    controlId: str
    sortId: str
    controlType: str
    references: str
    relatedControls: str
    subControls: str
    enhancements: str
    family: str
    mappings: str
    assessmentPlan: str
    weight: float
    catalogueID: int
    practiceLevel: str
    objectives: List[object]
    tests: List[object]
    parameters: List[object]
    archived: bool = False
    createdById: Optional[str] = None
    dateCreated: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    dateLastUpdated: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> "SecurityControl":
        _id = int(obj.get("id")) if obj.get("id") else None
        _isPublic = bool(obj.get("isPublic")) if obj.get("isPublic") else False
        _uuid = str(obj.get("uuid")) if obj.get("uuid") else None
        _controlId = str(obj.get("controlId")) if obj.get("controlId") else None
        _sortId = str(obj.get("sortId")) if obj.get("sortId") else None
        _controlType = str(obj.get("controlType")) if obj.get("controlType") else None
        _title = str(obj.get("title")) if obj.get("title") else None
        _description = str(obj.get("description")) if obj.get("description") else ""
        _references = str(obj.get("references")) if obj.get("references") else ""
        _relatedControls = (
            str(obj.get("relatedControls")) if obj.get("relatedControls") else ""
        )
        _subControls = str(obj.get("subControls")) if obj.get("subControls") else ""
        _enhancements = str(obj.get("enhancements")) if obj.get("enhancements") else ""
        _family = str(obj.get("family")) if obj.get("family") else ""
        _mappings = str(obj.get("mappings")) if obj.get("mappings") else ""
        _assessmentPlan = (
            str(obj.get("assessmentPlan")) if obj.get("assessmentPlan") else ""
        )
        _weight = float(obj.get("weight")) if obj.get("weight") else None
        _catalogueID = int(obj.get("catalogueID")) if obj.get("catalogueID") else None
        _practiceLevel = (
            str(obj.get("practiceLevel")) if obj.get("practiceLevel") else None
        )
        _archived = bool(obj.get("archived")) if obj.get("archived") else False
        _createdById = str(obj.get("createdById")) if obj.get("createdById") else None
        _dateCreated = str(obj.get("dateCreated")) if obj.get("dateCreated") else None
        _lastUpdatedById = (
            str(obj.get("lastUpdatedById")) if obj.get("lastUpdatedById") else None
        )
        _dateLastUpdated = (
            str(obj.get("dateLastUpdated")) if obj.get("dateLastUpdated") else None
        )
        return SecurityControl(
            _id,
            _isPublic,
            _uuid,
            _controlId,
            _sortId,
            _controlType,
            _title,
            _description,
            _references,
            _relatedControls,
            _subControls,
            _enhancements,
            _family,
            _mappings,
            _assessmentPlan,
            _weight,
            _catalogueID,
            _practiceLevel,
            _archived,
            _createdById,
            _dateCreated,
            _lastUpdatedById,
            _dateLastUpdated,
        )

    def __hash__(self):
        """
        Enable object to be hashable

        :return: Hashed SecurityControl
        """
        return hash((self.controlId, self.catalogueID))

    def __getitem__(self, key: any) -> any:
        """
        Get attribute from Pipeline

        :param key: Key to get value for
        :return: value of provided key
        :rtype: any
        """
        return getattr(self, key)

    def __setitem__(self, key: any, value: any) -> None:
        """
        Set attribute in Pipeline with provided key

        :param key: Key to change to provided value
        :param value: New value for provided Key
        :return: None
        """
        return setattr(self, key, value)

    def __eq__(self, other) -> bool:
        """
        Update items in SecurityControl class

        :param other: Object to compare to
        :return: Whether the two objects are equal
        :rtype: bool
        """
        return (
            self.controlId == other.controlId and self.catalogueID == other.catalogueID
        )

    def dict(self) -> dict:
        """
        Create a dictionary from the SecurityControl dataclass

        :return: Dictionary of SecurityControl
        :rtype: dict
        """
        return {k: v for k, v in asdict(self).items()}

    @staticmethod
    def lookup_control(
        app: Application,
        control_id: int,
    ) -> "SecurityControl":
        """
        Return a Security Control in RegScale via API

        :param Application app: Application Instance
        :param int control_id: ID of the Security Control to look up
        :return: A Security Control from RegScale
        :rtype: SecurityControl
        """
        api = Api()
        control = api.get(
            url=app.config["domain"] + f"/api/securitycontrols/{control_id}"
        ).json()
        return SecurityControl.from_dict(control)

    @staticmethod
    def lookup_control_by_name(
        app: Application, control_name: str, catalog_id: int
    ) -> Optional["SecurityControl"]:
        """
        Lookup a Security Control by name and catalog ID

        :param Application app: Application instance
        :param str control_name: Name of the security control
        :param int catalog_id: Catalog ID for the security control
        :return: A Security Control from RegScale, if found
        :rtype: Optional[SecurityControl]
        """
        api = Api()
        config = api.config
        res = api.get(
            config["domain"]
            + f"/api/securitycontrols/findByUniqueId/{control_name}/{catalog_id}"
        )
        return SecurityControl.from_dict(res.json()) if res.status_code == 200 else None
