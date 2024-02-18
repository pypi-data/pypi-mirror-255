#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Dataclass for Control Objective in the application """
from dataclasses import dataclass, field
from typing import Any

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.objective import Objective


@dataclass
class ControlObjective(Objective):
    """RegScale Control Objective"""

    name: str
    description: str
    otherId: str
    archived: bool
    createdById: str = ""
    lastUpdatedById: str = ""
    dateCreated: str = field(default_factory=get_current_datetime)
    dateLastUpdated: str = field(default_factory=get_current_datetime)
    objectiveType: str = "statement"

    @staticmethod
    def from_dict(obj: Any) -> "ControlObjective":
        """
        Create ControlObjective object from dict

        :param obj: Dictionary
        :return: ControlObjective class from provided dict
        :rtype: ControlObjective
        """
        _securityControlId = int(obj.get("securityControlId", 0))
        _id = int(obj.get("id", 0))
        _uuid = str(obj.get("uuid"))
        _name = str(obj.get("name"))
        _description = str(obj.get("description"))
        _otherId = str(obj.get("otherId"))
        _objectiveType = str(obj.get("objectiveType"))
        _archived = False
        return ControlObjective(
            _securityControlId,
            _id,
            _uuid,
            _name,
            _description,
            _otherId,
            _objectiveType,
            _archived,
        )
