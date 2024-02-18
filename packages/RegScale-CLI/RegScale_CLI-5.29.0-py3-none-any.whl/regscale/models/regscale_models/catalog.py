#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Model for Catalog in the application"""
import warnings
from typing import Optional
from urllib.parse import urljoin

from pydantic import ConfigDict

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.api_handler import APIRetrieveError
from regscale.models.regscale_models.regscale_model import RegScaleModel


class Catalog(RegScaleModel):
    """Catalog class"""

    _module_slug = "catalogues"

    id: Optional[int] = 0
    abstract: Optional[str] = None
    datePublished: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[str] = None
    lastRevisionDate: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    tenantsId: Optional[int] = None
    uuid: Optional[str] = None
    createdById: Optional[str] = None
    dateCreated: Optional[str] = None
    dateLastUpdated: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    master: bool = False
    sourceOscalURL: Optional[str] = None
    archived: bool = False
    isPublic: bool = True

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Catalogues model

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_count="/api/{model_slug}/getCount",
            get_list="/api/{model_slug}/getList",
            get_catalog_with_all_details="/api/{model_slug}/getCatalogWithAllDetails/{intID}",
            filter_catalogues="/api/{model_slug}/filterCatalogues",
            graph="/api/{model_slug}/graph",
            convert_mappings="/api/{model_slug}/convertMappings/{intID}",
            find_by_guid="/api/{model_slug}/findByGUID/{strID}",
            get_titles="/api/{model_slug}/getTitles",
            get_nist="/api/{model_slug}/getNIST",
        )

    def insert_catalog(self, app: Application) -> "Catalog":  # noqa
        """
        DEPRECATED: This method is deprecated and will be removed in a future version.
        Use the create method instead.

        Insert catalog into database

        :param Application app: Application
        :raises APIInsertionError: API request failed
        :return: Catalog
        :rtype: Catalog
        """
        warnings.warn(
            "insert_catalog is deprecated and will be removed in a future version. Use create method instead.",
            DeprecationWarning,
        )
        # Convert the model to a dictionary
        return self.create()

    @staticmethod
    def get_catalogs(app: Application) -> list:
        """
        DEPRECATED: This method is deprecated and will be removed in a future version.
        Use the get_list method instead.

        Get all catalogs from database

        :param Application app: Application
        :raises APIRetrieveError: API request failed
        :return: list of catalogs
        :rtype: list
        """
        warnings.warn(
            "get_catalogs is deprecated and will be removed in a future version. Use get_list method instead.",
            DeprecationWarning,
        )
        api = Api()
        api_url = urljoin(app.config["domain"], "/api/catalogues")
        response = api.get(api_url)
        if not response.ok:
            api.logger.debug(
                f"API request failed with status: {response.status_code}: {response.reason} {response.text}"
            )
            raise APIRetrieveError(
                f"API request failed with status {response.status_code}"
            )
        return response.json()

    @classmethod
    def get_with_all_details(cls, catalog_id: int) -> Optional[list]:
        """
        Retrieves a catalog with all details by its ID.

        :param catalog_id: The ID of the catalog
        :return: The response from the API or None
        :rtype: Optional[list]
        """
        endpoint = cls.get_endpoint("get_catalog_with_all_details").format(
            model_slug=cls._module_slug, intID=catalog_id
        )
        response = cls._api_handler.get(endpoint)

        if response and response.ok and response.status_code not in [204, 404]:
            return response.json()
        return None
