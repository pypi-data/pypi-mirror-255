#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Sync GCP Asset data with RegScale """

import logging

from google.cloud import asset_v1
from google.cloud.asset_v1.services.asset_service.pagers import ListAssetsPager

from regscale.core.app.utils.api_handler import APIHandler
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.integrations.commercial.gcp.auth import get_gcp_asset_service_client
from regscale.integrations.commercial.gcp.variables import GcpVariables
from regscale.models import regscale_models

logger = logging.getLogger(__name__)


def fetch_gcp_assets() -> ListAssetsPager:
    """
    Fetches GCP assets using the AssetServiceClient

    :return: A pager to iterate over GCP's assets
    :rtype: ListAssetsPager
    """
    logger.info("Fetching GCP assets...")
    client = get_gcp_asset_service_client()
    request = asset_v1.ListAssetsRequest(
        parent=f"projects/{GcpVariables.gcpProjectId}",
    )
    assets = client.list_assets(request=request)
    logger.info("Fetched GCP assets.")
    return assets


def update_regscale_assets(assets: ListAssetsPager, plan_id: int) -> None:
    """
    Updates RegScale assets with the provided GCP assets

    :param ListAssetsPager assets: A pager to iterate over GCP's assets
    :param int plan_id: The ID of the security plan to update
    :return: None
    """
    logger.info("Updating RegScale assets...")
    api_handler = APIHandler()
    user_id = api_handler.get_user_id()

    for i, asset_result in enumerate(assets):
        asset = regscale_models.Asset(
            name=asset_result.name,
            assetOwnerId=user_id,
            parentId=plan_id,
            parentModule=regscale_models.SecurityPlan.get_module_slug(),
            assetType=asset_result.asset_type,
            googleIdentifier=asset_result.name,
            dateLastUpdated=get_current_datetime(),
            status="Active (On Network)",
            assetCategory="GCP",
        ).get_or_create()
        logger.info(f"Asset {asset.name} created/updated.")

    logger.info("Updated RegScale assets.")


def sync_gcp_assets(plan_id: int) -> None:
    """
    Syncs GCP assets with RegScale assets

    :param int plan_id: The ID of the security plan to update
    :return: None
    """
    logger.info("Syncing GCP assets...")
    update_regscale_assets(assets=fetch_gcp_assets(), plan_id=plan_id)
    logger.info("Synced GCP assets.")
