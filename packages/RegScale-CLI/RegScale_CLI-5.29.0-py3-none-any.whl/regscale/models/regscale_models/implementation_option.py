#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" RegScale Implementation Option Model """

from datetime import datetime
from typing import Optional
from urllib.parse import urljoin

import requests
from pydantic import BaseModel

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.models.regscale_models.objective import Objective


class ImplementationOption(BaseModel, Objective):
    """RegScale Implementation Option"""

    id: int = 0
    uuid: str = ""
    name: str  # Required
    description: str  # Required
    acceptability: str  # Required
    otherId: Optional[str] = None
    securityControlId: Optional[int] = None
    objectiveId: Optional[int] = None
    restricted: bool = False
    restrictedSecurityPlanId: Optional[int] = None
    createdById: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    dateCreated: str = datetime.now().isoformat()
    dateLastUpdated: str = datetime.now().isoformat()
    archived: bool = False
    isPublic: bool = True

    def __eq__(self, other) -> bool:
        """
        Check if two ImplementationOption objects are equal

        :param other: ImplementationOption object to compare
        :return: True if equal, False if not
        :rtype: bool
        """
        return (
            self.name == other.name
            and self.description == other.description
            and self.objectiveId == other.objectiveId
            and self.securityControlId == other.securityControlId
        )

    def __hash__(self) -> hash:
        """
        Hash a ImplementationOption object

        :return: Hashed ImplementationOption object
        :rtype: hash
        """
        return hash(
            (self.name, self.description, self.objectiveId, self.securityControlId)
        )

    @staticmethod
    def fetch_implementation_options(
        app: Application, control_id: int
    ) -> list["ImplementationOption"]:
        """
        Fetch list of implementation objectives by control id

        :param Application app: Application Instance
        :param int control_id: Security Control ID
        :return: A list of Implementation Objectives as a dictionary from RegScale via API
        :rtype: list[dict]
        """
        results = []
        logger = create_logger()
        api = Api()
        res = api.get(
            url=app.config["domain"]
            + f"/api/implementationoptions/getByControl/{control_id}"
        )
        if res.ok:
            try:
                results = [ImplementationOption(**opt) for opt in res.json()]
            except requests.RequestException.JSONDecodeError:
                logger.warning("Unable to find control implementation objectives.")
        return results

    def insert(self, api: Api) -> requests.Response:
        """
        Insert implementation option into RegScale

        :param Api api: The API instance
        :return: API Response
        :rtype: requests.Response
        """
        response = api.post(
            url=urljoin(api.config["domain"], "/api/implementationOptions"),
            json=self.dict(),
        )
        api.logger.debug(
            "ImplementationOption insertion Response: %s=%s",
            response.status_code,
            response.text,
        )
        if not response.ok or response.status_code != 200:
            api.logger.error(
                "Unable to insert Implementation Option into RegScale.\n%s:%s %s",
                response.status_code,
                response.reason,
                response.text,
            )
        return response
