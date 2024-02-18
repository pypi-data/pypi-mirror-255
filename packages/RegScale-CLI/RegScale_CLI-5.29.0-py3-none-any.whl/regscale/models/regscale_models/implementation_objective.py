#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Dataclass for Implementation Objective in the application """

from dataclasses import asdict, dataclass, field
from enum import Enum
from logging import Logger
from typing import Any, Optional

import requests
from requests import Response

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.objective import Objective


class ImplementationStatus(Enum):
    """
    Implementation Status
    :param Enum: Enum
    """

    FULLY_IMPLEMENTED = "Fully Implemented"
    PARTIALLY_IMPLEMENTED = "Partially Implemented"
    NOT_IMPLEMENTED = "Not Implemented"


@dataclass
class ImplementationObjective(Objective):
    """RegScale Implementation Objective"""

    notes: str  # Required
    implementationId: int  # Required
    optionId: int  # Required
    status: str = "Not Implemented"  # Required
    objectiveId: Optional[int] = None
    createdById: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    statement: Optional[str] = None  # Should be required
    dateLastAssessed: str = field(default_factory=get_current_datetime)
    dateCreated: str = field(default_factory=get_current_datetime)
    dateLastUpdated: str = field(default_factory=get_current_datetime)

    def __eq__(self, other) -> bool:
        """
        Check if two ImplementationObjective objects are equal

        :param other: ImplementationObjective object to compare to
        :return: True if equal, False if not equal
        :rtype: bool
        """
        if isinstance(other, ImplementationObjective):
            return (
                self.notes == other.notes
                and self.implementationId == other.implementationId
                and self.objectiveId == other.objectiveId
                and self.optionId == other.optionId
                and self.statement == other.statement
            )
        return False

    def __hash__(self) -> hash:
        """
        Hash a ImplementationObjective object

        :return: Hash of ImplementationObjective object
        :rtype: hash
        """
        return hash((self.implementationId, self.objectiveId))

    @property
    def logger(self) -> Logger:
        """
        Logger implementation for a dataclass

        :return: logger object
        :rtype: Logger
        """
        logger = create_logger()
        return logger

    @staticmethod
    def fetch_by_security_control(
        app: Application,
        security_control_id: int,
    ) -> list["ImplementationObjective"]:
        """
        Fetch list of all implementation objectives in RegScale via API

        :param Application app: Application Instance
        :param int security_control_id: Security Control ID # in RegScale
        :return: List of security controls from RegScale
        :rtype: list[ImplementationObjective]
        """
        api = Api()
        logger = create_logger()
        query = """
                    query {
            implementationObjectives  (
                take: 50,
                skip: 0,
                where: { securityControlId:  {eq: placeholder }, })
                {
                items {
                    id,
                    uuid,
                    notes,
                    optionId,
                    implementationId,
                    securityControlId,
                    objectiveId,
                    status
                    }
                totalCount
                pageInfo {
                    hasNextPage
                }
            }
                }
            """.replace(
            "placeholder", str(security_control_id)
        )
        results = []
        data = api.graph(query=query)
        if "implementationObjectives" in data.keys():
            try:
                results.extend(data["implementationObjectives"]["items"])
            except requests.exceptions.JSONDecodeError:
                logger.warning(
                    "Unable to find control implementation objectives for control %i.",
                    security_control_id,
                )
        return [ImplementationObjective(**obj) for obj in results]

    @staticmethod
    def update_objective(
        app: Application,
        obj: Any,
    ) -> Response:
        """
        Update a single implementation objective

        :param Application app: Application Instance
        :param Any obj: Implementation Objective
        :return: Response from RegScale API
        :rtype: Response
        """
        if isinstance(obj, ImplementationObjective):
            obj = asdict(obj)
        api = Api(retry=10)
        return api.put(
            url=app.config["domain"] + f"/api/implementationObjectives/{obj['id']}",
            json=obj,
        )

    @staticmethod
    def insert_objective(
        app: Application,
        obj: Any,
    ) -> Response:
        """
        Update a single implementation objective

        :param Application app: Application Instance
        :param Any obj: Implementation Objective
        :return: Response from RegScale API
        :rtype: Response
        """
        if isinstance(obj, ImplementationObjective):
            obj = asdict(obj)
        api = Api(retry=10)
        res = api.post(
            url=app.config["domain"] + "/api/implementationObjectives", json=obj
        )
        return res

    @staticmethod
    def fetch_implementation_objectives(
        app: Application, control_id: int, query_type: Optional[str] = "implementation"
    ) -> list[dict]:
        """
        Fetch list of implementation objectives by control id

        :param Application app: Application Instance
        :param int control_id: Implementation Control ID
        :param Optional[str] query_type: Query Type for GraphQL query
        :return: A list of Implementation Objectives as a dictionary
        """
        graph_query = """
                        query {
                        implementationObjectives (skip: 0, take: 50,  where: {securityControlId: {eq: placeholder}}) {
                            items {
                                    id
                                    notes
                                    optionId
                                    objectiveId
                                    implementationId
                                    securityControlId
                                    status
                            }
                            totalCount
                                pageInfo {
                                    hasNextPage
                                }
                        }
                    }
                        """.replace(
            "placeholder", str(control_id)
        )
        results = []
        api = Api()
        if query_type != "implementation":
            results = api.graph(graph_query)
        else:
            res = api.get(
                url=app.config["domain"]
                + f"/api/implementationObjectives/getByControl/{control_id}"
            )
            if res.ok:
                try:
                    results = res.json()
                except requests.exceptions.JSONDecodeError:
                    app.logger.warning(
                        "Unable to find control implementation objectives."
                    )
        return results
