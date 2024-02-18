#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Class for a Wiz.io integration """

# standard python imports
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from datetime import datetime


class AssetCategory(Enum):
    """Map Wiz assetTypes with RegScale assetCategories"""

    SERVICE_USAGE_TECHNOLOGY = "Software"
    GATEWAY = "Software"
    SECRET = "Software"
    BUCKET = "Software"
    WEB_SERVICE = "Software"
    DB_SERVER = "Hardware"
    LOAD_BALANCER = "Software"
    CLOUD_ORGANIZATION = "Software"
    SUBNET = "Software"
    VIRTUAL_MACHINE = "Hardware"
    TECHNOLOGY = "Software"
    SECRET_CONTAINER = "Software"
    FILE_SYSTEM_SERVICE = "Software"
    KUBERNETES_CLUSTER = "Software"
    ROUTE_TABLE = "Software"
    COMPUTE_INSTANCE_GROUP = "Software"
    HOSTED_TECHNOLOGY = "Software"
    USER_ACCOUNT = "Software"
    DNS_ZONE = "Software"
    VOLUME = "Software"
    SERVICE_ACCOUNT = "Software"
    RESOURCE_GROUP = "Software"
    ACCESS_ROLE = "Software"
    SUBSCRIPTION = "Software"
    SERVICE_CONFIGURATION = "Software"
    VIRTUAL_NETWORK = "Software"
    VIRTUAL_MACHINE_IMAGE = "Software"
    FIREWALL = "Hardware"
    DATABASE = "Software"
    GOVERNANCE_POLICY_GROUP = "Software"
    STORAGE_ACCOUNT = "Software"
    CONFIG_MAP = "Software"
    NETWORK_ADDRESS = "Software"
    NETWORK_INTERFACE = "Software"
    DAEMON_SET = "Software"
    PRIVATE_ENDPOINT = "Software"
    ENDPOINT = "Software"
    DEPLOYMENT = "Software"
    POD = "Software"
    KUBERNETES_STORAGE_CLASS = "Software"
    ACCESS_ROLE_BINDING = "Software"
    KUBERNETES_INGRESS = "Software"
    CONTAINER = "Software"
    CONTAINER_IMAGE = "Software"
    CONTAINER_REGISTRY = "Software"
    GOVERNANCE_POLICY = "Software"
    REPLICA_SET = "Software"
    KUBERNETES_SERVICE = "Software"
    KUBERNETES_PERSISTENT_VOLUME_CLAIM = "Software"
    KUBERNETES_PERSISTENT_VOLUME = "Software"
    KUBERNETES_NETWORK_POLICY = "Software"
    KUBERNETES_NODE = "Software"


class ComplianceCheckStatus(Enum):
    PASS = "Pass"
    FAIL = "Fail"


class ComplianceReport(BaseModel):
    resource_name: str = Field(..., alias="Resource Name")
    cloud_provider_id: str = Field(..., alias="Cloud Provider ID")
    object_type: str = Field(..., alias="Object Type")
    native_type: str = Field(..., alias="Native Type")
    tags: Optional[str] = Field(None, alias="Tags")
    subscription: str = Field(..., alias="Subscription")
    projects: Optional[str] = Field(None, alias="Projects")
    cloud_provider: str = Field(..., alias="Cloud Provider")
    policy_id: str = Field(..., alias="Policy ID")
    policy_short_name: str = Field(..., alias="Policy Short Name")
    policy_description: Optional[str] = Field(None, alias="Policy Description")
    policy_category: Optional[str] = Field(None, alias="Policy Category")
    control_id: Optional[str] = Field(None, alias="Control ID")
    compliance_check: Optional[str] = Field(
        None, alias="Compliance Check Name (Wiz Subcategory)"
    )
    control_description: Optional[str] = Field(None, alias="Control Description")
    severity: Optional[str] = Field(None, alias="Severity")
    result: str = Field(..., alias="Result")
    framework: Optional[str] = Field(None, alias="Framework")
    remediation_steps: Optional[str] = Field(None, alias="Remediation Steps")
    assessed_at: Optional[datetime] = Field(None, alias="Assessed At")
    created_at: Optional[datetime] = Field(None, alias="Created At")
    updated_at: Optional[datetime] = Field(None, alias="Updated At")
    subscription_name: Optional[str] = Field(None, alias="Subscription Name")
    subscription_provider_id: Optional[str] = Field(
        None, alias="Subscription Provider ID"
    )
    resource_id: str = Field(..., alias="Resource ID")
    resource_region: Optional[str] = Field(None, alias="Resource Region")
    resource_cloud_platform: Optional[str] = Field(
        None, alias="Resource Cloud Platform"
    )


# # Attempt to create an instance of the model again
# example_row = data.iloc[0].to_dict()
# example_compliance_report = ComplianceReport(**example_row)
#
# # Display the instance
# example_compliance_report.dict()
