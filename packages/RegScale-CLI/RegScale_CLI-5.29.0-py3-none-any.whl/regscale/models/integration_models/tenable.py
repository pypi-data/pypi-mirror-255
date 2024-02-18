#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Dataclasses for a Tenable integration """

# standard python imports
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Tuple, Union

from pydantic import BaseModel

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import format_data_to_html
from regscale.models.regscale_models.asset import Asset


class Family(BaseModel):
    """Family Model

    :param BaseModel: Base Model
    """

    id: str
    name: str
    type: str

    @classmethod
    def from_dict(cls, obj: Any) -> "Family":
        """Dict to Family

        :param obj: Object
        :return: Family
        """
        return cls(**obj)


class Repository(BaseModel):
    """Repository Model

    :param BaseModel: Base Model
    """

    id: str
    name: str
    description: str
    dataFormat: str

    @classmethod
    def from_dict(cls, obj: Any) -> "Repository":
        """Dict to Repository

        :param obj: Object
        :return: Repository
        """
        return cls(**obj)


class Severity(BaseModel):
    """Severity Model

    :param BaseModel: Base Model
    """

    id: str
    name: str
    description: str

    @classmethod
    def from_dict(cls, obj: Any) -> "Severity":
        """Dict to Severity

        :param obj: Object
        :return: Severity
        """
        return cls(**obj)


class TenableIOAsset(BaseModel):
    """Tenable Asset Model from Tenable IO API

    :param BaseModel: Pydantic BaseModel
    """

    id: str
    has_agent: bool = False
    last_seen: str
    last_scan_target: Optional[str] = None
    sources: Optional[List[dict]] = []
    acr_score: Optional[int] = None
    acr_drivers: Optional[List[dict]] = None
    exposure_score: Optional[int] = None
    scan_frequency: Optional[List[dict]] = None
    ipv4: Optional[List[str]] = None
    ipv6: Optional[List[str]] = None
    fqdn: Optional[List[str]] = None
    mac_address: Optional[List[str]] = None
    netbios_name: Optional[List[str]] = None
    operating_system: Optional[List[str]] = None
    hostname: Optional[List[str]] = None
    agent_name: Optional[List[str]] = None
    aws_ec2_name: Optional[List[str]] = None
    security_protection_level: Optional[int] = None
    security_protections: Optional[Union[List[str], List[dict]]] = None
    exposure_confidence_value: Optional[Union[str, int]] = None

    @staticmethod
    def get_asset_name(asset: "TenableIOAsset") -> str:
        """Returns the name of an asset

        :param asset: Tenable IO Asset
        :return: Asset Name
        :rtype: str
        """
        if asset.netbios_name:
            return asset.netbios_name.pop()
        if asset.hostname:
            return asset.hostname.pop()
        if asset.ipv4:
            return asset.ipv4.pop()
        if asset.last_scan_target:
            return asset.last_scan_target
        return asset.id

    @staticmethod
    def get_asset_ip(asset: "TenableIOAsset") -> Optional[str]:
        """Returns the IP address of an asset

        :param asset: Tenable IO Asset
        :return: Asset IP
        :rtype: Optional[str]
        """
        if asset.ipv4:
            return asset.ipv4.pop()
        if asset.last_scan_target:
            return asset.last_scan_target
        return None

    @staticmethod
    def get_os_type(os_list: List[str]) -> Optional[str]:
        """Returns the operating system type of an asset.

        :param os_list: A list of operating systems associated with the asset.
        :return: The operating system type of the asset, or None if os_list is empty.
        :rtype: Optional[str]
        """
        if os_list:
            for os_name in os_list:
                if "windows" in os_name.lower():
                    return "Windows Server"
                if "linux" in os_name.lower():
                    return "Linux"
                if "android" in os_name.lower():
                    return "Android"
            return "Other"
        return None

    @staticmethod
    def create_asset_from_tenable(
        asset: "TenableIOAsset", ssp_id: int, app: Application
    ) -> Asset:
        """Creates an Asset object from a TenableIOAsset object.

        :param asset: The TenableIOAsset object to create an Asset from.
        :param ssp_id: The ID of the SSP associated with the Asset.
        :param app: The Application object to use for database operations.
        :return: The created Asset object.
        :rtype: Asset
        """
        keys = ["last_seen", "last_scan_target", "acr_score", "exposure_score"]
        meta = {key: asset.dict()[key] for key in keys}

        return Asset(
            otherTrackingNumber=asset.id,
            tenableId=asset.id,
            name=TenableIOAsset.get_asset_name(asset),
            ipAddress=TenableIOAsset.get_asset_ip(asset),
            awsIdentifier=asset.aws_ec2_name if asset.aws_ec2_name else None,
            macAddress=asset.mac_address.pop() if asset.mac_address else None,
            fqdn=asset.fqdn.pop() if asset.fqdn else None,
            status="Active (On Network)",
            assetCategory="Hardware",
            assetOwnerId=app.config["userId"],
            assetType="Other",
            operatingSystem=TenableIOAsset.get_os_type(asset.operating_system),
            operatingSystemVersion=(
                asset.operating_system.pop() if asset.operating_system else None
            ),
            scanningTool=asset.sources.pop()["name"] if asset.sources else None,
            notes=format_data_to_html(meta),
            parentId=ssp_id,
            parentModule="securityplans",
            createdById=app.config["userId"],
        )

    @staticmethod
    def update_existing_asset(
        asset: Asset, existing_assets: List[Asset]
    ) -> Optional[Asset]:
        """Updates an existing Asset object if it exists and if it has changed,
            otherwise returns None

        :param asset: The Asset object to update.
        :param existing_assets: A list of existing Asset objects to compare
            against.
        :return: The updated Asset object if it has changed, otherwise None.
        :rtype: Optional[Asset]
        """
        for existing in existing_assets:
            if existing.tenableId == asset.otherTrackingNumber:
                asset.id = existing.id
                if asset != existing:
                    return asset
                return None
        return asset

    @staticmethod
    def prepare_assets_for_sync(
        assets: List["TenableIOAsset"], ssp_id: int, app: Application
    ) -> Tuple[List[Asset], List[Asset]]:
        """Prepares Tenable assets for synchronization

        :param assets: A list of TenableIOAsset objects to prepare for synchronization.
        :param ssp_id: The ID of the SSP associated with the assets.
        :param app: The Application object to use for database operations.
        :return: A tuple containing two lists of Asset objects: new assets and updated assets.
        :rtype: Tuple[List[Asset], List[Asset]]
        """
        insert_assets = []
        update_assets = []
        existing_assets = Asset.find_assets_by_parent(
            app=app, parent_id=ssp_id, parent_module="securityplans"
        )

        for asset in assets:
            reg = TenableIOAsset.create_asset_from_tenable(asset, ssp_id, app)
            updated_asset = TenableIOAsset.update_existing_asset(reg, existing_assets)
            if reg not in existing_assets:
                insert_assets.append(reg)
            if updated_asset and reg in existing_assets:
                update_assets.append(updated_asset)

        return insert_assets, update_assets

    @staticmethod
    def update_off_network_assets(
        existing_assets: List[Asset],
        assets: List["TenableIOAsset"],
        update_assets: List[Asset],
    ) -> List[Asset]:
        """Updates off-network assets

        :param existing_assets: A list of existing Asset objects to compare against.
        :param assets: A list of TenableIOAsset objects to update.
        :param update_assets: A list of Asset objects to update.
        :return: A list of updated Asset objects.
        :rtype: List[Asset]
        """
        for existing in existing_assets:
            if existing.tenableId and existing.tenableId not in {
                asset.id for asset in assets
            }:
                existing.status = "Off-Network"
                updated_asset = TenableIOAsset.update_existing_asset(
                    existing, update_assets
                )
                if updated_asset is not None:
                    update_assets.append(updated_asset)
        return update_assets

    @staticmethod
    def sync_assets_to_regscale(
        app: Application, insert_assets: List[Asset], update_assets: List[Asset]
    ) -> None:
        """Synchronizes assets to RegScale.

        :param Application app: The Application object to use for database operations.
        :param List[Asset] insert_assets: A list of Asset objects to insert.
        :param List[Asset] update_assets: A list of Asset objects to update.
        :return: None
        """
        logger = create_logger()

        if insert_assets:
            logger.info("Creating %i new asset(s) in RegScale...", len(insert_assets))
            Asset.bulk_insert(app=app, assets=insert_assets, batch_size=100, batch=True)
            logger.info("Done!")
        else:
            logger.info("No new assets need to created in RegScale.")

        if update_assets:
            logger.info(
                "Updating %i existing asset(s) in RegScale...", len(update_assets)
            )
            Asset.bulk_update(app=app, assets=update_assets, batch_size=150, batch=True)
            logger.info("Done!")
        else:
            logger.info("No assets need to be updated in RegScale.")

    @staticmethod
    def sync_to_regscale(
        app: Application, assets: List["TenableIOAsset"], ssp_id: int
    ) -> None:
        """Synchronizes Tenable assets to RegScale

        :param app: The Application object to use for database operations.
        :param assets: A list of TenableIOAsset objects to synchronize.
        :param ssp_id: The ID of the SSP associated with the assets.
        :return: None
        """
        existing_assets = Asset.find_assets_by_parent(
            app=app, parent_id=ssp_id, parent_module="securityplans"
        )
        insert_assets, update_assets = TenableIOAsset.prepare_assets_for_sync(
            assets, ssp_id, app
        )
        update_assets = TenableIOAsset.update_off_network_assets(
            existing_assets, assets, update_assets
        )
        TenableIOAsset.sync_assets_to_regscale(app, insert_assets, update_assets)


class TenableBasicAsset(BaseModel):
    """Basic Asset Class for Tenable

    :param BaseModel: Pydantic Base Class
    """

    device_type: Optional[str] = None
    hostname: Optional[str] = None
    uuid: Optional[str] = None
    ipv4: Optional[str] = None
    last_unauthenticated_results: Optional[datetime] = None
    operating_system: Optional[List[str]] = None
    network_id: Optional[str] = None
    tracked: Optional[bool] = None


class TenableAsset(BaseModel):
    """TenableAsset Model

    :param BaseModel: Base Model
    """

    pluginID: str
    severity: Severity
    hasBeenMitigated: str
    acceptRisk: str
    recastRisk: str
    ip: str
    uuid: str
    port: str
    protocol: str
    pluginName: str
    firstSeen: str
    lastSeen: str
    exploitAvailable: str
    exploitEase: str
    exploitFrameworks: str
    synopsis: str
    description: str
    solution: str
    seeAlso: str
    riskFactor: str
    stigSeverity: str
    vprScore: str
    vprContext: str
    baseScore: str
    temporalScore: str
    cvssVector: str
    cvssV3BaseScore: str
    cvssV3TemporalScore: str
    cvssV3Vector: str
    cpe: str
    vulnPubDate: str
    patchPubDate: str
    pluginPubDate: str
    pluginModDate: str
    checkType: str
    version: str
    cve: str
    bid: str
    xref: str
    pluginText: str
    dnsName: str
    macAddress: str
    netbiosName: str
    operatingSystem: str
    ips: str
    recastRiskRuleComment: str
    acceptRiskRuleComment: str
    hostUniqueness: str
    acrScore: str
    keyDrivers: str
    uniqueness: str
    family: Family
    repository: Repository
    pluginInfo: str
    count: int = 0

    @classmethod
    def from_dict(cls, obj: Any) -> "TenableAsset":
        """Dict to TenableAsset

        :param obj: Object
        :return: TenableAsset
        :rtype: TenableAsset
        """
        obj["severity"] = Severity.from_dict(obj.get("severity"))
        obj["family"] = Family.from_dict(obj.get("family"))
        obj["repository"] = Repository.from_dict(obj.get("repository"))
        return cls(**obj)

    # 'uniqueness': 'repositoryID,ip,dnsName'
    def __hash__(self):
        """
        Enable object to be hashable
        :return: Hashed TenableAsset
        :rtype: int
        """
        return hash(str(self))

    def __eq__(self, other):
        """
        Update items in TenableAsset class
        :param other:
        :return: Updated TenableAsset
        :rtype: bool
        """
        return (
            self.dnsName == other.dnsName
            and self.macAddress == other.macAddress
            and self.ip == other.ip
            and self.repository.name == other.respository.name
        )


class Reference(BaseModel):
    """Reference Model

    :param BaseModel: Base Model
    """

    framework: str
    control: str


class AssetCheck(BaseModel):
    """AssetCheck Model

    :param BaseModel: Base Model
    """

    asset_uuid: str
    first_seen: str
    last_seen: str
    audit_file: str
    check_id: str
    check_name: str
    check_info: Optional[str] = None
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    status: str
    reference: Optional[List[Reference]] = []
    see_also: str
    solution: Optional[str] = None
    plugin_id: Optional[int] = None
    state: str
    description: str


class ExportStatus(Enum):
    """ExportStatus Enum

    :param Enum: Enum base class
    """

    PROCESSING = "PROCESSING"
    FINISHED = "FINISHED"
    READY = "READY"
    CANCELLED = "CANCELLED"
    ERROR = "ERROR"


class Plugin(BaseModel):
    """Plugin Class for Tenable

    :param BaseModel: Pydantic Base Class
    """

    checks_for_default_account: Optional[bool] = None
    checks_for_malware: Optional[bool] = None
    cvss3_base_score: Optional[float] = None
    cvss3_temporal_score: Optional[float] = None
    cvss_base_score: Optional[float] = None
    cvss_temporal_score: Optional[float] = None
    description: Optional[str] = None
    exploit_available: Optional[bool] = None
    exploit_framework_canvas: Optional[bool] = None
    exploit_framework_core: Optional[bool] = None
    exploit_framework_d2_elliot: Optional[bool] = None
    exploit_framework_exploithub: Optional[bool] = None
    exploit_framework_metasploit: Optional[bool] = None
    exploited_by_malware: Optional[bool] = None
    exploited_by_nessus: Optional[bool] = None
    family: Optional[str] = None
    family_id: Optional[int] = None
    has_patch: Optional[bool] = None
    id: Optional[int] = None
    in_the_news: Optional[bool] = None
    name: Optional[str] = None
    modification_date: Optional[datetime] = None
    publication_date: Optional[datetime] = None
    risk_factor: Optional[str] = None
    see_also: Optional[List[str]] = None
    solution: Optional[str] = None
    synopsis: Optional[str] = None
    type: Optional[str] = None
    unsupported_by_vendor: Optional[bool] = None
    version: Optional[str] = None


class TenablePort(BaseModel):
    """Tenable Port and Protocol

    :param BaseModel: Pydantic Base Class
    """

    port: Optional[int]
    protocol: Optional[str]


class TenableScan(BaseModel):
    """Tenable Basic Scan class

    :param BaseModel: Pydantic Base Class
    """

    completed_at: Optional[datetime] = None
    schedule_uuid: Optional[str] = None
    started_at: Optional[datetime] = None
    uuid: Optional[str] = None
