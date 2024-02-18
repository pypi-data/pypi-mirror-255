#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create Properties model."""
import json
import logging
from typing import List, Union, Optional, Any

from pydantic import ConfigDict, field_validator

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import get_current_datetime, recursive_items
from regscale.models.regscale_models.regscale_model import RegScaleModel

logger = logging.getLogger("rich")


class Property(RegScaleModel):
    """Properties plan model"""

    _module_slug = "properties"
    id: int = 0
    createdById: Optional[str] = ""  # this should be userID
    dateCreated: Optional[str] = get_current_datetime(dt_format="%Y-%m-%dT%H:%M:%S.%fZ")
    lastUpdatedById: Optional[str] = ""  # this should be userID
    isPublic: bool = True
    key: Optional[str] = ""
    value: Optional[Union[str, int]] = ""
    label: Optional[str] = ""
    otherAttributes: Optional[str] = ""
    parentId: Optional[int] = 0
    parentModule: Optional[str] = ""
    dateLastUpdated: Optional[str] = get_current_datetime(
        dt_format="%Y-%m-%dT%H:%M:%S.%fZ"
    )
    alt_id: Optional[str] = None

    @field_validator("value", mode="before")
    def validate_value(cls, value: Any) -> Any:
        """
        Validate the value field and convert it to a string if it is a boolean or list

        :param Any value: Value to validate
        :return: Value if valid
        :rtype: Any
        """
        if isinstance(value, bool):
            return "True" if value else "False"
        if isinstance(value, list):
            return ", ".join(value)
        return value

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Properties model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            batch_create_properties_post="/api/{model_slug}/batchCreate",
            batch_update_properties_put="/api/{model_slug}/batchUpdate",
        )

    @staticmethod
    def create_properties_from_list(
        parent_id: Union[str, int],
        parent_module: str,
        properties_list: List[dict],
    ) -> List["Property"]:
        """
        Create a list of Properties objects from a list of dicts

        :param Union[str, int] parent_id: ID of the SSP to create the Properties objects for
        :param str parent_module: Parent module of the Properties objects
        :param Union[str, int] properties_list: List of dicts to create objects from
        :return: List[dict] of Properties objects
        :rtype: List[Property]
        """
        properties = [
            Property(parentId=int(parent_id), parentModule=parent_module, **properties)
            for properties in properties_list
        ]
        return [
            property_.create_new_properties(return_object=True)
            for property_ in properties
        ]

    def create_new_properties(
        self, return_object: Optional[bool] = False
    ) -> Union[bool, "Property"]:
        """
        Create a new Properties object in RegScale

        :param Optional[bool] return_object: Whether to return the object if successful, defaults to False
        :return: True or the Properties created if successful, False otherwise
        :rtype: Union[bool, Property]
        """
        api = Api()
        data = self.dict()
        data["id"] = None
        data["createdById"] = api.config["userId"]
        data["lastUpdatedById"] = api.config["userId"]
        properties_response = api.post(
            f'{api.config["domain"]}/api/properties/',
            json=data,
        )
        if properties_response.ok:
            logger.info(f'Created Properties: {properties_response.json()["id"]}')
            if return_object:
                return Property(**properties_response.json())
            return True
        logger.error(f"Error creating Properties: {properties_response.text}")
        return False

    def __eq__(self, other) -> bool:
        """
        Test equality of two Property objects

        :param other: Other Property object to compare to
        :return: Equality of two Property objects
        :rtype: bool
        """
        return (
            self.key == other.key
            and self.value == other.value
            and self.parentId == other.parentId
            and self.parentModule == other.parentModule
        )

    @staticmethod
    def generate_property_list_from_dict(dat: dict) -> list["Property"]:
        """
        Generate Property List from Dict

        :param dict dat: Data to generate Property list from
        :return: List of Properties
        :rtype: list["Property"]
        """
        kvs = recursive_items(dat)
        return [
            Property(key=k, value=v, createdById="", parentModule="") for k, v in kvs
        ]

    @staticmethod
    def update_properties(app: Application, prop_list: list["Property"]) -> None:
        """
        Post a list of properties to RegScale

        :param Application app: Application object
        :param List[Property] prop_list: List of properties to post to RegScale
        :return: None
        """
        api = Api()
        props = [prop.dict() for prop in prop_list]
        res = api.put(
            url=app.config["domain"] + "/api/properties/batchupdate",
            json=props,
        )
        if res.status_code == 200:
            if len(prop_list) > 0:
                logger.info(
                    "Successfully updated %i properties to RegScale", len(prop_list)
                )
        else:
            logger.error("Failed to update properties to RegScale\n%s", res.text)

    @staticmethod
    def existing_properties(
        app: Application, existing_assets: list[dict]
    ) -> list["Property"]:
        """
        Return a list of existing properties in RegScale

        :param Application app: Application object
        :param list[dict] existing_assets: List of assets from RegScale
        :return: List of properties for the provided assets
        :rtype: list["Property"]
        """
        properties = []
        api = Api()
        for asset in existing_assets:
            res = api.get(
                url=app.config["domain"]
                + f"/api/properties/getAllByParent/{asset['id']}/assets"
            )
            if res.status_code == 200:
                for prop in res.json():
                    prop["alt_id"] = asset["wizId"]
                    properties.append(Property(**prop))
        return properties

    @staticmethod
    def insert_properties(
        app: Application, prop_list: list["Property"]
    ) -> list["Property"]:
        """
        Post a list of properties to RegScale

        :param Application app: Application instance
        :param list[Property] prop_list: List of properties to post
        :return: List of created properties in RegScale
        :rtype: list["Property"]
        """
        properties = []
        api = Api()
        res = api.post(
            url=app.config["domain"] + "/api/properties/batchcreate",
            json=[prop.dict() for prop in prop_list],
        )
        if res.status_code == 200:
            if len(prop_list) > 0:
                api.logger.info(
                    "Successfully posted %i properties to RegScale", len(prop_list)
                )
            properties = [Property(**prop) for prop in res.json()]
        else:
            logger.error("Failed to post properties to RegScale\n%s", res.text)
        return properties

    @staticmethod
    def get_properties(
        app: Application, wiz_data: str, wiz_id: str
    ) -> list["Property"]:
        """
        Convert Wiz properties data into a list of dictionaries

        :param Application app: Application instance
        :param str wiz_data: Wiz information
        :param str wiz_id: Wiz ID for an issue
        :return: Properties from Wiz
        :rtype: list["Property"]
        """

        # FIXME: remove this nested function, there are 2 flatten dict methods in app_utils
        def flatten_dict(
            d: dict, prefix: Optional[Any] = "", result: Optional[Any] = None
        ):
            """
            Simple recursive function to flatten a dictionary

            :param dict d: The dictionary to flatten
            :param Optional[Any] prefix: Prefix, defaults to ""
            :param Optional[Any] result: Result, defaults to None
            :return: List of flattened dictionaries
            :rtype: list
            """
            if result is None:
                result = []
            if isinstance(d, dict):
                for key, value in d.items():
                    if isinstance(value, dict):
                        flatten_dict(value, f"{prefix}{key}.", result)
                    elif isinstance(value, list):
                        for dat in value:
                            flatten_dict(dat, f"{prefix}{key}.", result)
                    else:
                        if value:
                            result.append((f"{prefix}{key}", value))
            return result

        props = []
        wiz_dict = json.loads(wiz_data)
        result = flatten_dict(wiz_dict)
        for k, v in result:
            if v:
                if isinstance(v, list):
                    v = v.pop()
                if isinstance(v, dict):
                    v = flatten_dict(v).pop()[1]
                prop = {
                    "createdById": app.config["userId"],
                    "dateCreated": get_current_datetime(),
                    "lastUpdatedById": app.config["userId"],
                    "isPublic": True,
                    "alt_id": wiz_id,
                    "key": k,
                    "value": v,
                    "parentId": 0,
                    "parentModule": "assets",
                    "dateLastUpdated": get_current_datetime(),
                }
                props.append(Property(**prop))

        return [prop for prop in props if prop.value != "{}"]
