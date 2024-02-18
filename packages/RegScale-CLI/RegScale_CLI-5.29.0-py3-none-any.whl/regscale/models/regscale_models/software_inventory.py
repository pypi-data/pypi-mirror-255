#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Model for SoftwareInventory in the application """

from typing import List, Optional

from pydantic import BaseModel

from regscale.core.app.api import Api
from regscale.core.app.application import Application


class SoftwareInventory(BaseModel):
    """
    SoftwareInventory
    """

    id: Optional[int] = None
    UUID: Optional[str] = None
    name: Optional[str] = None
    version: Optional[str] = None
    function: Optional[str] = None
    patchLevel: Optional[str] = None
    parentHardwareAssetId: Optional[int] = None
    parentSoftwareInventoryId: Optional[int] = None
    dateLastUpdated: Optional[str] = None
    createdById: Optional[str] = None
    dateCreated: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    isPublic: bool = True
    references: Optional[List[str]] = []

    def __eq__(self, other):
        """
        Override the default Equals behavior

        :param other: SoftwareInventory to compare
        :return: True if equal, False otherwise
        :rtype: bool
        """
        if isinstance(other, SoftwareInventory):
            return (
                self.name == other.name
                and self.version == other.version
                and self.parentHardwareAssetId == other.parentHardwareAssetId
            )
        return False

    def __hash__(self) -> hash:
        """
        Override the default hash behavior

        :return: hash of the SoftwareInventory
        :rtype: hash
        """
        return hash((self.name, self.version, self.parentHardwareAssetId))

    @classmethod
    def insert(cls, app: Application, obj: "SoftwareInventory") -> "SoftwareInventory":
        """
        Insert a new SoftwareInventory into RegScale

        :param Application app: application
        :param SoftwareInventory obj: SoftwareInventory to insert
        :return: SoftwareInventory object
        :rtype: SoftwareInventory
        """
        api = Api()
        result = {}
        res = api.post(
            url=app.config["domain"] + "/api/softwareinventory", json=obj.dict()
        )
        if res.status_code == 200 and res.ok:
            result = SoftwareInventory(**res.json())
        return result

    @classmethod
    def update(cls, app: Application, obj: "SoftwareInventory") -> "SoftwareInventory":
        """
        Update an existing SoftwareInventory in RegScale

        :param Application app: application
        :param SoftwareInventory obj: SoftwareInventory to update
        :return: SoftwareInventory object
        :rtype: SoftwareInventory
        """
        api = Api()
        result = {}
        res = api.put(
            url=app.config["domain"] + f"/api/softwareinventory/{obj.id}",
            json=obj.dict(),
        )
        if res.status_code == 200 and res.ok:
            result = SoftwareInventory(**res.json())
        return result

    @classmethod
    def fetch_by_asset(
        cls, app: Application, asset_id: int
    ) -> List["SoftwareInventory"]:
        """
        Fetch all SoftwareInventory for a given asset

        :param Application app: application
        :param asset_id int: The asset id
        :return: A list of SoftwareInventory objects
        :rtype: List[SoftwareInventory]
        """
        api = Api()
        result = []
        res = api.get(
            url=app.config["domain"]
            + f"/api/softwareinventory/getAllByParent/{asset_id}"
        )
        if res.status_code == 200 and res.ok:
            result = [SoftwareInventory(**inv) for inv in res.json()]
        return result
