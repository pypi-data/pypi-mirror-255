#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Model for Profile Mapping in the application """

from pydantic import BaseModel
from regscale.core.app.api import Api
from regscale.core.app.application import Application
from urllib.parse import urljoin
from typing import List, Optional


class ProfileMapping(BaseModel):
    """
    Profile Mapping Model
    """

    id: int = 0
    profileID: Optional[int] = None
    controlID: Optional[int] = None
    tenantsId: Optional[int] = None
    createdById: Optional[str] = None
    dateCreated: Optional[str] = None
    dateLastUpdated: Optional[str] = None
    isPublic: bool = True
    lastUpdatedById: Optional[str] = None

    def insert_profile_mapping(self, app: Application) -> dict:
        """
        Insert a new profile mapping

        :param Application app: Application
        :raises Exception: API request failed
        :return: dict of profile mapping
        :rtype: dict
        """
        api = Api()
        # Convert the model to a dictionary
        data = self.dict()
        api_url = urljoin(app.config["domain"], "/api/profileMapping")

        # Make the API call
        response = api.post(url=api_url, json=data)

        # Check the response
        if not response.ok:
            api.logger.debug(
                f"API Call failed to: {api_url}\n{response.status_code}: {response.reason} {response.text}"
            )
            raise response.raise_for_status()

        return response.json()

    @staticmethod
    def insert_batch(app: Application, mappings: List["ProfileMapping"]) -> list[dict]:
        """
        Insert a new list of profile mappings as a batch

        :param Application app: Application
        :param List[ProfileMapping] mappings: List of profile mappings
        :return: list(dict) of profile mappings
        :rtype: list(dict)
        """
        api = Api()
        # Convert the model to a dictionary

        data = [item.dict() for item in mappings]
        for d in data:
            d["isPublic"] = "true"
        api_url = urljoin(app.config["domain"], "/api/profileMapping/batchCreate")

        # Make the API call
        response = api.post(url=api_url, json=data)

        # Check the response
        return response.json() if response.ok else response.raise_for_status()
