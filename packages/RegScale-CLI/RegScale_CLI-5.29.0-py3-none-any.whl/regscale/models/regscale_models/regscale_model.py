#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Base Regscale Model """
import copy
import json
import logging
from abc import ABC
from typing import List, TypeVar, Optional, Union, cast, Dict, Any, ClassVar

from pydantic import BaseModel, Field, ConfigDict

from regscale.core.app.utils.api_handler import (
    APIHandler,
    APIInsertionError,
    APIUpdateError,
)

T = TypeVar("T", bound="RegScaleModel")

logger = logging.getLogger("rich")


class RegScaleModel(BaseModel, ABC):
    """Mixin class for RegScale Models to add functionality to interact with RegScale API"""

    model_config = ConfigDict(use_enum_values=True)
    _module_slug = "model_slug"
    _module_string = ""
    _module_slug_id_url = "/api/{model_slug}/{id}"
    _module_id = 0
    _api_handler: ClassVar[APIHandler] = APIHandler()
    _unique_fields: list[str] = []

    extra_data: dict = Field(default={}, exclude=True)
    createdById: Optional[str] = None
    lastUpdatedById: Optional[str] = None

    def __init__(self, *args, **data):
        try:
            super().__init__(*args, **data)
        except Exception as e:
            logger.error(f"Error creating {self.__class__.__name__}: {e} {data}")

    def dict(self, **kwargs) -> dict[str, Any]:
        """
        Override the default dict method to exclude hidden fields

        :param kwargs: kwargs
        :return: dict[str, Any]
        """
        hidden_fields = set(
            attribute_name
            for attribute_name, model_field in self.model_fields.items()
            if model_field.from_field("hidden") == "hidden"
        )
        kwargs.setdefault("exclude", hidden_fields)
        return super().model_dump(**kwargs)

    @classmethod
    def get_module_id(cls) -> int:
        """
        Get the module ID for the model.

        :return: Module ID #
        :rtype: int
        """
        return cls._module_id.default

    @classmethod
    def get_module_slug(cls) -> str:
        """
        Get the module slug for the model.

        :return: Module slug
        :rtype: str
        """
        return cls._module_slug.default

    @classmethod
    def get_module_string(cls) -> str:
        """
        Get the module name for the model.

        :return: Module name
        :rtype: str
        """
        return cls._module_string.default or cls.get_module_slug()

    @classmethod
    def _get_endpoints(cls) -> ConfigDict:
        """
        Get the endpoints for the API.

        :return: A dictionary of endpoints
        :rtype: ConfigDict
        """
        endpoints = ConfigDict(  # type: ignore
            get=cls._module_slug_id_url.default,
            insert="/api/{model_slug}/",
            update=cls._module_slug_id_url.default,
            delete=cls._module_slug_id_url.default,
            list="/api/{model_slug}/getList",
            get_all_by_parent="/api/{model_slug}/getAllByParent/{intParentID}/{strModule}",
        )
        endpoints.update(cls._get_additional_endpoints())
        return endpoints

    def __repr__(self) -> str:
        """
        Override the default repr method to return a string representation of the object.

        :return: String representation of the object
        :rtype: str
        """
        return f"<{self.__str__()}>"

    def __str__(self) -> str:
        """
        Override the default str method to return a string representation of the object.

        :return: String representation of the object
        :rtype: str
        """
        fields = (
            "\n  "
            + "\n  ".join(
                f"{name}={value!r},"
                for name, value in self.dict().items()
                # if value is not None
            )
            + "\n"
        )
        return f"{self.__class__.__name__}({fields})"

    def find_by_unique(self) -> Optional[T]:
        """
        Find a unique instance of the object.

        :raises NotImplementedError: If the method is not implemented
        :return: The instance or None if not found
        :rtype: Optional[T]
        """
        if not self._unique_fields:
            raise NotImplementedError(
                f"_unique_fields not defined for {self.__class__.__name__}"
            )

        if not (parent_control_id := getattr(self, "parentControlId", None)):
            raise NotImplementedError(
                f"parentControlId not defined for {self.__class__.__name__}"
            )

        for instance in self.get_by_parent(
            parent_id=parent_control_id, parent_module=""
        ):
            if all(
                getattr(instance, field) == getattr(self, field)
                for field in self._unique_fields
            ):
                return instance
        return None

    def get_or_create(self: T) -> T:
        """
        Get or create an instance.

        :return: The instance
        :rtype: T
        """
        functional_role = self.find_by_unique()
        if functional_role:
            return functional_role
        else:
            return self.create()

    def create_or_update(self):
        """
        Create or update a functional role.

        :return: The functional role
        :rtype: FunctionalRole
        """
        functional_role = self.find_by_unique()
        if functional_role:
            # Update the functional role
            self.id = functional_role.id  # noqa
            return self.save()
        else:
            return self.create()

    @classmethod
    def _handle_list_response(cls, response) -> List[T]:
        if not response or response.status_code in [204, 404]:
            return []
        if response.ok:
            json_response = response.json()
            if isinstance(json_response, dict):
                json_response = json_response.get("items", [])
            return cast(List[T], [cls(**o) for o in json_response])
        else:
            logger.error(f"Failed to get {cls.get_module_slug()} for {cls.__name__}")
            return []

    @classmethod
    def get_by_parent(cls, parent_id: int, parent_module: str) -> List[T]:
        """
        Get a list of objects by parent.

        :param int parent_id: The ID of the parent
        :param str parent_module: The module of the parent
        :return: A list of objects
        :rtype: List[T]
        """
        return cls._handle_list_response(
            cls._api_handler.get(
                endpoint=cls.get_endpoint("get_by_parent").format(
                    intParentID=parent_id,
                    strModule=parent_module,
                )
            )
        )

    @classmethod
    def get_all_by_parent(cls, parent_id: int, parent_module: str) -> List[T]:
        """
        Get a list of objects by parent.

        :param int parent_id: The ID of the parent
        :param str parent_module: The module of the parent
        :return: A list of objects
        :rtype: List[T]
        """
        return cls._handle_list_response(
            cls._api_handler.get(
                endpoint=cls.get_endpoint("get_all_by_parent").format(
                    intParentID=parent_id,
                    strModule=parent_module,
                )
            )
        )

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the API.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict()

    @classmethod
    def get_endpoint(cls, endpoint_type: str) -> str:
        """
        Get the endpoint for a specific type.

        :param str endpoint_type: The type of endpoint
        :raises ValueError: If the endpoint type is not found
        :return: The endpoint
        :rtype: str
        """
        endpoint = cls._get_endpoints().get(endpoint_type, "na")
        if not endpoint or endpoint == "na":
            logger.error(f"{cls.__name__} does not have endpoint {endpoint_type}")
            raise ValueError(f"Endpoint {endpoint_type} not found")
        endpoint = str(endpoint).replace("{model_slug}", cls.get_module_slug())
        return endpoint

    def create(self: T) -> T:
        """
        Insert a RegScale object.

        :raises APIInsertionError: If the insert fails
        :return: The created object
        :rtype: T
        """
        response = self._api_handler.post(
            endpoint=self.get_endpoint("insert"), data=self.dict()
        )
        if response and response.ok:
            return self.__class__(**response.json())
        else:
            logger.error(f"Failed to insert {self.__class__.__name__} {self.dict()}")
            if response and not response.ok:
                logger.error(
                    f"Response Error: Code #{response.status_code}: {response.reason}\n{response.text}"
                )
            if response is None:
                error_msg = "Response was None"
                logger.error(error_msg)
                raise APIInsertionError(error_msg)
            error_msg = f"Response Code: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise APIInsertionError(error_msg)

    def save(self: T) -> T:
        """
        Save changes of the model instance.

        :raises APIUpdateError: If the update fails
        :return: The updated object
        :rtype: T
        """
        response = self._api_handler.put(
            endpoint=self.get_endpoint("update").format(id=self.id), data=self.dict()
        )
        if hasattr(response, "ok") and response.ok:
            return self.__class__(**response.json())
        else:
            logger.error(f"Failed to update {self.__class__.__name__} {self.dict()}")
            if response is not None:
                raise APIUpdateError(
                    f"Response Code: {response.status_code} - {response.text}"
                )
            else:
                raise APIUpdateError("Response was None")

    @classmethod
    def get_object(cls, object_id: Union[str, int]) -> Optional[T]:
        """
        Get a RegScale object by ID.

        :param Union[str, int] object_id: The ID of the object
        :return: The object or None if not found
        :rtype: Optional[T]
        """
        response = cls._api_handler.get(
            endpoint=cls.get_endpoint("get").format(id=object_id)
        )
        if response and response.ok:
            logger.debug(json.dumps(response.json(), indent=4))
            if response.json() and isinstance(response.json(), list):
                return cast(T, cls(**response.json()[0]))
            else:
                return cast(T, cls(**response.json()))
        else:
            logger.debug(
                f"Failing response: {response.status_code}: {response.reason} {response.text}"
            )
            logger.error(f"Failed to get record {cls.__name__} {object_id}")
            return None

    @classmethod
    def get_list(cls) -> List[T]:
        """
        Get a list of objects.

        :return: A list of objects
        :rtype: List[T]
        """
        response = cls._api_handler.get(endpoint=cls.get_endpoint("list"))
        if response.ok:
            return cast(
                List[T], [cls.get_object(object_id=sp["id"]) for sp in response.json()]
            )
        else:
            logger.error(f"Failed to get list of {cls.__name__} {response}")
            return []

    def delete(self) -> bool:
        """
        Delete an object in RegScale.

        :return: True if successful, False otherwise
        :rtype: bool
        """
        response = self._api_handler.delete(
            endpoint=self.get_endpoint("delete").format(id=self.id)
        )
        if response.ok:
            return True
        else:
            logger.error(f"Failed to delete {self.__class__.__name__} {self.dict()}")
            return False

    @classmethod
    def from_dict(cls, obj: Dict[str, Any], copy_object: bool = False) -> T:  # type: ignore
        """
        Create RegScale Model from dictionary

        :param Dict[str, Any] obj: dictionary
        :param bool copy_object: Whether to copy the object without an id, defaults to False
        :return: Instance of RegScale Model
        :rtype: T
        """
        copy_obj = copy.copy(obj)
        if "id" in copy_obj and copy_object:
            del copy_obj["id"]
        return cast(T, cls(**copy_obj))
