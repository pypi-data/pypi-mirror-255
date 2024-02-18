#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Model for Leveraged Authorizations in the application """

from typing import Optional
from urllib.parse import urljoin

from pydantic import BaseModel, field_validator

from regscale.core.app.api import Api
from regscale.core.app.application import Application


class LeveragedAuthorization(BaseModel):
    """LeveragedAuthorizations model."""

    id: Optional[int] = 0
    isPublic: Optional[bool] = True
    uuid: Optional[str] = None
    title: str
    fedrampId: Optional[str] = None
    ownerId: str
    securityPlanId: int
    dateAuthorized: str
    description: Optional[str] = None
    servicesUsed: Optional[str] = None
    securityPlanLink: Optional[str] = ""
    crmLink: Optional[str] = ""
    responsibilityAndInheritanceLink: Optional[str] = ""
    createdById: str
    dateCreated: Optional[str] = None
    lastUpdatedById: str
    dateLastUpdated: Optional[str] = None
    tenantsId: Optional[int] = None

    @field_validator(
        "crmLink",
        "responsibilityAndInheritanceLink",
        "securityPlanLink",
        mode="before",
        check_fields=True,
    )
    def validate_fields(cls, value):
        """
        Validate the CRM link, responsibility and inheritance link, and security plan link.

        :param value: The field value.
        :return: The validated field value or empty string.
        :rtype: str
        """
        if not value:
            value = ""
        return value

    @staticmethod
    def insert_leveraged_authorizations(
        app: Application, leveraged_auth: "LeveragedAuthorization"
    ) -> dict:
        """
        Insert a leveraged authorization into the database.

        :param Application app: The application instance.
        :param LeveragedAuthorization leveraged_auth: The leveraged authorization to insert.
        :return: The response from the API or raise an exception
        :rtype: dict
        """
        api = Api()

        # Construct the URL by joining the domain and endpoint
        url = urljoin(app.config.get("domain"), "/api/leveraged-authorization")
        # Convert the Pydantic model to a dictionary
        data = leveraged_auth.dict()
        # Make the POST request to insert the data
        response = api.post(url, json=data)

        # Check for success and handle the response as needed
        return response.json() if response.ok else response.raise_for_status()
