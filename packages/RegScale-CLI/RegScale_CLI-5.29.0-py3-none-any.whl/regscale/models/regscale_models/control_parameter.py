#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Model for Control Parameter in the application """
import warnings
from typing import Optional
from urllib.parse import urljoin

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.api_handler import APIInsertionError
from regscale.models.regscale_models import RegScaleModel


class ControlParameter(RegScaleModel):
    """
    ControlParameter class
    """

    _module_slug = "controlparameters"

    id: Optional[int] = 0
    uuid: Optional[str] = None
    text: Optional[str] = None
    parameterId: Optional[str] = None
    securityControlId: Optional[int] = None
    archived: bool = False
    createdById: Optional[str] = None
    dateCreated: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    dateLastUpdated: Optional[str] = None
    tenantsId: Optional[int] = None
    dataType: Optional[str] = None
    isPublic: bool = True
    default: Optional[str] = None

    def insert_parameter(self, app: Application) -> dict:
        """
        DEPRECATED: Insert a new control parameter

        :param Application app: Application object
        :raises APIInsertionError: If the API request fails
        :return: JSON response as a dictionary
        :rtype: dict
        """
        warnings.warn(
            "The 'insert_parameter' method is deprecated, use 'create' method instead",
            DeprecationWarning,
        )

        # Convert the model to a dictionary
        api = Api()
        data = self.dict()
        api_url = urljoin(app.config["domain"], "/api/controlparameters")
        # Make the API call
        response = api.post(api_url, json=data)

        # Check the response
        if not response.ok:
            print(response.text)
            raise APIInsertionError(
                f"API request failed with status {response.status_code}"
            )

        return response.json()
