#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Model for a RegScale Asset """
import warnings
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from typing import Any, List, Optional, Union
from urllib.parse import urljoin

from pydantic import ConfigDict, Field
from requests import Response
from rich.progress import Progress

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class AssetStatus(str, Enum):
    """Asset Status Enum"""

    Active = "Active (On Network)"
    Inactive = "Off-Network"
    Decommissioned = "Decommissioned"


class AssetCategory(str, Enum):
    """Asset Category Enum"""

    Hardware = "Hardware"
    Software = "Software"


class AssetType(str, Enum):
    """Asset Type Enum"""

    PhysicalServer = "Physical Server"
    VM = "Virtual Machine (VM)"
    Appliance = "Appliance"
    NetworkRouter = "Network Router"
    NetworkSwitch = "Network Switch"
    Firewall = "Firewall"
    Desktop = "Desktop"
    Laptop = "Laptop"
    Tablet = "Tablet"
    Phone = "Phone"
    Other = "Other"


class Asset(RegScaleModel):
    """Asset Model"""

    _module_slug = "assets"
    _unique_fields = ["name"]

    id: int = 0  # Required
    name: str  # Required
    assetType: Union[AssetType, str]  # Required
    status: Union[AssetStatus, str]  # Required
    assetCategory: Union[AssetCategory, str]  # Required
    parentId: int = 0  # Required
    parentModule: str = ""  # Required
    isPublic: bool = True  # Required as Bool
    ram: int = 0  # Required as int
    assetOwnerId: str = "Unknown"  # Required as string
    dateCreated: str = Field(default_factory=get_current_datetime)  # Required as string
    dateLastUpdated: str = Field(
        default_factory=get_current_datetime
    )  # Required as string
    location: Optional[str] = None
    diagramLevel: Optional[str] = None
    cpu: Optional[int] = 0
    description: Optional[str] = None
    diskStorage: Optional[int] = 0
    ipAddress: Optional[str] = None
    macAddress: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    osVersion: Optional[str] = None
    operatingSystem: Optional[str] = None
    otherTrackingNumber: Optional[str] = None
    uuid: Optional[str] = None
    serialNumber: Optional[str] = None
    createdById: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    endOfLifeDate: Optional[str] = None
    purchaseDate: Optional[str] = None
    tenantsId: Optional[int] = None
    facilityId: Optional[int] = None
    orgId: Optional[int] = None
    cmmcAssetType: Optional[str] = None
    wizId: Optional[str] = None
    wizInfo: Optional[str] = None
    assetTagNumber: Optional[str] = None
    baselineConfiguration: Optional[str] = None
    fqdn: Optional[str] = None
    netBIOS: Optional[str] = None
    softwareName: Optional[str] = None
    softwareVendor: Optional[str] = None
    softwareVersion: Optional[str] = None
    vlanId: Optional[str] = None
    bAuthenticatedScan: bool = True
    bPublicFacing: bool = True
    bVirtual: bool = True
    notes: Optional[str] = None
    patchLevel: Optional[str] = None
    softwareFunction: Optional[str] = None
    systemAdministratorId: Optional[str] = None
    bLatestScan: Optional[bool] = None
    managementType: Optional[str] = None
    qualysId: Optional[str] = None
    sicuraId: Optional[Union[str, int]] = None
    tenableId: Optional[str] = None
    firmwareVersion: Optional[str] = None
    purpose: Optional[str] = None
    awsIdentifier: Optional[str] = None
    azureIdentifier: Optional[str] = None
    googleIdentifier: Optional[str] = None
    otherCloudIdentifier: Optional[str] = None
    ipv6Address: Optional[str] = None
    scanningTool: Optional[str] = None
    uri: Optional[str] = None
    bScanDatabase: Optional[bool] = None
    bScanInfrastructure: Optional[bool] = None
    bScanWeb: Optional[bool] = None

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Assets model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            drilldown="/api/{model_slug}/drilldown/{strMonth}/{strCategory}",
            get_count="/api/{model_slug}/getCount",
            graph="/api/{model_slug}/graph",
            graph_by_date="/api/{model_slug}/graphByDate/{strGroupBy}/{year}",
            filter_dashboard="/api/{model_slug}/filterDashboard/{dtStart}/{dtEnd}",
            dashboard="/api/{model_slug}/dashboard/{strGroupBy}",
            dashboard_by_parent="/api/{model_slug}/dashboardByParent/{strGroupBy}/{intId}/{strModule}",
            schedule="/api/{model_slug}/schedule/{year}/{dvar}",
            report="/api/{model_slug}/report/{strReport}",
            filter_assets="/api/{model_slug}/filterAssets",
            query_by_custom_field="/api/{model_slug}/queryByCustomField/{strFieldName}/{strValue}",
        )

    # Legacy code

    @classmethod
    def find_os(cls, os_string: str) -> str:
        """
        Determine the RegScale OS from a string.

        :param str os_string: String containing OS information or description
        :return: RegScale compatible OS string
        :rtype: str
        """
        if "windows" in os_string.lower():
            return "Windows Server"
        elif any(
            sub_string in os_string.lower()
            for sub_string in ["linux", "ubuntu", "debian", "redhat", "suse"]
        ):
            return "Linux"
        elif "mac" in os_string.lower():
            return "Mac OSX"
        else:
            return "Other"

    # 'uniqueness': 'ip, macaddress'
    # Enable object to be hashable
    def __hash__(self):
        """
        Enable object to be hashable

        :return: Hashed TenableAsset
        :rtype: int
        """
        return hash(
            (
                self.name,
                self.ipAddress,
                self.macAddress.lower() if self.macAddress else None,
                self.assetCategory,
                self.assetType,
                self.fqdn,
                self.parentId,
                self.parentModule,
                self.description,
                self.notes,
            )
        )

    def __getitem__(self, key: Any) -> Any:
        """
        Get attribute from Pipeline

        :param Any key: Key to get value of
        :return: value of provided key
        :rtype: Any
        """
        return getattr(self, key)

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set attribute in Pipeline with provided key

        :param Any key: Key to change to provided value
        :param Any value: New value for provided Key
        :return: None
        """
        return setattr(self, key, value)

    def __eq__(self, other: "Asset") -> bool:
        """
        Update items in Asset class

        :param Asset other: Asset object to compare to
        :return: Whether the two assets are equal
        :rtype: bool
        """
        return (
            self.name == other.name
            and self.ipAddress == other.ipAddress
            and self.macAddress == other.macAddress
            and self.wizId == other.wizId
            and self.description == other.description
            and self.notes == other.notes
            and self.status == other.status
            and self.parentId == other.parentId
            and self.otherTrackingNumber == other.otherTrackingNumber
            and self.parentModule == other.parentModule
        )

    @staticmethod
    def insert_asset(
        app: Application,
        obj: Any,
        retry_count: int = 3,
    ) -> Response:
        """
        DEPRECATED: This method is deprecated and will be removed in a future version.
        Use create method to create assets.

        :param Application app: Application Instance
        :param Any obj: Asset Object
        :param int retry_count: Number of times to retry if it fails, defaults to 3
        :return: Response from RegScale after inserting the provided asset object
        :rtype: Response
        """
        import warnings

        warnings.warn(
            "insert_asset is deprecated and will be removed in a future version. Use create method instead.",
            DeprecationWarning,
        )
        url = urljoin(app.config["domain"], "/api/assets")
        if isinstance(obj, Asset):
            obj = obj.dict()
        api = Api()
        res = api.post(url=url, json=obj)
        if not res.ok:
            if res.status_code == 500:
                app.logger.error(
                    "%i: %s\nError creating asset: %s", res.status_code, res.text, obj
                )
            # as long as the status code is not 500, retry
            while res.status_code != 500 and retry_count >= 0:
                app.logger.warning(
                    "Retrying to create asset, attempts remaining: %i", retry_count
                )
                res = api.post(url=url, json=obj)
                retry_count -= 1
                if res.ok:
                    app.logger.info(
                        "[green]Successfully created asset: %s", res.json()["id"]
                    )
                    break
            if retry_count < 0:
                app.logger.error(
                    "%i: %s\n[red]Failed to create asset: %s",
                    res.status_code,
                    res.reason,
                    obj,
                )
        return res

    @staticmethod
    def update_asset(
        app: Application,
        obj: Any,
    ) -> Response:
        """
        DEPRECATED: This method is deprecated and will be removed in a future version.
        Use save method to update assets.

        :param Application app: Application Instance
        :param Any obj: Asset Object
        :return: Response from RegScale after inserting the provided asset object
        :rtype: Response
        """
        warnings.warn(
            "update_asset is deprecated and will be removed in a future version. Use save method instead.",
            DeprecationWarning,
        )
        url = urljoin(app.config["domain"], f"/api/assets/{obj['id']}")
        if isinstance(obj, Asset):
            obj = obj.dict()
        api = Api()
        res = api.put(url=url, json=obj)
        if res.status_code != 200:
            app.logger.error("Error updating asset: %s", obj)
        return res

    @staticmethod
    def bulk_insert(
        app: Application,
        assets: List["Asset"],
        max_workers: int = 30,
        batch_size: int = 100,
        batch: bool = False,
    ) -> List[Response]:
        """
        Bulk insert assets using the RegScale API and ThreadPoolExecutor

        :param Application app: Application Instance
        :param List[Asset] assets: Asset List
        :param int max_workers: Max Workers, defaults to 30
        :param int batch_size: Number of assets to insert per batch, defaults to 100
        :param bool batch: Insert assets in batches, defaults to False
        :return: List of Responses from RegScale
        :rtype: List[Response]
        """
        url = urljoin(app.config["domain"], "/api/assets/batchcreate")
        api = Api()
        results = []
        if batch:
            # Chunk list into batches
            batches = [
                assets[i : i + batch_size] for i in range(0, len(assets), batch_size)
            ]

            with Progress() as progress:
                total_task = progress.add_task(
                    "[red]Creating Total Assets", total=len(assets)
                )
                for my_batch in batches:
                    res = api.post(url=url, json=[asset.dict() for asset in my_batch])
                    if not res.ok:
                        app.logger.error(
                            "%i: %s\nError creating batch of assets: %s",
                            res.status_code,
                            res.text,
                            my_batch,
                        )
                    results.append(res)
                    progress.update(total_task, advance=len(my_batch))

            return results
        # Deprecated in favor of batch
        else:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                workers = [executor.submit(asset.create()) for asset in assets]
            return [worker.result() for worker in workers] or []

    @staticmethod
    def bulk_update(
        app: Application,
        assets: List["Asset"],
        max_workers: int = 30,
        batch_size: int = 100,
        batch: bool = False,
    ) -> List[Response]:
        """Bulk insert assets using the RegScale API and ThreadPoolExecutor

        :param Application app: Application Instance
        :param List[Asset] assets: Asset List
        :param int max_workers: Max Workers, defaults to 30
        :param int batch_size: Number of assets to insert per batch, defaults to 100
        :param bool batch: Insert assets in batches, defaults to False
        :return: List of Responses from RegScale
        :rtype: List[Response]
        """
        url = urljoin(app.config["domain"], "/api/assets/batchupdate")
        api = Api()
        results = []
        if batch:
            # Chunk list into batches
            batches = [
                assets[i : i + batch_size] for i in range(0, len(assets), batch_size)
            ]
            with Progress() as progress:
                total_task = progress.add_task(
                    "[red]Updating Total Assets", total=len(assets)
                )
                for my_batch in batches:
                    res = api.put(url=url, json=[asset.dict() for asset in my_batch])
                    if not res.ok:
                        app.logger.error(
                            "%i: %s\nError batch updating assets: %s",
                            res.status_code,
                            res.text,
                            my_batch,
                        )
                    results.append(res)
                    progress.update(total_task, advance=len(my_batch))
            return results
        else:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                workers = [
                    executor.submit(
                        Asset.update_asset,
                        app,
                        asset,
                    )
                    for asset in assets
                ]
            return [worker.result() for worker in workers] or []

    @classmethod
    def find_assets_by_parent(
        cls,
        app: Application,  # noqa: F841
        parent_id: int,
        parent_module: str,
    ) -> List["Asset"]:
        """
        DEPRECATED: This method is deprecated and will be removed in a future version.
        Use alternative methods to fetch assets.
        Find all assets by parent id and parent module

        :param Application app: Application Instance
        :param int parent_id: Parent Id
        :param str parent_module: Parent Module
        :return: List of Assets
        :rtype: List[Asset]
        """
        warnings.warn(
            "find_asset_by_parent is deprecated and will be removed in a future version. "
            "Use get_all_by_parent instead.",
            DeprecationWarning,
        )
        return cls.get_all_by_parent(
            parent_id=parent_id,
            parent_module=parent_module,
        )

    @classmethod
    def fetch_asset_by_id(cls, asset_id: int) -> Optional["Asset"]:
        """
        DEPRECATED: This method is deprecated and will be removed in a future version.
        Use alternative methods to fetch assets.
        Find all assets by parent id and parent module
        :param int asset_id: RegScale Asset ID number
        :return: Asset, if found
        :rtype: Optional[dict]
        """
        warnings.warn(
            "fetch_asset_by_id is deprecated and will be removed in a future version. Use get_object instead.",
            DeprecationWarning,
        )
        return cls.get_object(object_id=asset_id)

    @classmethod
    def fetch_assets_by_module(
        cls,
        app: Application,  # noqa: F841
        parent_id: int,
        parent_module: str,
    ) -> List["Asset"]:
        """
        DEPRECATED: This method is deprecated and will be removed in a future version.
        Use alternative methods to fetch assets.
        Find all assets by parent id and parent module
        :param Application app: Application Instance
        :param int parent_id: Parent Id
        :param str parent_module: Parent Module
        :return: List of Assets
        :rtype: List[Asset]
        """
        warnings.warn(
            "find_asset_by_parent is deprecated and will be removed in a future version. "
            "Use get_all_by_parent instead.",
            DeprecationWarning,
        )
        return cls.get_all_by_parent(
            parent_id=parent_id,
            parent_module=parent_module,
        )
