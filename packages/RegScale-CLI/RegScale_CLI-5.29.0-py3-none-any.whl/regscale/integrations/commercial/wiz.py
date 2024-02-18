#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integrates Wiz.io into RegScale"""

# standard python imports
import codecs
import concurrent
import csv
import datetime
import io
import json
import os
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import closing
from datetime import date
from os import mkdir, path, sep
from typing import List, Optional, Tuple, Dict, Any
from urllib.parse import urljoin

import click
import pandas as pd
import requests
from pydantic import ValidationError
from requests import Session
from rich.progress import track

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import (
    capitalize_words,
    check_config_for_issues,
    check_file_path,
    check_license,
    convert_datetime_to_regscale_string,
    create_progress_object,
    find_uuid_in_str,
    get_current_datetime,
    get_env_variable,
    format_dict_to_html,
)
from regscale.core.app.utils.regscale_utils import (
    Modules,
    error_and_exit,
    verify_provided_module,
)
from regscale.models import regscale_id, regscale_module
from regscale.models.integration_models.wiz import (
    AssetCategory,
    ComplianceReport,
    ComplianceCheckStatus,
)
from regscale.models.regscale_models import Catalog
from regscale.models.regscale_models.assessment import Assessment
from regscale.models.regscale_models.asset import Asset
from regscale.models.regscale_models.control_implementation import (
    ControlImplementation,
)
from regscale.models.regscale_models.issue import Issue
from regscale.models.regscale_models.property import Property

TECHNOLOGIES_FILE_PATH = "./artifacts/technologies.json"
CONTENT_TYPE = "application/json"
RATE_LIMIT_MSG = "Rate limit exceeded"

logger = create_logger()
job_progress = create_progress_object()
url_job_progress = create_progress_object()
regscale_job_progress = create_progress_object()
compliance_job_progress = create_progress_object()

AUTH0_URLS = [
    "https://auth.wiz.io/oauth/token",
    "https://auth0.gov.wiz.io/oauth/token",
    "https://auth0.test.wiz.io/oauth/token",
    "https://auth0.demo.wiz.io/oauth/token",
]
COGNITO_URLS = [
    "https://auth.app.wiz.io/oauth/token",
    "https://auth.gov.wiz.io/oauth/token",
    "https://auth.test.wiz.io/oauth/token",
    "https://auth.demo.wiz.io/oauth/token",
    "https://auth.app.wiz.us/oauth/token",
]

CHECK_INTERVAL_FOR_DOWNLOAD_REPORT = 7
MAX_RETRIES = 100

CREATE_REPORT_QUERY = """
    mutation CreateReport($input: CreateReportInput!) {
    createReport(input: $input) {
        report {
        id
        }
    }
    }
"""

LOW = "III - Low - Other Weakness"
MODERATE = "II - Moderate - Reportable Condition"
HIGH = "I - High - Other Weakness"

PROVIDER = "Provider ID"
RESOURCE = "Resource Type"


# Create group to handle Wiz.io integration
@click.group()
def wiz():
    """Integrates continuous monitoring data from Wiz.io."""


@wiz.command()
@click.option("--client_id", default=None, hide_input=False, required=False)
@click.option("--client_secret", default=None, hide_input=True, required=False)
def authenticate(client_id, client_secret):
    """Authenticate to Wiz."""
    wiz_authenticate(client_id, client_secret)


def wiz_authenticate(
    client_id: Optional[str] = None, client_secret: Optional[str] = None
) -> None:
    """
    Authenticate to Wiz

    :param str client_id: Wiz client ID, defaults to None
    :param str client_secret: Wiz client secret, defaults to None
    :return: None
    """
    app = check_license()
    api = Api()
    # Login with service account to retrieve a 24 hour access token that updates YAML file
    logger.info("Authenticating - Loading configuration from init.yaml file")

    # load the config from YAML
    config = app.config

    # get secrets
    if "wizclientid" in [key.lower() for key in os.environ] and not client_id:
        client_id = get_env_variable("WizClientID")
    if not client_id:
        raise ValueError(
            "No Wiz Client ID provided in system environment or CLI command."
        )
    if "wizclientsecret" in [key.lower() for key in os.environ] and not client_secret:
        client_secret = get_env_variable("WizClientSecret")
    if not client_secret:
        raise ValueError(
            "No Wiz Client Secret provided in system environment or CLI command."
        )
    wiz_auth_url = config.get("wizAuthUrl")
    if not wiz_auth_url:
        error_and_exit("No Wiz Authentication URL provided in the init.yaml file.")

    # login and get token
    logger.info("Attempting to retrieve OAuth token from Wiz.io.")
    token, scope = get_token(
        api=api,
        client_id=client_id,
        client_secret=client_secret,
        token_url=wiz_auth_url,
    )

    # assign values

    config["wizAccessToken"] = token
    config["wizScope"] = scope

    # write our the result to YAML
    # write the changes back to file
    app.save_config(config)


def get_token(
    api: Api, client_id: str, client_secret: str, token_url: str
) -> tuple[str, str]:
    """
    Return Wiz.io token

    :param Api api: api instance
    :param str client_id: Wiz client ID
    :param str client_secret: Wiz client secret
    :param str token_url: token url
    :return: tuple of token and scope
    :rtype: tuple[str, str]
    """
    app = api.app
    config = api.config
    status_code = 500
    logger.info("Getting a token")
    response = api.post(
        url=token_url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        json=None,
        data=generate_authentication_params(client_id, client_secret, token_url),
    )
    if response.ok:
        status_code = 200
    logger.debug(response.reason)
    # If response is unauthorized, try the first cognito url
    if response.status_code == requests.codes.unauthorized:
        try:
            response = api.post(
                url=COGNITO_URLS[0],
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                json=None,
                data=generate_authentication_params(
                    client_id, client_secret, COGNITO_URLS[0]
                ),
            )
            if response.ok:
                status_code = 200
                logger.info(
                    "Successfully authenticated using the authorization url: %s, now updating init.yaml..",
                    COGNITO_URLS[0],
                )
                config["wizAuthUrl"] = COGNITO_URLS[0]
                app.save_config(config)
        except requests.RequestException:
            error_and_exit(f"Wiz Authentication: {response.reason}")
    if status_code != requests.codes.ok:
        error_and_exit(
            f"Error authenticating to Wiz [{response.status_code}] - {response.text}"
        )
    response_json = response.json()
    token = response_json.get("access_token")
    scope = response_json.get("scope")
    if not token:
        error_and_exit(
            f'Could not retrieve token from Wiz: {response_json.get("message")}'
        )
    logger.info("SUCCESS: Wiz.io access token successfully retrieved.")
    return token, scope


def generate_authentication_params(
    client_id: str, client_secret: str, token_url: str
) -> dict:
    """
    Create the Correct Parameter format based on URL

    :param str client_id: Wiz Client ID
    :param str client_secret: Wiz Client Secret
    :param str token_url: Wiz URL
    :raises Exception: A generic exception if token_url provided is invalid
    :return: Dictionary containing authentication parameters
    :rtype: dict
    """
    if token_url in AUTH0_URLS:
        return {
            "grant_type": "client_credentials",
            "audience": "beyond-api",
            "client_id": client_id,
            "client_secret": client_secret,
        }
    if token_url in COGNITO_URLS:
        return {
            "grant_type": "client_credentials",
            "audience": "wiz-api",
            "client_id": client_id,
            "client_secret": client_secret,
        }
    raise ValueError("Invalid Token URL")


@wiz.command()
@click.option(
    "--wiz_project_id",
    prompt="Enter the Wiz project ID",
    help="Enter the Wiz Project ID.  Options include: projects, \
          policies, supplychain, securityplans, components.",
    required=True,
)
@regscale_id(help="RegScale will create and update issues as children of this record.")
@regscale_module()
@click.option(
    "--client_id",
    help="Wiz Client ID, or can be set as environment variable WizClientID",
    default=None,
    hide_input=False,
    required=False,
)
@click.option(
    "--client_secret",
    help="Wiz Client Secret, or can be set as environment variable WizClientSecret",
    default=None,
    hide_input=True,
    required=False,
)
def inventory(
    wiz_project_id: str,
    regscale_id: int,
    regscale_module: str,
    client_id: str,
    client_secret: str,
) -> None:
    """Process inventory from Wiz and create assets in RegScale."""
    fetch_inventory(
        wiz_project_id=wiz_project_id,
        regscale_id=regscale_id,
        regscale_module=regscale_module,
        client_id=client_id,
        client_secret=client_secret,
    )


def update_properties(
    app: Application, existing_asset_data: list[dict], properties: list[Property]
) -> None:
    """Insert or update properties for existing assets.

    :param app: An instance of the RegScale app.
    :param existing_asset_data: Existing asset data.
    :param properties: Properties to isnert or update.
    :return: None
    """

    def process_props() -> None:
        """
        Process Properties.

        :return: None
        """
        if prop.alt_id not in {wiz.alt_id for wiz in existing_property_data}:
            new_props.append(prop)
        else:
            if prop not in existing_property_data:
                match = [
                    data
                    for data in existing_property_data
                    if prop.key == data.key and data.parentId == prop.parentId
                ]
                if match:
                    prop.id = match[0].id
                    update_props.append(prop)
                else:
                    new_props.append(prop)

    # Update Properties
    new_props = []  # type: list
    update_props = []  # type: list
    existing_property_data = Property.existing_properties(
        app=app, existing_assets=existing_asset_data
    )
    for prop in properties:
        # Update property records with a valid parent id from the newly inserted asset.
        dat = [asset for asset in existing_asset_data if prop.alt_id == asset["wizId"]]
        if dat:
            asset = dat[0]
            prop.parentId = asset["id"]
            process_props()
    Property.insert_properties(app, new_props)
    Property.update_properties(app, update_props)


def update_results(res: requests.Response, results: List[dict]) -> None:
    """
    Update results

    :param requests.Response res: A requests response
    :param list results: A list of results
    :return: None
    """
    content_type = res.headers.get("Content-Type", "")
    if CONTENT_TYPE not in content_type:
        error_and_exit(
            "Failed to fetch technologies. Invalid content type in response."
        )
    if "errors" in res.json():
        error_and_exit(f'Wiz Error: {res.json()["errors"]}')
    for node in res.json()["data"]["technologies"]["nodes"]:
        if node["id"] not in {res["id"] for res in results}:
            results.append(node)


def fetch_technologies(app: Application) -> list[dict]:
    """
    Fetch technologies from Wiz.

    :param app: Application instance
    :return: List of technologies
    :rtype: list
    """

    def query_techs():
        """
        Make a request to Wiz for technologies.

        :return: True if next page exists, False otherwise
        :rtype: bool
        """
        res = send_request(
            app=app,
            query=body,
            variables=variables,
            api_endpoint_url=app.config["wizUrl"],
        )
        update_results(res, results)
        # Update vars
        page_info = res.json()["data"]["technologies"]["pageInfo"]
        variables["after"] = page_info["endCursor"] if "endCursor" in page_info else ""
        next_page = page_info["hasNextPage"] if "hasNextPage" in page_info else False
        logger.info("Fetched %i technologies from Wiz..", len(results))
        return next_page

    results = []
    updated = False
    # Load Prefetched results if exist:
    results = load_techs(results)
    body = """
        query TechQuery($first: Int!, $after: String) {
        technologies(
          first: $first
          after: $after
        ) {
          totalCount
          pageInfo {
            endCursor
            hasNextPage
          }
          nodes {
            id
            name
          }
        }
        }
    """
    # The variables sent along with the above query
    variables = {"first": 500, "after": None}
    file_age = set_file_age()
    if len(results) == 0 or file_age == 0 or (file_age > 21600):
        updated = True
        # Clear results
        results = []
        logger.info("Refreshing the latest Wiz technology list..")
        has_next_page = query_techs()
        # Get file age from today
        while has_next_page:
            # fetch next page
            has_next_page = query_techs()
    if updated:
        prefetch(results)
    return results


def set_file_age() -> int:
    """
    Set file age in minutes.

    :return: File age in minutes
    :rtype: int
    """
    file_age = 0
    if path.exists(TECHNOLOGIES_FILE_PATH):
        file_age = (
            datetime.datetime.now()
            - datetime.datetime.fromtimestamp(path.getmtime(TECHNOLOGIES_FILE_PATH))
        ).seconds / 60
    return file_age


def load_techs(results) -> dict:
    """
    Load prefetched technologies from local file.

    :param results: List of results
    :return: Results loaded from local file
    :rtype: dict
    """
    try:
        if not path.exists("artifacts"):
            mkdir("artifacts")
        if path.exists(TECHNOLOGIES_FILE_PATH):
            with open(TECHNOLOGIES_FILE_PATH, "r", encoding="utf-8") as file:
                results = json.load(file)
    except FileNotFoundError as ex:
        logger.warning("Error loading prefetched technologies: %s", ex)
    return results


def prefetch(data: list[dict]) -> None:
    """
    Prefetch data to artifacts directory.

    :param list data: List of data
    :return: None
    """
    assert isinstance(data, list)
    if not path.exists("artifacts"):
        mkdir("artifacts")
    with open("artifacts/technologies.json", "w") as file:
        json.dump(data, file)


def fetch_inventory(
    wiz_project_id: str,
    regscale_id: int,
    regscale_module: str,
    client_id: str,
    client_secret: str,
) -> None:
    """Process inventory list from Wiz.

    :param wiz_project_id: A Wiz project ID
    :param regscale_id: RegScale ID
    :param regscale_module: RegScale module
    :param client_id: Wiz Client ID
    :param client_secret: Wiz Client Secret
    :return: None
    """
    wiz_authenticate(client_id, client_secret)
    app = check_license()
    api = Api()
    verify_provided_module(regscale_module)
    # load the config from YAML
    config = app.config
    if not check_module_id(regscale_id, regscale_module):
        error_and_exit(f"Please enter a valid regscale_id for {regscale_module}.")

    # get secrets
    url = config["wizUrl"]

    # get the full list of assets
    logger.info("Fetching full asset list from RegScale.")

    existing_asset_data = Asset.get_by_parent(
        parent_id=regscale_id, parent_module=regscale_module
    )

    # make directory if it doesn't exist
    if path.exists("artifacts") is False:
        mkdir("artifacts")
        logger.warning(
            "Artifacts directory does not exist.  Creating new directory for artifact \
                processing."
        )

    else:
        logger.info(
            "Artifacts directory exists.  This directly will store output files from all processing."
        )

    report_prefix = f"RegScale_Inventory_Report_Automated_Entities_{wiz_project_id}"
    existing_inventory_reports = [
        # report for report in query_reports(app) if report_prefix in report["name"]
    ]
    date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    # Update existing reports
    for report in existing_inventory_reports:
        last_run = datetime.datetime.strptime(
            report["lastRun"]["runAt"], date_format
        )  # UTC
        update_report(app, last_run, report["id"])

    # Update Existing reports, if any

    # if report ids are null, create
    wiz_report_ids = create_or_update_inventory_report(
        app=app,
        url=url,
        rpts=existing_inventory_reports,
        report_prefix=report_prefix,
        wiz_project_id=wiz_project_id,
    )
    properties, wiz_assets = create_assets(
        app=app,
        wiz_report_ids=wiz_report_ids,
        parent_id=regscale_id,
        parent_module=regscale_module,
    )
    new_assets = [
        asset
        for asset in wiz_assets
        if asset["wizId"] not in {wiz.wizId for wiz in existing_asset_data}
    ]
    update_assets = []
    existing_wiz_ids = {wiz.wizId for wiz in existing_asset_data}
    for asset in existing_asset_data:
        regscale_id, update_assets = process_asset(
            asset, existing_wiz_ids, regscale_id, update_assets, wiz_assets
        )

    api.update_server(
        config=app.config,
        url=urljoin(app.config["domain"], "/api/assets"),
        method="put",
        message=f"[#6200ff]Updating {len(update_assets)} assets in RegScale.",
        json_list=update_assets,
    )
    for asset in track(
        new_assets,
        description=f"[#ba1d49]Inserting {len(new_assets)} new assets in RegScale.",
    ):
        api.post(url=urljoin(app.config["domain"], "/api/assets"), json=asset)
    existing_asset_data = Asset.get_by_parent(
        parent_id=regscale_id, parent_module=regscale_module
    )
    update_properties(
        app=app, existing_asset_data=existing_asset_data, properties=properties
    )


def process_asset(
    asset: dict,
    existing_wiz_ids: set[str],
    regscale_id: int,
    update_assets: List[Asset],
    wiz_assets: List[dict],
) -> tuple[int, List[Asset]]:
    """
    Process asset

    :param dict asset: Asset dictionary
    :param set existing_wiz_ids: Existing Wiz IDs
    :param int regscale_id: RegScale ID
    :param list update_assets: List of assets to update
    :param list wiz_assets: List of Wiz assets
    :return: RegScale ID, list of assets to update
    :rtype: tuple[int, list]
    """
    if isinstance(asset, Asset):
        asset = asset.dict()
    if asset["wizId"] in existing_wiz_ids:
        regscale_id = asset["id"]
        if wiz_index := next(
            (
                index
                for (index, d) in enumerate(wiz_assets)
                if d["wizId"] == asset["wizId"]
            ),
            None,
        ):
            update_asset = wiz_assets[wiz_index]
            update_asset["id"] = regscale_id
            if (
                isinstance(update_asset, dict)
                and isinstance(asset, dict)
                and Asset(**update_asset) != Asset(**asset)
                and isinstance(asset, dict)
            ):
                update_assets.append(update_asset)
    return regscale_id, update_assets


def lookup_tech(techs, wiz_json) -> str:
    """
    Lookup tech

    :param list techs: List of technologies
    :param dict wiz_json: Wiz JSON
    :return: Technology name
    :rtype: str
    """
    result: str = ""
    if isinstance(wiz_json, str):
        dat = json.loads(wiz_json)
    elif isinstance(wiz_json, dict):
        dat = wiz_json

    inner_dict = None
    for key, value in dat.items():
        if key == "technologies" and isinstance(value, dict):
            inner_dict = value
            break
    if inner_dict:
        result = techs.get(inner_dict["id"], "")
    if "common" in dat.keys() and "enrichments" in dat["common"]:
        try:
            tech_id = dat["common"]["enrichments"]["techIDs"].pop()
            dat = [tech for tech in techs if tech["id"] == tech_id]
            if dat:
                result = dat[0]["name"]
        except IndexError:
            logger.debug("Empty list in tech lookup")
    return result


def create_wiz_assets(
    app: Application, dataframe: pd.DataFrame, parent_id: int, parent_module: str
) -> tuple[list, list]:
    """
    Create Wiz Assets

    :param app: Application instance
    :param dataframe: frame of wiz assets
    :param parent_id: RegScale parent id
    :param parent_module: RegScale parent module
    :return: List of Wiz assets and properties
    :rtype: tuple[list, list]
    """
    mapping = {
        "ACCESS_ROLE": "Other",
        "ACCESS_ROLE_BINDING": "Other",
        "ACCESS_ROLE_PERMISSION": "Other",
        "API_GATEWAY": "Other",
        "APPLICATION": "Other",
        "AUTHENTICATION_CONFIGURATION": "Other",
        "BACKUP_SERVICE": "Other",
        "BUCKET": "Other",
        "CDN": "Other",
        "CERTIFICATE": "Other",
        "CICD_SERVICE": "Other",
        "CLOUD_LOG_CONFIGURATION": "Other",
        "CLOUD_ORGANIZATION": "Other",
        "COMPUTE_INSTANCE_GROUP": "Other",
        "CONFIG_MAP": "Other",
        "CONTAINER": "Other",
        "CONTAINER_GROUP": "Other",
        "CONTAINER_IMAGE": "Other",
        "CONTAINER_REGISTRY": "Other",
        "CONTAINER_SERVICE": "Other",
        "DAEMON_SET": "Other",
        "DATABASE": "Other",
        "DATA_WORKLOAD": "Other",
        "DB_SERVER": "Physical Server",
        "DEPLOYMENT": "Other",
        "DNS_RECORD": "Other",
        "DNS_ZONE": "Other",
        "DOMAIN": "Other",
        "EMAIL_SERVICE": "Other",
        "ENCRYPTION_KEY": "Other",
        "ENDPOINT": "Other",
        "FILE_SYSTEM_SERVICE": "Other",
        "FIREWALL": "Firewall",
        "GATEWAY": "Other",
        "GOVERNANCE_POLICY": "Other",
        "GOVERNANCE_POLICY_GROUP": "Other",
        "HOSTED_APPLICATION": "Other",
        "IAM_BINDING": "Other",
        "IP_RANGE": "Other",
        "KUBERNETES_CLUSTER": "Other",
        "KUBERNETES_CRON_JOB": "Other",
        "KUBERNETES_INGRESS": "Other",
        "KUBERNETES_INGRESS_CONTROLLER": "Other",
        "KUBERNETES_JOB": "Other",
        "KUBERNETES_NETWORK_POLICY": "Other",
        "KUBERNETES_NODE": "Other",
        "KUBERNETES_PERSISTENT_VOLUME": "Other",
        "KUBERNETES_PERSISTENT_VOLUME_CLAIM": "Other",
        "KUBERNETES_POD_SECURITY_POLICY": "Other",
        "KUBERNETES_SERVICE": "Other",
        "KUBERNETES_STORAGE_CLASS": "Other",
        "KUBERNETES_VOLUME": "Other",
        "LOAD_BALANCER": "Other",
        "MANAGED_CERTIFICATE": "Other",
        "MANAGEMENT_SERVICE": "Other",
        "NETWORK_ADDRESS": "Other",
        "NETWORK_INTERFACE": "Other",
        "NETWORK_ROUTING_RULE": "Other",
        "NETWORK_SECURITY_RULE": "Other",
        "PEERING": "Other",
        "POD": "Other",
        "PORT_RANGE": "Other",
        "PRIVATE_ENDPOINT": "Other",
        "PROXY": "Other",
        "PROXY_RULE": "Other",
        "RAW_ACCESS_POLICY": "Other",
        "REGISTERED_DOMAIN": "Other",
        "REPLICA_SET": "Other",
        "RESOURCE_GROUP": "Other",
        "SEARCH_INDEX": "Other",
        "SUBNET": "Other",
        "SUBSCRIPTION": "Other",
        "SWITCH": "Network Switch",
        "VIRTUAL_DESKTOP": "Virtual Machine (VM)",
        "VIRTUAL_MACHINE": "Virtual Machine (VM)",
        "VIRTUAL_MACHINE_IMAGE": "Other",
        "VIRTUAL_NETWORK": "Other",
        "VOLUME": "Other",
        "WEB_SERVICE": "Other",
        "DATA_WORKFLOW": "Other",
    }

    wiz_assets, wiz_properties = [], []
    techs = fetch_technologies(app)
    for _, row in dataframe.iterrows():
        provider_id = (
            find_uuid_in_str(row[PROVIDER])
            if isinstance(row[PROVIDER], str)
            else row[PROVIDER]
        )
        external_id = row["External ID"]
        description = lookup_tech(techs, row["Wiz JSON Object"])
        wiz_json = json.loads(row["Wiz JSON Object"])
        native_json = json.loads(row["Cloud Native JSON"])
        wiz_data = json.dumps(
            {
                "info_data": {
                    PROVIDER: row[PROVIDER],
                    "External ID": external_id,
                    "Cloud Platform": row["Cloud Platform"],
                    "Subscription ID": row["Subscription ID"],
                },
                "tags": json.loads(row["Tags"]),
                "wiz_json": wiz_json,
                "other": native_json,
            }
        )
        name = determine_asset_name(native_json, row, wiz_json)
        version = wiz_json.get("versionInformation", {}).get("version", "")
        properties = Property.get_properties(
            app=app, wiz_data=wiz_data, wiz_id=external_id
        )
        r_asset = Asset(
            name=name,
            notes=f"External ID: {external_id}",
            otherTrackingNumber=provider_id,
            wizId=external_id,
            wizInfo=None,
            parentId=parent_id,
            parentModule=parent_module,
            ipAddress=None,
            macAddress=None,
            operatingSystem=(
                row["app.kubernetes.io/os"]
                if "app.kubernetes.io/os" in json.loads(row["Tags"])
                else None
            ),
            assetOwnerId=app.config["userId"],
            status="Active (On Network)",  # Get Status from Tags
            assetCategory=map_category(row[RESOURCE]),
            assetType=mapping.get(row[RESOURCE], "Other"),
            description=description,
            version=version,
            softwareVersion=(
                version if map_category(row[RESOURCE]) == "Software" else ""
            ),
            softwareName=name if map_category(row[RESOURCE]) == "Software" else "",
            location=wiz_json.get("region"),
        )
        wiz_assets.append(r_asset.dict())
        wiz_properties.extend(properties)
    logger.info("%i Wiz Assets with valid provider id's filtered..", len(wiz_assets))
    # Dedupe assets
    deduped = list({Asset(**asset) for asset in wiz_assets})
    wiz_assets = [asset.dict() for asset in deduped]
    return wiz_assets or [], wiz_properties or []


def determine_asset_name(native_json, row, wiz_json):
    """
    Determine the name of an asset

    :param dict native_json: Native JSON data
    :param Series row: A Pandas Series from a DataFrame
    :param dict wiz_json: Wiz JSON data
    :rtype: str
    """
    name = "Unknown"
    if "name" in native_json.keys():
        name = native_json["name"]
    elif "name" in row:
        name = row["name"]
    elif "common" in wiz_json and "name" in wiz_json["common"]:
        name = wiz_json["common"]["name"]
    return name


def gather_urls_concurrently(app: Application, wiz_report_ids: List[str]) -> List[str]:
    """
    Gathers download URLs for Wiz reports concurrently.

    :param Application app: An instance of the RegScale app.
    :param List[str] wiz_report_ids: A list of Wiz report IDs.
    :return: A list of download URLs.
    :rtype: List[str]
    """
    max_workers = app.config.get("wizMaxConnectionPoolWorkers", 10)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(get_report_url_and_status, app, report_id)
            for report_id in wiz_report_ids
        ]
        return [future.result() for future in futures]


def download_and_process_report(url: str, session: Session) -> Optional[pd.DataFrame]:
    """
    Downloads a report and processes it into a DataFrame.

    :param str url: The URL to download the report from.
    :param Session session: The requests session to use.
    :return: A DataFrame.
    :rtype: pandas.DataFrame or None
    """
    logger.debug("Downloading %s", url)
    response = session.get(url, stream=True)
    if url_data := response.content:
        stream_frame = pd.read_csv(io.StringIO(url_data.decode("utf-8")))
        logger.debug(len(stream_frame))
        return stream_frame


def download_and_process_reports_concurrently(
    app: Application, urls: List[str], session: Session
) -> List[pd.DataFrame]:
    """
    Downloads and processes reports concurrently.

    :param Application app: An instance of the RegScale app.
    :param List[str] urls: A list of URLs to download reports from.
    :param Session session: The requests session to use.
    :return: A list of DataFrames.
    :rtype: list
    """
    max_workers = app.config.get("wizMaxConnectionPoolWorkers", 10)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all the tasks to the executor
        future_to_url = {
            executor.submit(download_and_process_report, url, session): url
            for url in urls
        }
        results = []
        for future in as_completed(future_to_url):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                # Handle exceptions if needed
                # future_to_url[future] is the url for this future
                logger.debug(f"Error processing: {e}")
        return results


def create_assets(
    app: Application,
    wiz_report_ids: List[str],
    parent_id: int,
    parent_module: str,
) -> Tuple[List[dict], List[Asset]]:
    """
    Create Wiz Assets and Sync to RegScale

    :param Application app: The application instance
    :param list wiz_report_ids: A list of Wiz report IDs
    :param int parent_id: ID from RegScale of parent
    :param str parent_module: Parent Module of item in RegScale
    :raises Exception: A generic exception
    :raises requests.RequestException: A requests exception
    :return: properties: str, wiz_assets: list
    :rtype: tuple[list[dict], list[Asset]]
    """
    try:
        logger.info("Streaming Automated Inventory Report(s) to RegScale Assets..")
        api = Api()
        session = api.session

        # Gather URLs concurrently
        urls = gather_urls_concurrently(app, wiz_report_ids)

        # Download and process reports concurrently
        frames = download_and_process_reports_concurrently(
            app=app, urls=urls, session=session
        )

        # Merge reports and create assets
        all_df = pd.concat(frames)
        logger.info("Merging reports to a dataset with %i records", len(all_df))
        wiz_assets, properties = create_wiz_assets(
            app, all_df, parent_id, parent_module
        )
        wiz_assets = wiz_assets if wiz_assets is not None else []
        properties = properties if properties is not None else []
        if len(wiz_assets) == 0:
            logger.warning("No Wiz Assets found!")

        return properties, wiz_assets

    except Exception as e:
        logger.error("Error fetching reports: %s", e)
        return [], []


@wiz.command()
@click.option(
    "--wiz_project_id",
    prompt="Enter the project ID for Wiz",
    default=None,
    required=True,
)
@regscale_id(help="RegScale will create and update issues as children of this record.")
@regscale_module()
@click.option(
    "--issue_severity_filter",
    default="low, medium, high, critical",
    help="A filter for the severity types included in the wiz issues report. defaults to ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']",
    type=click.STRING,
    hide_input=False,
    required=False,
)
@click.option(
    "--client_id",
    help="Wiz Client ID, or can be set as environment variable WizClientID",
    default=None,
    hide_input=False,
    required=False,
)
@click.option(
    "--client_secret",
    help="Wiz Client Secret, or can be set as environment variable WizClientSecret",
    default=None,
    hide_input=True,
    required=False,
)
# flake8: noqa: C901
def issues(
    wiz_project_id: str,
    regscale_id: int,
    regscale_module: str,
    client_id: str,
    client_secret: str,
    issue_severity_filter: str,
) -> None:
    """
    Process Issues from Wiz into RegScale
    """
    process_wiz_issues(
        wiz_project_id=wiz_project_id,
        regscale_id=regscale_id,
        regscale_module=regscale_module,
        client_id=client_id,
        client_secret=client_secret,
        issue_severity_filter=issue_severity_filter,
    )


def concatenate_security_checks(issue_security_checks, wiz_security_checks):
    """
    Concatenate security checks from issue and wiz if both are present and different.

    :param issue_security_checks: Security checks from the issue.
    :param wiz_security_checks: Security checks from the wiz.
    :return: Concatenated or original security checks.
    """
    if issue_security_checks and issue_security_checks != wiz_security_checks:
        return f"{issue_security_checks}</br>{wiz_security_checks}"
    return wiz_security_checks


def update_issue_status(issue, set_wiz_issues) -> None:
    """
    Update the issue's status based on its presence in Wiz issues.

    :param issue: The issue to be updated.
    :param set_wiz_issues: Set containing the identifiers of Wiz issues.
    :return: None.
    """
    issue.status = "Open" if issue.wizId in set_wiz_issues else "Closed"
    if issue.status == "Closed" and not issue.dateCompleted:
        issue.dateCompleted = get_current_datetime()
    elif issue.status == "Open":
        issue.dateCompleted = ""


def update_issue_with_wiz_data(issue, wiz_issue) -> bool:
    """
    Update the issue fields with data from a corresponding Wiz issue.

    :param issue: The issue to be updated.
    :param wiz_issue: A Wiz issue containing data for update.
    :return: Boolean indicating if the issue was updated.
    :rtype: bool
    """
    if issue.wizId != wiz_issue.wizId:
        return False

    issue.securityChecks = concatenate_security_checks(
        issue.securityChecks, wiz_issue.securityChecks
    )
    if issue.recommendedActions != wiz_issue.recommendedActions:
        issue.recommendedActions = wiz_issue.recommendedActions
        return True

    return False


def update_issue(issue, wiz_issues) -> Issue:
    """
    Process RegScale issue and update it with Wiz issue data.

    :param issue: RegScale Issue.
    :param wiz_issues: List of Wiz Issues.
    :return: Updated RegScale Issue.
    :rtype: Issue.
    """
    set_wiz_issues = set(wiz.wizId for wiz in wiz_issues)
    update_issue_status(issue, set_wiz_issues)

    for wiz_issue in wiz_issues:
        if update_issue_with_wiz_data(issue, wiz_issue):
            break

    return issue


def process_wiz_issues(
    wiz_project_id: str,
    regscale_id: int,
    regscale_module: str,
    client_id: str,
    client_secret: str,
    issue_severity_filter: str = None,
) -> None:
    """Process Issues from Wiz.

    :param wiz_project_id: Wiz Project ID
    :param regscale_id: RegScale ID
    :param regscale_module: RegScale Module
    :param client_id: Wiz Client ID
    :param client_secret: Wiz Client Secret
    :param issue_severity_filter: Wiz Issue Severity Filter
    :return: None
    """
    if issue_severity_filter is None:
        issue_severity_filter = "low, medium, high, critical"

    issues_severity = [
        iss.upper().strip() for iss in issue_severity_filter.split(",")
    ]  # Case insensitive for the user.

    wiz_authenticate(client_id, client_secret)
    app = check_license()
    config = app.config
    api = Api()
    if "wizIssuesReportId" not in config:
        config["wizIssuesReportId"] = {}
        config["wizIssuesReportId"]["report_id"] = None
        config["wizIssuesReportId"]["last_seen"] = None
        app.save_config(config)
    verify_provided_module(regscale_module)
    wiz_report_info = None
    # load the config from YAML
    wiz_report_id: str = ""
    if not check_module_id(regscale_id, regscale_module):
        error_and_exit(f"Please enter a valid regscale_id for {regscale_module}.")

    # get secrets
    url = config["wizUrl"]
    # set headers
    if regscale_module == "securityplans":
        existing_regscale_issues = Issue.fetch_issues_by_ssp(
            app=app, ssp_id=regscale_id
        )
    else:
        existing_regscale_issues = Issue.fetch_issues_by_parent(
            app=app, regscale_id=regscale_id, regscale_module=regscale_module
        )
    # Only pull issues that have a wizId
    existing_regscale_issues = [iss for iss in existing_regscale_issues if iss.wizId]
    check_file_path("artifacts")

    # write out issues data to file
    if len(existing_regscale_issues) > 0:
        with open(
            f"artifacts{sep}existingRecordIssues.json", "w", encoding="utf-8"
        ) as outfile:
            outfile.write(
                json.dumps(
                    [iss.dict() for iss in existing_regscale_issues],
                    indent=4,
                )
            )
        logger.info(
            "Writing out RegScale issue list for Record # %s "
            "to the artifacts folder (see existingRecordIssues.json)",
            str(regscale_id),
        )
    logger.info(
        "%s existing issues retrieved for processing from RegScale.",
        str(len(existing_regscale_issues)),
    )
    issue_report_name = f"RegScale_Issues_Report_project_{wiz_project_id}_{'_'.join([fil.lower() for fil in issues_severity])}"
    rpts = [
        report for report in query_reports(app) if report["name"] == issue_report_name
    ]
    report_data, wiz_report_info = update_wiz_report_id_config(
        app, rpts, wiz_report_info
    )

    # find report if exists and is valid
    if "wizIssuesReportId" in app.config and not wiz_report_id:
        try:
            assert app.config["wizIssuesReportId"]["report_id"] == rpts[0]["id"]
            date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
            last_run = datetime.datetime.strptime(
                rpts[0]["lastRun"]["runAt"], date_format
            )  # UTC
            report_id = wiz_report_info["report_id"]
            update_report(app, last_run, report_id)

        except (AssertionError, IndexError):
            logger.warning(
                "Report not found, creating Automated RegScale report on Wiz"
            )
            wiz_report_id = create_issues_report(
                app,
                url,
                issue_report_name,
                wiz_project_id=wiz_project_id,
                issues_severity=issues_severity,
            )
    elif rpts:
        app.config["wizIssuesReportId"] = report_data
        wiz_report_id = app.config["wizIssuesReportId"]["report_id"]
        app.save_config(app.config)
    else:
        wiz_report_id = create_issues_report(
            app,
            url,
            issue_report_name,
            wiz_project_id=wiz_project_id,
            issues_severity=issues_severity,
        )
    wiz_report_id = wiz_report_info["report_id"] if wiz_report_info else wiz_report_id
    report_url = get_report_url_and_status(app=app, report_id=wiz_report_id)

    # Fetch the data!
    wiz_issues = fetch_wiz_issues(
        download_url=report_url,
        regscale_id=regscale_id,
        regscale_module=regscale_module,
    )
    update_issues = []
    filtered_issues = [
        wiz.dict()
        for wiz in wiz_issues
        if wiz.wizId not in set(reg.wizId for reg in existing_regscale_issues)
    ]

    new_issues = process_issue_due_date(
        config, filtered_issues, existing_regscale_issues
    )
    for issue in existing_regscale_issues:
        issue = update_issue(issue, wiz_issues)
        update_issues.append(issue)
    api.update_server(
        config=app.config,
        method="post",
        url=urljoin(app.config["domain"], "/api/issues"),
        json_list=new_issues,
        message=f"[#14bfc7]Inserting {len(new_issues)} issues in RegScale.",
    )
    api.update_server(
        config=app.config,
        method="put",
        url=urljoin(app.config["domain"], "/api/issues"),
        json_list=[iss.dict() for iss in update_issues],
        message=f"[#15cfec]Updating {len(update_issues)} issues in RegScale.",
    )


def update_report(app, last_run, report_id) -> None:
    """
    Update report if necessary

    :param app: Application instance
    :param last_run: Last run
    :param report_id: Report ID
    :return: None
    """
    if (
        (
            datetime.datetime.now() - last_run
        ).seconds  # removed timezone aware datetime as it threw errors
        > (app.config["wizReportAge"]) * 60
        if app.config["wizReportAge"] != 0
        else 1
    ):  # Rerun old reports
        rerun_report(app, report_id)


def update_wiz_report_id_config(
    app: Application, rpts: List[dict], wiz_report_info: dict
) -> tuple[dict, dict]:
    """
    Update Wiz Report ID Config

    :param Application app: Application instance
    :param List[dict] rpts: Wiz reports
    :param dict wiz_report_info: Wiz report info
    :return: Report data, Wiz report info
    :rtype: tuple[dict, dict]
    """
    report_data = {}
    if rpts:
        last_seen = (
            app.config["wizIssuesReportId"]["last_seen"]
            if "wizIssuesReportId" in app.config
            and "last_seen" in app.config["wizIssuesReportId"].keys()
            else None
        )
        if not last_seen:
            rerun_report(app, rpts[0]["id"])
            last_seen = app.config["wizIssuesReportId"]["last_seen"]
        report_data = {
            "report_id": rpts[0]["id"],
            "last_seen": last_seen,
        }
        wiz_report_info = report_data
        app.config["wizIssuesReportId"] = wiz_report_info
        app.save_config(app.config)

    return report_data, wiz_report_info


def process_issue_due_date(
    config: dict, filtered_issues: List[Issue], existing_regscale_issues: List[Issue]
) -> list[Issue]:
    """
    Process issue due date

    :param dict config: Config
    :param List[Issue] filtered_issues: Filtered issues
    :param List[Issue] existing_regscale_issues: Existing RegScale issues
    :return: New issues
    :rtype: List[Issue]
    """
    new_issues = []
    fmt = "%Y-%m-%d %H:%M:%S"
    for issue in filtered_issues:
        if issue["severityLevel"] == LOW:
            days = config["issues"]["wiz"]["low"]
        elif issue["severityLevel"] == MODERATE:
            days = config["issues"]["wiz"]["medium"]
        elif issue["severityLevel"] == HIGH:
            days = config["issues"]["wiz"]["high"]
        else:
            days = config["issues"]["wiz"]["low"]
        days = int(days)
        issue["dueDate"] = (
            datetime.datetime.now() + datetime.timedelta(days=days)
        ).strftime(fmt)
        if issue["title"] not in {iss.title for iss in existing_regscale_issues}:
            new_issues.append(issue)
    return new_issues


@wiz.command()
def threats():
    """Process threats from Wiz -> Coming soon"""
    check_license()
    logger.info("Threats - COMING SOON")


@wiz.command()
def vulnerabilities():
    """Process vulnerabilities from Wiz -> Coming soon"""
    check_license()
    logger.info("Vulnerabilities - COMING SOON")


def fetch_report_id(app: Application, query, variables, url) -> str:
    """
    Fetch report ID from Wiz

    :param app: Application instance
    :param query: Query string
    :param variables: Variables
    :param url: Wiz URL
    :return: Wiz ID
    """
    try:
        resp = send_request(
            app=app,
            query=query,
            variables=variables,
            api_endpoint_url=url,
        )
        if "error" in resp.json().keys():
            error_and_exit(f'Wiz Error: {resp.json()["error"]}')
        return resp.json()["data"]["createReport"]["report"]["id"]
    except (requests.RequestException, AttributeError, TypeError) as rex:
        logger.error("Unable to pull report id from requests object\n%s", rex)
    return ""


def get_framework_names(wiz_frameworks) -> list:
    """
    Get the names of frameworks and replace spaces with underscores.

    :param wiz_frameworks: List of Wiz frameworks.
    :return: List of framework names.
    :rtype: list
    """
    return [framework["name"].replace(" ", "_") for framework in wiz_frameworks]


def check_reports_for_frameworks(reports, frames) -> bool:
    """
    Check if any reports contain the given frameworks.

    :param reports: List of reports.
    :param frames: List of framework names.
    :return: Boolean indicating if any report contains a framework.
    """
    return any(frame in item["name"] for item in reports for frame in frames)


def prompt_for_framework_selection(frames) -> str:
    """
    Prompt the user to select a framework and return the selected framework.

    :param frames: List of framework names.
    :return: Selected framework.
    :rtype: str
    """
    for i, frame in enumerate(frames):
        logger.info(f"{i}: {frame}")
    prompt = "Please enter the number of the framework that you would like to link to this project's wiz issues"
    value = click.prompt(prompt, type=int)
    assert (
        0 <= value < len(frames)
    ), f"Please enter a valid number between 0 and {len(frames)-1}"
    return frames[value]


def create_report_if_needed(
    app, wiz_project_id, frames, wiz_frameworks, reports, snake_framework
) -> list:
    """
    Create a report if needed and return report IDs.

    :param app: Application instance.
    :param wiz_project_id: Wiz Project ID.
    :param frames: List of framework names.
    :param wiz_frameworks: List of Wiz frameworks.
    :param reports: List of reports.
    :param snake_framework: Framework name with spaces replaced by underscores.
    :return: List of Wiz report IDs.
    :rtype: list
    """
    if not check_reports_for_frameworks(reports, frames):
        selected_frame = snake_framework
        selected_index = frames.index(selected_frame)
        wiz_framework = wiz_frameworks[selected_index]
        wiz_report_id = create_compliance_report(
            app=app,
            wiz_project_id=wiz_project_id,
            report_name=f"{selected_frame}_project_{wiz_project_id}",
            framework_id=wiz_framework.get("id"),
        )
        logger.info(f"Wiz compliance report created with ID {wiz_report_id}")
        return [wiz_report_id]

    return [
        report["id"]
        for report in reports
        if any(frame in report["name"] for frame in frames)
    ]


def fetch_and_process_report_data(app: Application, wiz_report_ids):
    """
    Fetch and process report data from report IDs.

    :param Application app: Application instance.
    :param wiz_report_ids: List of Wiz report IDs.
    :return: List of processed report data.
    """
    report_data = []
    for wiz_report in wiz_report_ids:
        download_url = get_report_url_and_status(app, wiz_report)
        logger.debug(f"Download url: {download_url}")
        with closing(requests.get(url=download_url, stream=True, timeout=10)) as data:
            logger.info("Download URL fetched. Streaming and parsing report")
            reader = csv.DictReader(
                codecs.iterdecode(data.iter_lines(), encoding="utf-8"), delimiter=","
            )
            for row in reader:
                report_data.append(row)
    return report_data


def fetch_framework_report(
    app: Application, wiz_project_id: str, snake_framework: str
) -> List[Any]:
    """
    Fetch Framework Report from Wiz.

    :param Application app: Application instance.
    :param str wiz_project_id: Wiz Project ID.
    :param str snake_framework: Framework name with spaces replaced by underscores.
    :return: List containing the framework report data.
    :rtype: List[Any]
    """
    wiz_frameworks = fetch_frameworks(app)
    frames = get_framework_names(wiz_frameworks)
    reports = list(query_reports(app))

    wiz_report_ids = create_report_if_needed(
        app, wiz_project_id, frames, wiz_frameworks, reports, snake_framework
    )
    return fetch_and_process_report_data(app, wiz_report_ids)


def fetch_frameworks(app: Application) -> list:
    """
    Fetch frameworks from Wiz

    :param Application app: Application Instance
    :raises General Error: If error in API response
    :return: List of frameworks
    :rtype: list
    """
    query = """
        query SecurityFrameworkAutosuggestOptions($policyTypes: [SecurityFrameworkPolicyType!], 
        $onlyEnabledPolicies: Boolean) {
      securityFrameworks(
        first: 500
        filterBy: {policyTypes: $policyTypes, enabled: $onlyEnabledPolicies}
      ) {
        nodes {
          id
          name
        }
      }
    }
    """
    variables = {
        "policyTypes": "CLOUD",
        "first": 500,
    }
    resp = send_request(
        app=app,
        query=query,
        variables=variables,
        api_endpoint_url=app.config["wizUrl"],
    )

    if resp.ok:
        # ["data"]["securityFrameworks"]["nodes"]
        data = resp.json()
        return data.get("data").get("securityFrameworks").get("nodes")
    else:
        error_and_exit(
            f"Wiz Error: {resp.status_code if resp else None} - {resp.text if resp else 'No response'}"
        )
        return []


def create_or_update_inventory_report(
    app: Application,
    url: str,
    rpts: List[dict],
    report_prefix: str,
    wiz_project_id: str,
) -> list[str]:
    """
    Create Wiz inventory report

    :param Application app: Application instance
    :param str url: URL String
    :param List[dict] rpts: reports from Wiz
    :param str report_prefix: Prefix of Wiz report
    :param str wiz_project_id: Wiz project ID
    :return: List of Wiz report IDs
    :rtype: list[str]
    """
    update_wiz_inv_report_config(app, 0, rpts)
    report_ids = []
    entities = update_wiz_config_entities(app)
    for entity in entities:
        logger.info(entity)
        report_name = f"{report_prefix}_{entity}"
        report_variables = {
            "input": {
                "name": report_name,
                "type": "CLOUD_RESOURCE",
                "projectId": wiz_project_id,
                "compressionMethod": "GZIP",
                "cloudResourceParams": {
                    "includeCloudNativeJSON": True,
                    "includeWizJSON": True,
                    "entityType": [entity],
                    "cloudPlatform": [
                        "AWS",
                        "Azure",
                        "GCP",
                        "OCI",
                        "AKS",
                        "EKS",
                        "Kubernetes",
                        "GKE",
                        "OpenShift",
                        "OKE",
                        "Alibaba",
                        "vSphere",
                    ],
                },
            }
        }

        try:
            wiz_report_id = get_report_id_from_response(
                app, report_name, report_variables, url
            )
            report_ids.append(wiz_report_id)
        except Exception as e:
            # Handle/report the error as appropriate
            logger.info(f"Error processing report: {e}")

    if not report_ids:
        report_ids = app.config.get(
            "wizInventoryReportId", [report["id"] for report in rpts]
        )

    update_config(app, report_ids)
    return report_ids


def get_report_id_from_response(
    app: Application, report_name: str, report_variables: dict, url: str
) -> str:
    """
    Get report ID from response

    :param Application app: Application instance
    :param str report_name: Wiz report name
    :param dict report_variables: Wiz report variables
    :param str url: URL String
    :return: Wiz report ID
    :rtype: str
    """
    try:
        while True:  # infinite loop
            wiz_inv_resp = send_request(
                app=app,
                query=CREATE_REPORT_QUERY,
                variables=report_variables,
                api_endpoint_url=url,
            )
            if (
                "errors" in wiz_inv_resp.json().keys()
                and RATE_LIMIT_MSG in wiz_inv_resp.json()["errors"][0]["message"]
            ):
                logger.debug(
                    "Sleeping %f",
                    wiz_inv_resp.json()["errors"][0]["extensions"]["retryAfter"],
                )
                time.sleep(wiz_inv_resp.json()["errors"][0]["extensions"]["retryAfter"])
                continue
            wiz_report_id = wiz_inv_resp.json()["data"]["createReport"]["report"]["id"]
            if wiz_report_id:
                break
            logger.info("Successfully created %s", report_name)
    except (requests.RequestException, AttributeError, TypeError) as rex:
        error_and_exit(
            f"Unable to pull report id from requests object\n{rex}\n{wiz_inv_resp.json()}"
        )
    return wiz_report_id


def update_wiz_inv_report_config(
    app: Application, entities_available: int, rpts: List[dict]
):
    """
    Update Wiz inventory report config

    :param Application app: Application instance
    :param int entities_available: Number of entities available
    :param List[dict] rpts: Reports from Wiz
    """
    if rpts:
        entities_available = sorted(
            [
                int(report["name"][-3:-1])
                for report in rpts
                if report["name"][-3:-1].isnumeric()
            ]
        ).pop()
    if (
        "wizInventoryReportId" in app.config
        and isinstance(app.config["wizInventoryReportId"], list)
        and len(app.config["wizInventoryReportId"]) != len(rpts)
    ):
        app.config["wizInventoryReportId"] = []
        for report in rpts:
            app.config["wizInventoryReportId"].append(report["id"])
        app.save_config(app.config)
    return entities_available


def update_wiz_config_entities(app: Application) -> list[str]:
    """
    Update config entities

    :param Application app: Application instance
    :return: List of entities
    :rtype: list[str]
    """
    if "wizEntities" not in app.config.keys() or not app.config["wizEntities"]:
        entities = [
            "CONTAINER",
            "CONTAINER_IMAGE",
            "DATABASE",
            "DATABASE_SERVER",
            "DB_SERVER",
            "DOMAIN",
            "FILE_SYSTEM_SERVICE",
            "FIREWALL",
            "GATEWAY",
            "IP_RANGE",
            "KUBERNETES_CLUSTER",
            "VIRTUAL_DESKTOP",
            "VIRTUAL_MACHINE",
            "VIRTUAL_MACHINE_IMAGE",
        ]
        app.config["wizEntities"] = list(entities)
        app.save_config(app.config)
    else:
        entities = app.config["wizEntities"]
    return entities


def update_config(app: Application, report_ids: list[str]) -> None:
    """Update init.yaml

    :param Application app: Application instance
    :param list[str] report_ids: list of report ids
    :return: None
    """
    app.config["wizInventoryReportId"] = report_ids
    app.save_config(app.config)


def create_issues_report(
    app: Application,
    url: str,
    report_name: str,
    wiz_project_id: str,
    issues_severity: list,
) -> str:
    """
    Create Wiz Issues Report

    :param Application app: Application instance
    :param str url: URL String
    :param str report_name: Wiz report name
    :param str wiz_project_id: Wiz project ID
    :param list issues_severity: Severity of Wiz issues
    :return: Wiz report ID
    :rtype: str
    """
    config = app.config
    report_issue_status = ["OPEN", "IN_PROGRESS"]
    report_type = "DETAILED"  # Possible values: "STANDARD", "DETAILED"
    report_variables = {
        "input": {
            "name": report_name,
            "type": "ISSUES",
            "projectId": wiz_project_id,
            "issueParams": {
                "type": report_type,
                "issueFilters": {
                    "severity": issues_severity,
                    "status": report_issue_status,
                },
            },
        }
    }
    try:
        wiz_report_id = fetch_report_id(app, CREATE_REPORT_QUERY, report_variables, url)
        if "wizIssuesReportId" not in config:
            config["wizIssuesReportId"] = []
            config["wizIssuesReportId"]["report_id"] = None
            config["wizIssuesReportId"]["last_seen"] = None
            app.save_config(config)
        if wiz_report_id:
            config["wizIssuesReportId"]["report_id"] = wiz_report_id
            config["wizIssuesReportId"]["last_seen"] = get_current_datetime()
            app.save_config(config)
    except AttributeError as aex:
        logger.error("Unable to pull report id from requests object\n%s", aex)
    if not wiz_report_id:
        error_and_exit(
            "Unable to find wiz report id associated with this project number, please check your Wiz Project ID."
        )
    return wiz_report_id


def map_category(asset_string: str) -> str:
    """
    category mapper

    :param str asset_string:
    :return: Category
    :rtype: str
    """
    try:
        return getattr(AssetCategory, asset_string).value
    except (KeyError, AttributeError) as ex:
        logger.warning("Unable to find %s in AssetType enum \n", ex)
        return "Software"


def query_reports(app: Application) -> list:
    """
    Query Report table from Wiz

    :param Application app: RegScale Application instance
    :return: list object from an API response from Wiz
    :rtype: list
    """
    query = """
        query ReportsTable($filterBy: ReportFilters, $first: Int, $after: String) {
          reports(first: $first, after: $after, filterBy: $filterBy) {
            nodes {
              id
              name
              type {
                id
                name
              }
              project {
                id
                name
              }
              emailTarget {
                to
              }
              parameters {
                query
                framework {
                  name
                }
                subscriptions {
                  id
                  name
                  type
                }
                entities {
                  id
                  name
                  type
                }
              }
              lastRun {
                ...LastRunDetails
              }
              nextRunAt
              runIntervalHours
            }
            pageInfo {
              hasNextPage
              endCursor
            }
            totalCount
          }
        }
        
            fragment LastRunDetails on ReportRun {
          id
          status
          failedReason
          runAt
          progress
          results {
            ... on ReportRunResultsBenchmark {
              errorCount
              passedCount
              failedCount
              scannedCount
            }
            ... on ReportRunResultsGraphQuery {
              resultCount
              entityCount
            }
            ... on ReportRunResultsNetworkExposure {
              scannedCount
              publiclyAccessibleCount
            }
            ... on ReportRunResultsConfigurationFindings {
              findingsCount
            }
            ... on ReportRunResultsVulnerabilities {
              count
            }
            ... on ReportRunResultsIssues {
              count
            }
          }
        }
    """

    # The variables sent along with the above query
    variables = {"first": 100, "filterBy": {}}

    res = send_request(
        app,
        query=query,
        variables=variables,
        api_endpoint_url=app.config["wizUrl"],
    )
    try:
        if "errors" in res.json().keys():
            error_and_exit(f'Wiz Error: {res.json()["errors"]}')

        result = res.json()["data"]["reports"]["nodes"]
    except requests.JSONDecodeError:
        error_and_exit(
            f"Unable to fetch reports from Wiz: {res.status_code}, {res.reason}"
        )
    return result


def send_request(
    app: Application,
    query: str,
    variables: dict,
    api_endpoint_url: Optional[str] = None,
) -> requests.Response:
    """
    Send a graphQL request to Wiz.

    :param Application app:
    :param str query: Query to use for GraphQL
    :param dict variables:
    :param str api_endpoint_url: Wiz GraphQL URL
    :raises: General Exception if the access token is missing from wizAccessToken in init.yaml
    :return: response from post call to provided api_endpoint_url
    :rtype: requests.Response
    """
    logger.debug("Sending a request to Wiz API")
    api = Api()
    payload = dict({"query": query, "variables": variables})
    if api_endpoint_url is None:
        api_endpoint_url = app.config["wizUrl"]
    if app.config["wizAccessToken"]:
        return api.post(
            url=api_endpoint_url,
            headers={
                "Content-Type": CONTENT_TYPE,
                "Authorization": "Bearer " + app.config["wizAccessToken"],
            },
            json=payload,
        )
    raise ValueError("An access token is missing.")


def rerun_report(app: Application, report_id: str) -> str:
    """
    Rerun a Wiz Report

    :param Application app: Application instance
    :param str report_id: report id
    :return: Wiz report ID
    :rtype: str
    """
    rerun_report_query = """
        mutation RerunReport($reportId: ID!) {
            rerunReport(input: { id: $reportId }) {
                report {
                    id
                }
            }
        }
    """
    variables = {"reportId": report_id}
    rate = 0.5
    while True:
        response = send_request(app, query=rerun_report_query, variables=variables)
        content_type = response.headers.get("content-type")
        if content_type and CONTENT_TYPE in content_type:
            if "errors" in response.json():
                if RATE_LIMIT_MSG in response.json()["errors"][0]["message"]:
                    rate = response.json()["errors"][0]["extensions"]["retryAfter"]
                    time.sleep(rate)
                    continue
                error_info = response.json()["errors"]
                variables_info = variables
                query_info = rerun_report_query
                error_and_exit(
                    f"Error info: {error_info}\nVariables:{variables_info}\nQuery:{query_info}"
                )
            report_id = response.json()["data"]["rerunReport"]["report"]["id"]
            logger.info("Report was re-run successfully. Report ID: %s", report_id)
            break
        time.sleep(rate)
    config = app.config
    config.setdefault("wizIssuesReportId", {})
    config["wizIssuesReportId"]["report_id"] = report_id
    config["wizIssuesReportId"]["last_seen"] = get_current_datetime()
    app.save_config(config)
    return report_id


def create_compliance_report(
    app: Application,
    report_name: str,
    wiz_project_id: str,
    framework_id: str,
) -> str:
    """Create Wiz compliance report

    :param Application app: Application instance
    :param str url: Wiz URL
    :param str report_name: Report name
    :param str wiz_project_id: Wiz Project ID
    :param str framework_id: Wiz Framework ID
    :return: Compliance Report id
    :rtype: str
    """
    report_variables = {
        "input": {
            "name": report_name,
            "type": "COMPLIANCE_ASSESSMENTS",
            "csvDelimiter": "US",
            "projectId": wiz_project_id,
            "complianceAssessmentsParams": {"securityFrameworkIds": [framework_id]},
            "emailTargetParams": None,
            "exportDestinations": None,
        }
    }

    return fetch_report_id(
        app, CREATE_REPORT_QUERY, report_variables, url=app.config["wizUrl"]
    )


def get_report_url_and_status(app: Application, report_id: str) -> str:
    """
    Generate Report URL from Wiz report

    :param Application app: Application instance
    :param str report_id: Wiz report ID
    :raises: requests.RequestException if download failed and exceeded max # of retries
    :return: URL of report
    :rtype: str
    """
    num_of_retries = 0
    while num_of_retries < MAX_RETRIES:
        variables = {"reportId": report_id}
        if num_of_retries > 0:
            logger.info(
                "Report %s is still updating, waiting %.2f seconds",
                report_id,
                CHECK_INTERVAL_FOR_DOWNLOAD_REPORT,
            )
            time.sleep(CHECK_INTERVAL_FOR_DOWNLOAD_REPORT)
        response = download_report(app, variables)
        response_json = response.json()
        if "errors" in response_json.keys():
            try:
                if RATE_LIMIT_MSG in response_json.json()["errors"][0]["message"]:
                    rate = response.json()["errors"][0]["extensions"]["retryAfter"]
                    time.sleep(rate)  # Give a bit of extra time, this is threaded.
                    logger.warning("Sleeping %i", rate)
                    continue
                logger.error(response_json["errors"])
            except AttributeError:
                continue
        status = response_json["data"]["report"]["lastRun"]["status"]
        if status == "COMPLETED":
            return response_json["data"]["report"]["lastRun"]["url"]
        num_of_retries += 1
    raise requests.RequestException(
        "Download failed, exceeding the maximum number of retries"
    )


def download_report(app: Application, variables) -> requests.Response:
    """
    Return a download URL for a provided Wiz report id

    :param Application app: Application instance
    :param variables: Variables for Wiz request
    :return: response from Wiz API
    :rtype: requests.Response
    """
    download_query = """
    query ReportDownloadUrl($reportId: ID!) {
        report(id: $reportId) {
            lastRun {
                url
                status
            }
        }
    }
    """
    response = send_request(app, download_query, variables=variables)
    return response


def get_asset_by_external_id(
    wiz_external_id: str, existing_ssp_assets: list[Asset]
) -> Optional[Asset]:
    """
    Returns a single asset by the wiz external ID

    :param str wiz_external_id: Wiz external ID
    :return: Asset if found, else None
    :rtype: Optional[Asset]
    """
    asset = None
    for existing_ssp_asset in existing_ssp_assets:
        if existing_ssp_asset["wizId"] == wiz_external_id:
            asset = existing_ssp_asset
    return asset


def deduplicate_issues(regscale_issues_from_wiz: List[Issue]) -> List[Issue]:
    """
    Deduplicate issues.

    :param List[Issue] regscale_issues_from_wiz: Application configuration
    :return: list of RegScale issues
    :rtype: list[Issue]
    """

    def convert_to_date(date_string: str) -> datetime.datetime:
        """
        Convert date string to datetime

        :param str date_string: Date string
        :return: datetime
        :rtype: datetime.datetime
        """
        return datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

    deduped_issues = []
    unique_titles = {d.title for d in regscale_issues_from_wiz}
    for title in unique_titles:
        # Group by title
        issues = [d for d in regscale_issues_from_wiz if d.title == title]
        wiz_data = [json.loads(iss.description) for iss in issues]
        min_first_seen = min(
            wiz_data, key=lambda x: convert_to_date(x["date_first_seen"])
        )["date_first_seen"]
        max_last_seen = max(
            wiz_data, key=lambda x: convert_to_date(x["date_last_seen"])
        )["date_last_seen"]
        control_ids = list({dat["control_id"] for dat in wiz_data})
        wiz_ids = list({dat["issue_id"] for dat in wiz_data})
        description_data = wiz_data[0]
        description_data["date_first_seen"] = min_first_seen
        description_data["date_last_seen"] = max_last_seen
        description_data["control_id"] = ", ".join(control_ids)
        description_data["issue_id"] = ", ".join(wiz_ids)
        description = convert_description(description_data)
        for issue in issues:
            if issue.title not in {iss.title for iss in deduped_issues}:
                issue.description = description
                deduped_issues.append(issue)
    return deduped_issues


def convert_description(description_data: dict) -> str:
    """
    Convert description data dictionary to a string

    :param dict description_data: Description data dictionary
    :return: Description string
    :rtype: str
    """
    return f"""<strong>Wiz Control ID: </strong>{description_data['control_id']}<br/>\
                    <strong>Wiz Issue ID: </strong>{description_data['issue_id']}<br/>\
                    <strong>Asset Type: </strong>{description_data['asset_type']}<br/>
                    <strong>Severity: </strong>{description_data['severity']}<br/> \
                    <strong>Date First Seen: </strong>{description_data['date_first_seen']}<br/>\
                    <strong>Date Last Seen: </strong>{description_data['date_last_seen']}<br/>\
                    <strong>Description: </strong>{description_data['description']}<br/>\
                    """


def fetch_wiz_issues(
    download_url: str,
    regscale_id: int,
    regscale_module: str = "securityplans",
) -> list[Issue]:
    """
    Read Stream of CSV data from a URL and process to RegScale Issues.

    :param str download_url: WIZ download URL
    :param int regscale_id: ID # for RegScale record
    :param str regscale_module: RegScale module, defaults to securityplans
    :return: list of RegScale issues
    :rtype: list[Issue]
    """
    app = Application()

    regscale_issues_from_wiz = []
    header = []
    existing_ssp_assets = Asset.find_assets_by_parent(
        app=app, parent_id=regscale_id, parent_module="securityplans"
    )
    with closing(requests.get(url=download_url, stream=True, timeout=10)) as data:
        logger.info("Download URL fetched. Streaming and parsing report")
        reader = csv.reader(codecs.iterdecode(data.iter_lines(), encoding="utf-8"))
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            for row in reader:
                logger.debug(row)
                if reader.line_num == 1:
                    header = row
                    continue
                args = (
                    row,
                    header,
                    app.config,
                    regscale_id,
                    regscale_module,
                    existing_ssp_assets,
                )
                futures.append(executor.submit(process_row, args))
            for future in as_completed(futures):
                regscale_issues_from_wiz.append(future.result())

    regscale_issues_from_wiz = deduplicate_issues(regscale_issues_from_wiz)
    logger.info(
        "Found %i Wiz Issues to update or insert into RegScale",
        len(regscale_issues_from_wiz),
    )
    return regscale_issues_from_wiz


def _build_due_date(days: int, today_date: str, date_format: str) -> datetime:
    """
    Function to add days to today_date and return a datetime object

    :param int days: Number of days to add
    :param str today_date: Today's date as a string
    :param str date_format: Date format as a string
    :return:
    """
    return datetime.datetime.strptime(today_date, date_format) + datetime.timedelta(
        days=days
    )


def process_row(*args) -> Issue:
    """
    Process row from Wiz report

    :param args: Variable length argument list.
    :return: RegScale Issue
    :rtype: Issue
    """
    row, header, config, module_id, module, existing_ssp_assets = args[0]
    logger.debug(row)
    title = row[header.index("Title")]
    first_seen = convert_datetime_to_regscale_string(
        datetime.datetime.strptime(
            row[header.index("Created At")], "%Y-%m-%dT%H:%M:%SZ"
        )
    )

    last_seen = config["wizIssuesReportId"]["last_seen"]
    date_format = "%m/%d/%y"
    status = row[header.index("Status")]
    severity = row[header.index("Severity")]
    today_date = date.today().strftime(date_format)
    # handle parent assignments for deep linking
    int_security_plan_id = 0
    int_component_id = 0
    int_project_id = 0
    int_supply_chain_id = 0
    if module == "projects":
        int_project_id = module_id
    elif module == "supplychain":
        int_supply_chain_id = module_id
    elif module == "components":
        int_component_id = module_id
    elif module == "securityplans":
        int_security_plan_id = module_id
    if severity == "LOW":
        days = check_config_for_issues(config=config, issue="wiz", key="low")
        str_severity = LOW
        due_date = _build_due_date(
            days=days, today_date=today_date, date_format=date_format
        )
    elif severity == "MEDIUM":
        days = check_config_for_issues(config=config, issue="wiz", key="medium")
        str_severity = MODERATE
        due_date = _build_due_date(
            days=days, today_date=today_date, date_format=date_format
        )
    elif severity == "HIGH":
        days = check_config_for_issues(config=config, issue="wiz", key="high")
        str_severity = MODERATE
        due_date = _build_due_date(
            days=days, today_date=today_date, date_format=date_format
        )
    elif severity == "CRITICAL":
        days = check_config_for_issues(config=config, issue="wiz", key="critical")
        str_severity = HIGH
        due_date = _build_due_date(
            days=days, today_date=today_date, date_format=date_format
        )
    else:
        logger.error("Unknown Wiz severity level: %s", severity)

    issue_row = row[header.index("Issue ID")]
    # Park description data, will build this description field later
    description_data = {
        "control_id": row[header.index("Control ID")],
        "issue_id": issue_row,
        "asset_type": row[header.index(RESOURCE)],
        "severity": severity,
        "date_first_seen": first_seen,
        "date_last_seen": last_seen,
        "description": row[header.index("Description")],
    }

    wiz_asset_external_id = row[header.index("Resource external ID")]
    linked_asset = get_asset_by_external_id(
        wiz_asset_external_id, existing_ssp_assets=existing_ssp_assets
    )

    issue = Issue(
        title=title,
        dateCreated=first_seen,
        status=capitalize_words(status),
        uuid=issue_row,
        securityChecks=row[header.index("Description")],
        severityLevel=str_severity,
        issueOwnerId=config["userId"],
        supplyChainId=int_supply_chain_id,
        securityPlanId=int_security_plan_id,
        projectId=int_project_id,
        componentId=int_component_id,
        # Defaults to SSP if no asset id is linked
        parentId=linked_asset.id if linked_asset else module_id,
        parentModule="assets" if linked_asset else module,
        identification="Security Control Assessment",
        dueDate=convert_datetime_to_regscale_string(due_date),
        wizId=issue_row,
        description=json.dumps(description_data),
        recommendedActions=row[header.index("Remediation Recommendation")],
    )
    return issue


def check_module_id(parent_id: int, parent_module: str) -> bool:
    """
    Verify object exists in RegScale

    :param int parent_id: RegScale parent ID
    :param str parent_module: RegScale module
    :return: True or False if the object exists in RegScale
    :rtype: bool
    """
    res = False
    api = Api()
    # increase timeout to match GraphQL timeout in the application
    api.timeout = 30
    try:
        key = Modules().graphql_names()[parent_module]
    except KeyError:
        logger.warning("Unable to find %s in Modules", parent_module)
        return res
    body = """
    query {
        NAMEOFTABLE(take: 50, skip: 0, where: {id: {eq: PARENTID}}) {
          items {
            id
          },
          pageInfo {
            hasNextPage
          }
          ,totalCount 
        }
    }
        """.replace(
        "NAMEOFTABLE", key
    ).replace(
        "PARENTID", str(parent_id)
    )
    logger.debug(f"Using query: {body}")
    if items := _try_query(api, body):
        try:
            return items[key]["totalCount"] > 0
        except (KeyError, TypeError):
            return False
        except TimeoutError as exc:
            # this is an exception that is raised by the _try_query function
            logger.error(f"TimeoutError: {exc}")
            # we have left it in here for Airflow to fail if this happens
            raise exc
    return False


def _try_query(api: Api, query: str, retries: int = 5, delay: int = 15):
    """Try to query the API

    :param api: API instance
    :param query: Query to run
    :param retries: Number of retries
    :param delay: Delay between retries
    :return: Query results
    """
    while retries > 0:
        try:
            items = api.graph(query=query)
            logger.debug(f"items retrieved: {items}")
            if any(value is None for value in items.values()):
                raise ValueError("items is None")
            return items
        except Exception as e:
            logger.exception(f"Exception occurred while checking module id: {e}")
            retries -= 1
            time.sleep(delay)
            return _try_query(api, query, retries, delay)
    raise TimeoutError("Unable to query the API")


@wiz.command("sync_compliance")
@click.option(
    "--wiz_project_id",
    "-p",
    prompt="Enter the Wiz project ID",
    help="Enter the Wiz Project ID.  Options include: projects, \
          policies, supplychain, securityplans, components.",
    required=True,
)
@regscale_id(help="RegScale will create and update issues as children of this record.")
@regscale_module()
@click.option(
    "--client_id",
    "-i",
    help="Wiz Client ID. Can also be set as an environment variable: WIZ_CLIENT_ID",
    default=os.environ.get("WIZ_CLIENT_ID"),
    hide_input=False,
    required=False,
)
@click.option(
    "--client_secret",
    "-s",
    help="Wiz Client Secret. Can also be set as an environment variable: WIZ_CLIENT_SECRET",
    default=os.environ.get("WIZ_CLIENT_SECRET"),
    hide_input=True,
    required=False,
)
@click.option(
    "--catalog_id",
    "-c",
    help="RegScale Catalog ID for the selected framework.",
    prompt="RegScale Catalog ID",
    hide_input=False,
    required=True,
)
@click.option(
    "--framework",
    "-f",
    type=click.Choice(["CSF", "NIST800-53R5", "NIST800-53R4"], case_sensitive=False),
    help="Choose either one of the Frameworks",
    default="NIST800-53R5",
    required=True,
)
@click.option(
    "--include_not_implemented",
    "-n",
    is_flag=True,
    help="Include not implemented controls",
    default=False,
)
def sync_compliance(
    wiz_project_id,
    regscale_id,
    regscale_module,
    client_id,
    client_secret,
    catalog_id,
    framework,
    include_not_implemented,
):
    """Sync compliance posture from Wiz to RegScale"""
    with compliance_job_progress:
        _sync_compliance(
            wiz_project_id=wiz_project_id,
            regscale_id=regscale_id,
            regscale_module=regscale_module,
            client_id=client_id,
            client_secret=client_secret,
            catalog_id=catalog_id,
            framework=framework,
            include_not_implemented=include_not_implemented,
        )


def _sync_compliance(
    wiz_project_id: str,
    regscale_id: int,
    regscale_module: str,
    include_not_implemented: bool,
    client_id: str,
    client_secret: str,
    catalog_id: int,
    framework: Optional[str] = "NIST800-53R5",
) -> List[ComplianceReport]:
    """
    Sync compliance posture from Wiz to RegScale

    :param str wiz_project_id: Wiz Project ID
    :param int regscale_id: RegScale ID
    :param str regscale_module: RegScale module
    :param str client_id: Wiz Client ID
    :param str client_secret: Wiz Client Secret
    :param int catalog_id: Catalog ID, defaults to None
    :param Optional[str] framework: Framework, defaults to NIST800-53R5
    :param include_not_implemented: Include not implemented controls
    :return: List of ComplianceReport objects
    :rtype: List[ComplianceReport]
    """

    app = Application()
    logger.info("Syncing compliance from Wiz with project ID %s", wiz_project_id)
    wiz_authenticate(
        client_id=client_id,
        client_secret=client_secret,
    )
    report_job = compliance_job_progress.add_task(
        "[#f68d1f]Fetching Wiz compliance report...", total=1
    )
    fetch_regscale_data_job = compliance_job_progress.add_task(
        "[#f68d1f]Fetching RegScale Catalog info for framework...", total=1
    )
    logger.info("Fetching Wiz compliance report for project ID %s...", wiz_project_id)
    compliance_job_progress.update(report_job, completed=True, advance=1)

    framework_mapping = {
        "CSF": "NIST CSF v1.1",
        "NIST800-53R5": "NIST SP 800-53 Revision 5",
        "NIST800-53R4": "NIST SP 800-53 Revision 4",
    }
    sync_framework = framework_mapping.get(framework)
    snake_framework = sync_framework.replace(" ", "_")
    logger.info(snake_framework)
    logger.info("Fetching Wiz compliance report for project ID %s", wiz_project_id)
    report_data = fetch_framework_report(app, wiz_project_id, snake_framework)
    report_models = []
    compliance_job_progress.update(report_job, completed=True, advance=1)

    catalog = Catalog.get_with_all_details(id=catalog_id)
    controls = catalog.get("controls")
    passing_controls = dict()
    failing_controls = dict()
    controls_to_reports = dict()
    existing_implementations = (
        ControlImplementation.get_existing_control_implementations(
            parent_id=regscale_id
        )
    )
    compliance_job_progress.update(fetch_regscale_data_job, completed=True, advance=1)
    logger.info(f"Analyzing ComplianceReport for framework {sync_framework} from Wiz")
    running_compliance_job = compliance_job_progress.add_task(
        "[#f68d1f]Building compliance posture from wiz report...",
        total=len(report_data),
    )
    for row in report_data:
        try:
            cr = ComplianceReport(**row)
            if cr.framework == sync_framework:
                check_compliance(
                    cr,
                    controls,
                    passing_controls,
                    failing_controls,
                    controls_to_reports,
                )
                report_models.append(cr)
                compliance_job_progress.update(running_compliance_job, advance=1)
        except ValidationError as e:
            logger.error(f"Error creating ComplianceReport: {e}")
    try:
        saving_regscale_data_job = compliance_job_progress.add_task(
            "[#f68d1f]Saving RegScale data...", total=1
        )
        ControlImplementation.create_control_implementations(
            controls=controls,
            parent_id=regscale_id,
            parent_module=regscale_module,
            existing_implementation_dict=existing_implementations,
            full_controls=passing_controls,
            partial_controls={},
            failing_controls=failing_controls,
            include_not_implemented=include_not_implemented,
        )
        create_assessment_from_compliance_report(
            controls_to_reports=controls_to_reports,
            regscale_id=regscale_id,
            regscale_module=regscale_module,
            controls=controls,
        )
        compliance_job_progress.update(
            saving_regscale_data_job, completed=True, advance=1
        )

    except Exception as e:
        logger.error(
            f"Error creating ControlImplementations from compliance report: {e}"
        )
        traceback.print_exc()
    return report_models


def create_assessment_from_compliance_report(
    controls_to_reports: Dict, regscale_id: int, regscale_module: str, controls: List
) -> None:
    """
    Create assessment from compliance report

    :param Dict controls_to_reports: Controls to reports
    :param int regscale_id: RegScale ID
    :param str regscale_module: RegScale module
    :param list controls: Controls
    :return: None
    """
    implementations = ControlImplementation.get_all_by_parent(
        parent_module=regscale_module, parent_id=regscale_id
    )
    for control_id, reports in controls_to_reports.items():
        control_record_id = None
        for control in controls:
            if control.get("controlId").lower() == control_id:
                control_record_id = control.get("id")
                break
        filtered_results = [
            x for x in implementations if x.controlID == control_record_id
        ]
        create_report_assessment(filtered_results, reports, control_id)


def create_report_assessment(
    filtered_results: List, reports: List, control_id: str
) -> None:
    """
    Create report assessment

    :param List filtered_results: Filtered results
    :param List reports: Reports
    :param str control_id: Control ID
    :return: None
    """
    implementation = filtered_results[0] if len(filtered_results) > 0 else None
    for report in reports:
        html_summary = format_dict_to_html(report.dict())
        if implementation:
            Assessment(
                leadAssessorId=implementation.createdById,
                title=f"Wiz compliance report assessment for {control_id}",
                assessmentType="Control Testing",
                plannedStart=get_current_datetime(),
                plannedFinish=get_current_datetime(),
                actualFinish=get_current_datetime(),
                assessmentResult=report.result,
                assessmentReport=html_summary,
                status="Complete",
                parentId=implementation.id,
                parentModule="controls",
                isPublic=True,
            ).create()


def check_compliance(
    cr: ComplianceReport,
    controls: List[Dict],
    passing: Dict,
    failing: Dict,
    controls_to_reports: Dict,
) -> None:
    """
    Check compliance report for against controls

    :param ComplianceReport cr: Compliance Report
    :param List controls: Controls List
    :param Dict passing: Passing controls
    :param Dict failing: Failing controls
    :param Dict controls_to_reports: Controls to reports
    :return: None
    """
    for control in controls:
        if f"{control.get('controlId').lower()} " in cr.compliance_check.lower():
            _add_controls_to_controls_to_report_dict(control, controls_to_reports, cr)
            if cr.result == ComplianceCheckStatus.PASS.value:
                if control.get("controlId").lower() not in passing:
                    passing[control.get("controlId").lower()] = control
            else:
                if control.get("controlId").lower() not in failing:
                    failing[control.get("controlId").lower()] = control
    _clean_passing_list(passing, failing)


def _add_controls_to_controls_to_report_dict(
    control: Dict, controls_to_reports: Dict, cr: ComplianceReport
) -> None:
    """
    Add controls to dict to process assessments from later

    :param Dict control: Control
    :param Dict controls_to_reports: Controls to reports
    :param ComplianceReport cr: Compliance Report
    :return: None
    """
    if control.get("controlId").lower() not in controls_to_reports.keys():
        controls_to_reports[control.get("controlId").lower()] = [cr]
    else:
        controls_to_reports[control.get("controlId").lower()].append(cr)


def _clean_passing_list(passing: Dict, failing: Dict) -> None:
    """
    Clean passing list. Ensures that controls that are passing are not also failing

    :param Dict passing: Passing controls
    :param Dict failing: Failing controls
    :return: None
    """
    for control_id in failing:
        if control_id in passing:
            passing.pop(control_id, None)
