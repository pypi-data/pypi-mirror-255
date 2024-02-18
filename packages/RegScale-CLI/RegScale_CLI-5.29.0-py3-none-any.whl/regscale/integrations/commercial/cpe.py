"""
This module contains functions for interacting with the NIST CPE API.
"""

from typing import List, Optional

import requests

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import error_and_exit

logger = create_logger()


def get_cpe_titles(search_str: str, lang: Optional[str] = "en") -> List[str]:
    """
    Get CPE titles from NIST CPE API for a given search string

    :param str search_str: the search string to use
    :param str lang: the language to use
    :return: a list of CPE titles
    :rtype: List[str]
    """
    api = Api()
    config = api.config
    api_key = config.get("nistCpeApiKey")
    if not api_key:
        error_and_exit("NIST CPE API key not found in config")
    headers = {"api_key": api_key}
    nist_api_url = (
        f"https://services.nvd.nist.gov/rest/json/cpes/2.0?cpeMatchString={search_str}"
    )
    response = requests.get(nist_api_url, headers=headers, timeout=10)
    cpe_names = []
    if response and response.ok:
        raw = response.json()
        logger.debug(raw)
        if "products" in raw:
            for product in raw["products"]:
                if "cpe" in product:
                    cpe = product.get("cpe")
                    names = [
                        name.get("title")
                        for name in cpe.get("titles")
                        if name.get("lang") == lang
                    ]
                    cpe_names.extend(names)
        return cpe_names
    return []


def get_cpe_title_by_version(cpe_title_list: List[str], version: str) -> Optional[str]:
    """
    Get CPE title from a list of CPE titles for a given version

    :param List[str] cpe_title_list: the list of CPE titles to use
    :param str version: the version to use
    :return: a CPE title
    :rtype: Optional[str]
    """
    for title in cpe_title_list:
        if version in title:
            return title
    return None


def get_cpe_title(cpe_name: str, version: str) -> Optional[str]:
    """
    Get CPE title from NIST CPE API for a given CPE name and version

    :param str cpe_name: the CPE name to use
    :param str version: the version to use
    :return: a CPE title
    :rtype: Optional[str]
    """
    try:
        cpe_title_list = get_cpe_titles(cpe_name)
        if cpe_title_list:
            return get_cpe_title_by_version(cpe_title_list, version)
        return None
    except requests.RequestException as ex:
        logger.error("Error getting CPE title: %s", ex)
        return None
