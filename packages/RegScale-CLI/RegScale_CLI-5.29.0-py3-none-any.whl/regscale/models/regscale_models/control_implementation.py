#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Model for a RegScale Security Control Implementation """
# standard python imports
import logging
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Callable
from urllib.parse import urljoin

import requests
from lxml.etree import Element
from pydantic import ConfigDict

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import get_current_datetime, remove_keys
from regscale.models.regscale_models.control import Control
from regscale.models.regscale_models.regscale_model import RegScaleModel

logger = logging.getLogger("rich")
PATCH_CONTENT_TYPE = "application/json-patch+json"


class ControlImplementationStatus(Enum):
    """Control Implementation Status"""

    FullyImplemented = "Fully Implemented"
    NotImplemented = "Not Implemented"
    PartiallyImplemented = "Partially Implemented"
    InRemediation = "In Remediation"
    Inherited = "Inherited"
    NA = "Not Applicable"
    Planned = "Planned"
    Archived = "Archived"
    RiskAccepted = "Risk Accepted"


class ControlImplementation(RegScaleModel):
    """Control Implementation"""

    _module_slug = "controlImplementation"
    _module_string = "controls"

    controlOwnerId: str  # Required
    status: str  # Required
    controlID: int  # Required
    id: Optional[int] = 0
    parentId: Optional[int] = None
    parentModule: Optional[str] = None
    control: Optional[Control] = None
    createdById: Optional[str] = None
    uuid: Optional[str] = None
    policy: Optional[str] = None
    implementation: Optional[str] = None
    dateLastAssessed: Optional[str] = None
    lastAssessmentResult: Optional[str] = None
    practiceLevel: Optional[str] = None
    processLevel: Optional[str] = None
    cyberFunction: Optional[str] = None
    implementationType: Optional[str] = None
    implementationMethod: Optional[str] = None
    qdWellDesigned: Optional[str] = None
    qdProcedures: Optional[str] = None
    qdSegregation: Optional[str] = None
    qdFlowdown: Optional[str] = None
    qdAutomated: Optional[str] = None
    qdOverall: Optional[str] = None
    qiResources: Optional[str] = None
    qiMaturity: Optional[str] = None
    qiReporting: Optional[str] = None
    qiVendorCompliance: Optional[str] = None
    qiIssues: Optional[str] = None
    qiOverall: Optional[str] = None
    responsibility: Optional[str] = None
    inheritedControlId: Optional[int] = None
    inheritedRequirementId: Optional[int] = None
    inheritedSecurityPlanId: Optional[int] = None
    inheritedPolicyId: Optional[int] = None
    dateCreated: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    dateLastUpdated: Optional[str] = None
    weight: Optional[int] = None
    isPublic: Optional[bool] = True
    inheritable: Optional[bool] = False
    systemRoleId: Optional[int] = None
    plannedImplementationDate: Optional[str] = None
    stepsToImplement: Optional[str] = None

    @classmethod
    def _get_additional_endpoints(cls) -> ConfigDict:
        """
        Get additional endpoints for the API.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_all_count="/api/{model_slug}/getAllCount",
            get_filtered_list="/api/{model_slug}/getFilteredList/{str_find}",
            get_all_by_plan="/api/{model_slug}/getAllByPlan/{int_security_plan}",
            get_all_by_plan_with_controls="/api/{model_slug}/getAllByPlanWithControls/{int_security_plan}",
            get_compliance_history_by_plan="/api/{model_slug}/GetComplianceHistoryByPlan/{int_parent}/{str_module}",
            save_compliance_history_by_plan="/api/{model_slug}/SaveComplianceHistoryByPlan",
            get_all_by_plan_with_objectives="/api/{model_slug}/getAllByPlanWithObjectives/{int_security_plan}",
            get_all_by_component_list="/api/{model_slug}/getAllByComponentList",
            get_mappings_by_security_plan="/api/{model_slug}/getMappingsBySecurityPlan/{int_security_plan}",
            get_list_by_plan="/api/{model_slug}/getListByPlan/{int_security_plan}",
            get_list_by_parent="/api/{model_slug}/getListByParent/{int_id}/{str_module}",
            get_master_assessment_list="/api/{model_slug}/getMasterAssessmentList/{int_parent}/{str_module}",
            get_list_by_parent_control="/api/{model_slug}/getListByParentControl/{parent_control_id}",
            get_sc_list_by_plan="/api/{model_slug}/getSCListByPlan/{int_security_plan}",
            get_inheritance_list_by_plan="/api/{model_slug}/getInheritanceListByPlan/{int_security_plan}",
            get_sc_list_by_component="/api/{model_slug}/getSCListByComponent/{int_component}",
            graph_main_dashboard="/api/{model_slug}/graphMainDashboard/{str_group_by}/{str_mod}",
            export="/api/{model_slug}/export/{int_id}",
            wizard="/api/{model_slug}/wizard/{int_id}/{str_module}",
            get_date_last_assessed_by_parent="/api/{model_slug}/getDateLastAssessedByParent/{int_record}",
            get_date_last_assessed_by_parent_and_module="/api/{model_slug}/getDateLastAssessedByParentAndModule/{str_module}/{int_record}",
            get_date_last_assessed_for_all_assets="/api/{model_slug}/getDateLastAssessedForAllAssets/{int_record}",
            graph_controls_by_date="/api/{model_slug}/graphControlsByDate/{year}",
            get_date_last_assessed_by_control="/api/{model_slug}/getDateLastAssessedByControl/{int_control}",
            get_by_status_and_parent="/api/{model_slug}/getByStatusAndParent/{int_id}",
            get_by_status_and_parent_control="/api/{model_slug}/getByStatusAndParentControl/{int_id}",
            get_by_owner_and_parent="/api/{model_slug}/getByOwnerAndParent/{int_id}",
            get_by_owner_and_parent_control="/api/{model_slug}/getByOwnerAndParentControl/{int_id}",
            get_by_result_and_parent="/api/{model_slug}/getByResultAndParent/{int_id}",
            get_by_result_and_parent_control="/api/{model_slug}/getByResultAndParentControl/{int_id}",
            get_by_process_and_parent="/api/{model_slug}/getByProcessAndParent/{int_id}",
            get_by_practice_and_parent="/api/{model_slug}/getByPracticeAndParent/{int_id}",
            get_by_practice_and_control="/api/{model_slug}/getByPracticeAndControl/{int_id}",
            get_by_process_and_control="/api/{model_slug}/getByProcessAndControl/{int_id}",
            graph="/api/{model_slug}/graph",
            filter_control_implementations="/api/{model_slug}/filterControlImplementations",
            filter_scorecard="/api/{model_slug}/filterScorecard",
            scorecard_count="/api/{model_slug}/ScorecardCount",
            query_by_custom_field="/api/{model_slug}/queryByCustomField/{str_field_name}/{str_value}",
            insert="/api/controlImplementation",
            batch_create="/api/{model_slug}/batchCreate",
            batch_update="/api/{model_slug}/batchUpdate",
            update=cls.module_slug_id_url,
            delete=cls.module_slug_id_url,
            get=cls.module_slug_id_url,
            quick_update="/api/{model_slug}/quickUpdate/{id}/{str_status}/{int_weight}/{str_user}",
            dashboard_by_parent="/api/{model_slug}/dashboardByParent/{str_group_by}/{int_id}/{str_module}",
            security_control_dashboard="/api/{model_slug}/securityControlDashboard/{str_group_by}/{int_id}",
            dashboard_by_parent_and_catalogue="/api/{model_slug}/dashboardByParentAndCatalogue/{str_group_by}/{int_id}/{int_cat_id}",
            group_by_family="/api/{model_slug}/groupByFamily/{int_security_plan}",
            dashboard_by_sp="/api/{model_slug}/dashboardBySP/{str_group_by}/{int_security_plan}",
            report="/api/{model_slug}/report/{str_report}",
            get_by_parent="/api/{model_slug}/getByParent/{int_id}/{str_module}",
            get_count_by_parent="/api/{model_slug}/getCountByParent/{int_id}/{str_module}",
            get_all_asset_controls_by_component="/api/{model_slug}/getAllAssetControlsByComponent/{int_id}",
            drilldown_asset_controls_by_component="/api/{model_slug}/drilldownAssetControlsByComponent/{component_id}/{str_field}/{str_value}",
            get_control_context="/api/{model_slug}/getControlContext/{int_control_id}/{int_parent_id}/{str_module}",
        )

    # TODO: A record can be saved without a status, but not updated without a status.
    @classmethod
    def get_object(
        cls, object_id: Union[str, int]
    ) -> Optional["ControlImplementation"]:  # type ignore
        """
        Get an object by ID.

        :param Union[str, int] object_id: The ID of the object
        :return: The object or None if not found
        :rtype: Optional[ControlImplementation]
        """
        response = cls._api_handler.get(endpoint=cls.get_endpoint("get").format(id=id))
        if response and response.ok:
            response_json = response.json()
            response_json["status"] = (
                response_json.get("status", None)
                or ControlImplementationStatus.NotImplemented.value
            )
            return cls(**response_json)
        else:
            logger.error(f"Failed to get record {cls.__name__} {id}")
            return None

    def find_by_unique(self) -> Optional["ControlImplementation"]:
        """
        Find an object by unique query.

        :return: The object or None if not found
        :rtype: Optional[ControlImplementation]
        """

        for instance in self.get_by_security_control_id(
            security_control_id=self.controlID
        ):
            return instance
        return None

    @classmethod
    def get_by_security_control_id(
        cls, security_control_id: int
    ) -> List["ControlImplementation"]:
        """
        Get a list of control implementations by security control ID.

        :param int security_control_id: The ID of the security control
        :return: A list of control implementations
        :rtype: List[ControlImplementation]
        """
        response = cls._api_handler.get(
            endpoint=cls.get_endpoint("get_by_security_control_id").format(
                int_security_plan=security_control_id
            )
        )
        security_controls = []
        if response and response.ok:
            for ci in response.json():
                if ci := cls.get_object(object_id=ci["id"]):
                    security_controls.append(ci)
        return security_controls

    @classmethod
    def get_list_by_plan(cls, plan_id: int) -> List["ControlImplementation"]:
        """
        Get a list of control implementations by plan ID.

        :param int plan_id: The ID of the plan
        :return: A list of control implementations
        :rtype: List[ControlImplementation]
        """
        response = cls.api_handler.get(
            endpoint=cls.get_endpoint("get_list_by_plan").format(
                intSecurityPlan=plan_id
            )
        )
        security_controls = []
        if response and response.ok:
            for ci in response.json():
                if ci := cls.get_object(object_id=ci["id"]):
                    security_controls.append(ci)
        return security_controls

    @classmethod
    def get_control_map_by_plan(cls, plan_id: int) -> Dict[str, int]:
        """
        Get a map of control implementations by plan ID.

        :param int plan_id: The ID of the plan
        :return: A dictionary mapping control IDs to implementation IDs
        :rtype: Dict[str, int]
        """
        response = cls.api_handler.get(
            endpoint=cls.get_endpoint("get_all_by_plan_with_controls").format(
                int_security_plan=plan_id
            )
        )
        if response and response.ok:
            return {ci["control"]["controlId"]: ci["id"] for ci in response.json()}
        return {}

    @staticmethod
    def post_implementation(
        app: Application, implementation: "ControlImplementation"
    ) -> Union[requests.Response, Dict]:
        """
        Post a control implementation to RegScale via API

        :param Application app:
        :param ControlImplementation implementation:
        :return: Response from RegScale API or the response if the response is not ok
        :rtype: Union[requests.Response, Dict]
        """
        api = Api()
        headers = {
            "accept": "*/*",
            "Authorization": app.config["token"],
            "Content-Type": PATCH_CONTENT_TYPE,
        }

        res = api.post(
            app.config["domain"] + "/api/controlimplementation",
            headers=headers,
            data=implementation.dict(),
        )
        if not res.raise_for_status() and res.status_code == 200:
            return res.json()
        else:
            return res

    @staticmethod
    def update(
        app: Application, implementation: "ControlImplementation"
    ) -> Union[requests.Response, Dict]:
        """
        Update Method for ControlImplementation

        :param Application app: Application instance
        :param ControlImplementation implementation: ControlImplementation instance
        :return: A control implementation dict or a response object
        :rtype: Union[requests.Response, Dict]
        """
        api = Api()

        res = api.put(
            app.config["domain"] + f"/api/controlimplementation/{implementation.id}",
            json=implementation.dict(),
        )
        if not res.raise_for_status() and res.status_code == 200:
            return res.json()
        else:
            return res

    @staticmethod
    def fetch_existing_implementations(
        app: Application, regscale_parent_id: int, regscale_module: str
    ) -> List[Dict]:
        """
        Fetch existing implementations for the provided id and module from RegScale

        :param Application app: Application instance
        :param int regscale_parent_id: RegScale Parent ID
        :param str regscale_module: RegScale Parent Module
        :return: list of existing implementations
        :rtype: List[Dict]
        """
        api = Api()
        existing_implementations = []
        existing_implementations_response = api.get(
            url=app.config["domain"]
            + "/api/controlimplementation"
            + f"/getAllByParent/{regscale_parent_id}/{regscale_module}"
        )
        if existing_implementations_response.ok:
            existing_implementations = existing_implementations_response.json()
        return existing_implementations

    @staticmethod
    def _extract_text_and_log(element, debug_logger) -> Optional[str]:
        """
        Extracts and logs text from an XML element.

        :param element: The XML element.
        :param debug_logger: Logger for debugging.
        :return: Stripped text from the element.
        :rtype: Optional[str]
        """
        text = element.text.strip() if element.text else None
        if text:
            debug_logger.debug("Text: %s", text)
        return text

    @staticmethod
    def _update_implementation_status(element, imp) -> None:
        """
        Updates the implementation status of the control based on the element.

        :param element: The XML element.
        :param imp: The control implementation instance.
        :return: None
        """
        if (
            "name" in element.attrib
            and element.attrib["name"] == "implementation-status"
        ):
            imp.status = (
                "Fully Implemented"
                if element.attrib.get("value") == "implemented"
                else "Not Implemented"
            )

    @staticmethod
    def from_oscal_element(
        app: Application, obj: Element, control: dict
    ) -> "ControlImplementation":
        """
        Create RegScale ControlImplementation from XML element.

        :param Application app: RegScale CLI Application object.
        :param Element obj: Element object.
        :param dict control: Control dictionary.
        :return: ControlImplementation class.
        :rtype: ControlImplementation.
        """
        user = app.config["userId"]
        imp = ControlImplementation(
            controlOwnerId=user, status="notimplemented", controlID=control["id"]
        )

        for element in obj.iter():
            ControlImplementation._extract_text_and_log(element, logger)
            logger.debug("Element: %s", element.tag)
            imp.control = control["controlId"]
            for name, value in element.attrib.items():
                logger.debug(f"Property: {name}, Value: {value}")
                ControlImplementation._update_implementation_status(element, imp)

        return imp

    @staticmethod
    def from_dict(obj: Any) -> "ControlImplementation":
        """
        Create ControlImplementation from dictionary

        :param Any obj: Object to create ControlImplementation from
        :return: ControlImplementation class
        :rtype: ControlImplementation
        """
        if "id" in obj:
            del obj["id"]
        return ControlImplementation(**obj)

    def __hash__(self) -> int:
        """
        Hash function for ControlImplementation

        :return: Hash of ControlImplementation
        :rtype: int
        """
        return hash(
            (
                self.controlID,
                self.controlOwnerId,
                self.status,
            )
        )

    @staticmethod
    def stringify_children(node) -> str:
        """
        Converts XML node to string

        :param node: Node to convert to string
        :return: String representation of node
        :rtype: str
        """
        from itertools import chain

        from lxml.etree import tostring

        parts = (
            [node.text]
            + list(chain(*([c.text, tostring(c), c.tail] for c in node.getchildren())))
            + [node.tail]
        )
        # filter removes possible Nones in texts and tails
        return "".join(filter(None, parts))

    @staticmethod
    def post_batch_implementation(
        app: Application, implementations: List[Dict]
    ) -> Optional[Union[requests.Response, Dict]]:
        """
        Post a batch of control implementations to the RegScale API

        :param Application app: RegScale CLI Application object
        :param List[Dict] implementations: list of control implementations to post to RegScale
        :return: Response from RegScale API or the response content if the response is not ok
        :rtype: Optional[Union[requests.Response, Dict]]
        """
        if len(implementations) > 0:
            api = Api()
            headers = {
                "accept": "*/*",
                "Authorization": app.config["token"],
                "Content-Type": PATCH_CONTENT_TYPE,
            }
            res = api.post(
                url=urljoin(
                    app.config["domain"], "/api/controlImplementation/batchCreate"
                ),
                json=implementations,
                headers=headers,
            )
            if not res.raise_for_status() and res.status_code == 200:
                app.logger.info(
                    f"Created {len(implementations)} Control Implementations, Successfully!"
                )
                return res.json()
            else:
                return res

    @staticmethod
    def put_batch_implementation(
        app: Application, implementations: List[Dict]
    ) -> Optional[Union[requests.Response, Dict]]:
        """
        Put a batch of control implementations to the RegScale API

        :param Application app: RegScale CLI Application object
        :param List[Dict] implementations: list of control implementations to post to RegScale
        :return: Response from RegScale API or the response content if the response is not ok
        :rtype: Optional[Union[requests.Response, Dict]]
        """
        if len(implementations) > 0:
            api = Api()
            headers = {
                "accept": "*/*",
                "Authorization": app.config["token"],
                "Content-Type": PATCH_CONTENT_TYPE,
            }
            res = api.post(
                url=urljoin(
                    app.config["domain"], "/api/controlImplementation/batchUpdate"
                ),
                json=implementations,
                headers=headers,
            )
            if not res.raise_for_status() and res.status_code == 200:
                app.logger.info(
                    f"Updated {len(implementations)} Control Implementations, Successfully!"
                )
                return res.json()
            else:
                return res

    @staticmethod
    def get_existing_control_implementations(parent_id: int) -> Dict:
        """
        Fetch existing control implementations as dict with control id as the key used for
        automating control implementation creation

        :param int parent_id: parent control id
        :return: Dictionary of existing control implementations
        :rtype: Dict
        """
        app = Application()
        api = Api()
        domain = app.config.get("domain")
        existing_implementation_dict = {}
        get_url = urljoin(
            domain, f"/api/controlImplementation/getAllByPlan/{parent_id}"
        )
        response = api.get(get_url)
        if response.ok:
            existing_control_implementations_json = response.json()
            for cim in existing_control_implementations_json:
                existing_implementation_dict[cim.get("controlName")] = cim
            logger.info(
                f"Found {len(existing_implementation_dict)} existing control implementations"
            )
        elif response.status_code == 404:
            logger.info(f"No existing control implementations found for {parent_id}")
        else:
            logger.warning(
                f"Unable to get existing control implementations. {response.content}"
            )
        return existing_implementation_dict

    @classmethod
    def create_control_implementations(
        cls,
        controls: list,
        parent_id: int,
        parent_module: str,
        existing_implementation_dict: dict,
        full_controls: dict,
        partial_controls: dict,
        failing_controls: dict,
        include_not_implemented: Optional[bool] = False,
    ) -> None:
        """
        Creates and updates control implementations based on given controls

        :param list controls: List of control details
        :param int parent_id: Identifier for the parent control
        :param str parent_module: Name of the parent module
        :param dict existing_implementation_dict: Dictionary of existing implementations
        :param dict full_controls: Dictionary of fully implemented controls
        :param dict partial_controls: Dictionary of partially implemented controls
        :param dict failing_controls: Dictionary of failing controls
        :param Optional[bool] include_not_implemented: Whether to include not implemented controls, defaults to False
        :return: None
        """
        app = Application()
        user_id = app.config.get("userId")

        to_create, to_update = cls.process_controls(
            controls,
            parent_id,
            parent_module,
            existing_implementation_dict,
            full_controls,
            partial_controls,
            failing_controls,
            user_id,
            include_not_implemented,
        )

        cls.post_batch_if_needed(
            app, to_create, ControlImplementation.post_batch_implementation
        )
        cls.put_batch_if_needed(
            app, to_update, ControlImplementation.put_batch_implementation
        )

    @classmethod
    def process_controls(
        cls,
        controls: list,
        parent_id: int,
        parent_module: str,
        existing_implementation_dict: dict,
        full_controls: dict,
        partial_controls: dict,
        failing_controls: dict,
        user_id: Optional[str] = None,
        include_not_implemented: Optional[bool] = False,
    ) -> tuple[list, list]:
        """
        Processes each control for creation or update

        :param list controls: List of control details
        :param int parent_id: Identifier for the parent control
        :param str parent_module: Name of the parent module
        :param dict existing_implementation_dict: Dictionary of existing implementations
        :param dict full_controls: Dictionary of fully implemented controls
        :param dict partial_controls: Dictionary of partially implemented controls
        :param dict failing_controls: Dictionary of failing controls
        :param Optional[str] user_id: ID of the user performing the operation, defaults to None
        :param Optional[bool] include_not_implemented: Whether to include not implemented controls, defaults to False
        :return: Tuple containing lists of controls to create and update
        :rtype: tuple[list, list]
        """
        to_create = []
        to_update = []

        for control in controls:
            lower_case_control_id = control["controlId"].lower()
            status = cls.check_implementation(
                full_controls, partial_controls, failing_controls, lower_case_control_id
            )
            if (
                not include_not_implemented
                and status == ControlImplementationStatus.NotImplemented.value
            ):
                continue
            if control["controlId"] not in existing_implementation_dict:
                cim = cls.create_new_control_implementation(
                    control, parent_id, parent_module, status, user_id
                )
                to_create.append(cim)
            else:
                cls.update_existing_control_implementation(
                    control, existing_implementation_dict, status, to_update, user_id
                )

        return to_create, to_update

    @staticmethod
    def create_new_control_implementation(
        control: dict,
        parent_id: int,
        parent_module: str,
        status: str,
        user_id: Optional[str] = None,
    ) -> "ControlImplementation":
        """
        Creates a new control implementation object

        :param dict control: Control details
        :param int parent_id: Identifier for the parent control
        :param str parent_module: Name of the parent module
        :param str status: Status of the control implementation
        :param Optional[str] user_id: ID of the user performing the operation, defaults to None
        :return: New control implementation object
        :rtype: ControlImplementation
        """
        cim = ControlImplementation(
            controlOwnerId=user_id,
            dateLastAssessed=get_current_datetime(),
            implementation=control.get("implementation", None),
            status=status,
            controlID=control["id"],
            parentId=parent_id,
            parentModule=parent_module,
            createdById=user_id,
            dateCreated=get_current_datetime(),
            lastUpdatedById=user_id,
            dateLastUpdated=get_current_datetime(),
        ).dict()
        cim["controlSource"] = "Baseline"
        return cim

    @classmethod
    def update_existing_control_implementation(
        cls,
        control: dict,
        existing_implementation_dict: dict,
        status: str,
        to_update: list,
        user_id: Optional[str] = None,
    ):
        """
        Updates an existing control implementation

        :param dict control: Control details
        :param dict existing_implementation_dict: Dictionary of existing implementations
        :param str status: Status of the control implementation
        :param list to_update: List of controls to update
        :param Optional[str] user_id: ID of the user performing the operation, defaults to None
        """
        existing_imp = existing_implementation_dict[control["controlId"]]
        existing_imp.update(
            {
                "implementation": control.get("implementation"),
                "status": status,
                "dateLastAssessed": get_current_datetime(),
                "lastUpdatedById": user_id,
                "dateLastUpdated": get_current_datetime(),
            }
        )

        remove_keys(
            existing_imp, ["createdBy", "systemRole", "controlOwner", "lastUpdatedBy"]
        )

        if existing_imp not in to_update:
            to_update.append(existing_imp)

    @staticmethod
    def post_batch_if_needed(
        app: Application,
        to_create: list,
        post_function: Callable[[Application, list], None],
    ) -> None:
        """
        Posts a batch of new implementations if the list is not empty

        :param Application app: RegScale CLI application object
        :param list to_create: List of new implementations to post
        :param Callable[[Application, list], None] post_function: The function to call for posting the batch, if needed
        :return: None
        """
        if to_create:
            post_function(app, to_create)

    @staticmethod
    def put_batch_if_needed(
        app: Application,
        to_update: list,
        put_function: Callable[[Application, list], None],
    ) -> None:
        """
        Puts a batch of updated implementations if the list is not empty

        :param Application app: RegScale CLI application object
        :param list to_update: List of implementations to update
        :param Callable[[Application, list], None] put_function: The function to call for putting the batch, if needed
        """
        if to_update:
            put_function(app, to_update)

    @staticmethod
    def check_implementation(
        full_controls: dict,
        partial_controls: dict,
        failing_controls: dict,
        control_id: str,
    ) -> str:
        """
        Checks the status of a control implementation

        :param dict full_controls: Dictionary of passing controls
        :param dict partial_controls: Dictionary of partially implemented controls
        :param dict failing_controls: Dictionary of failing control implementations
        :param str control_id: control id
        :return: status of control implementation
        :rtype: str
        """
        if control_id in full_controls.keys():
            logger.debug(f"Found fully implemented control: {control_id}")
            return ControlImplementationStatus.FullyImplemented.value
        elif control_id in partial_controls.keys():
            logger.debug(f"Found partially implemented control: {control_id}")
            return ControlImplementationStatus.PartiallyImplemented.value
        elif control_id in failing_controls.keys():
            logger.debug(f"Found failing control: {control_id}")
            return ControlImplementationStatus.InRemediation.value
        else:
            logger.debug(f"Found not implemented control: {control_id}")
            return ControlImplementationStatus.NotImplemented.value
