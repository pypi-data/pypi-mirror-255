#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Functions used throughout the application """

# standard python imports
import csv
import glob
import hashlib
import json
import math
import ntpath
import os
import platform
import random
import re
import sys
from collections import abc
from datetime import datetime
from logging import Logger
from pathlib import Path
from shutil import copytree, rmtree
from site import getusersitepackages
from tempfile import gettempdir
from typing import Any, Dict, Optional, Union
from urllib.parse import urlparse

import pandas as pd
import psutil
import requests
import xmltodict
from dateutil import relativedelta
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.internal.login import is_licensed
from regscale.core.app.logz import create_logger
from regscale.exceptions.license_exception import LicenseException

logger = create_logger()


def get_cross_platform_user_data_dir() -> Path:
    """
    Return the user data directory for the current platform

    :return: user data directory
    :rtype: Path
    """
    if sys.platform == "win32":
        return Path(os.getenv("APPDATA")) / "regscale"
    else:
        return Path.home() / ".config" / "regscale"


def check_license(config: Optional[dict] = None) -> Application:
    """
    Check RegScale license

    :param dict config: Config dictionary, defaults to None
    :raises: LicenseException if Application license isn't at the requested level of the feature
    :return: Application object
    """
    app = Application(config)
    if not is_licensed(app):
        raise LicenseException(
            "This feature is limited to RegScale Enterprise, please check RegScale license."
        )
    return app


def get_site_package_location() -> Path:
    """
    Return site package location as string

    :return: site package location
    :rtype: Path
    """
    return Path(getusersitepackages())


def creation_date(path_to_file) -> float:
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.

    :param str path_to_file: Path to the file
    :return: Date of creation
    :rtype: datetime
    """
    if platform.system() == "Windows":
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


def is_valid_fqdn(fqdn: str) -> bool:
    """
    Function to check if the provided fqdn is valid

    :param str fqdn: FQDN to check
    :return: True if valid, False if not
    :rtype: bool
    """
    fqdn_regex = r"^(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)*"
    fqdn_regex += r"(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|localhost)$"
    if re.match(fqdn_regex, fqdn, re.IGNORECASE):
        return True
    else:
        return False


def convert_datetime_to_regscale_string(
    reg_dt: datetime, dt_format: Optional[str] = "%Y-%m-%d %H:%M:%S"
):
    """
    Convert a datetime object to a RegScale API friendly string
    :param datatime reg_dt: Datetime object
    :param Optional[str] dt_format: Defaults to "%Y-%m-%d %H:%M:%S".
    :return: RegScale datetime string
    :rtype: str
    """
    return reg_dt.strftime(dt_format)


def reformat_str_date(date_str: str, dt_format: str = "%m/%d/%Y") -> str:
    """
    Function to convert a string into a datetime object and reformat it to dt_format, default \
        format is MM/DD/YYYY

    :param str date_str: date as a string
    :param str dt_format: datetime string format, defaults to "%m/%d/%Y"
    :return: string with the provided date format
    :rtype: str
    """
    # replace the T with a space and create list of result
    date_str = date_str.replace("T", " ").split(" ")

    return datetime.strptime(date_str[0], "%Y-%m-%d").strftime(dt_format)


def pretty_short_str(long_str: str, start_length: int, end_length: int) -> str:
    """
    Function to convert long string to shortened string

    :param str long_str: long string to shorten
    :param int start_length: number of characters to use from string start
    :param int end_length: number of characters to use from string end
    :return: attractive short string of form 'start..end'
    :rtype: str
    """
    return long_str[:start_length] + ".." + long_str[-end_length:]


def camel_case(text) -> str:
    """
    Function to convert known module to camel case... (GraphQL)

    :param text: _description_
    :return: _description_
    :rtype: str
    """
    # Split the input string into words using a regular expression
    words = [word for word in re.split(r"[\s_\-]+|(?<=[a-z])(?=[A-Z])", text) if word]
    # Make the first word lowercase, and capitalize the first letter of each subsequent word
    words[0] = words[0].lower()
    for i in range(1, len(words)):
        words[i] = words[i].capitalize()
    # Concatenate the words without spaces
    return "".join(words)


def snake_case(text: str) -> str:
    """
    Function to convert a string to snake_case

    :param str text: string to convert
    :return: string in snake_case
    :rtype: str
    """
    # Split the input string into words using a regular expression
    words = [word for word in re.split(r"[\s_\-]+|(?<=[a-z])(?=[A-Z])", text) if word]
    # Make the first word lowercase, and capitalize the first letter of each subsequent word
    words[0] = words[0].lower()
    for i in range(1, len(words)):
        words[i] = words[i].capitalize()
    # Concatenate the words without spaces
    return "_".join(words)


def uncamel_case(camel_str: str) -> str:
    """
    Function to convert camelCase strings to Title Case

    :param camel_str:
    :return: Title Case string from provided camelCase
    :rtype: str
    """
    # check to see if a string with data was passed
    if camel_str != "":
        # split at any uppercase letters
        result = re.sub("([A-Z])", r" \1", camel_str)

        # use title to Title Case the string and strip to remove leading
        # and trailing white spaces
        result = result.title().strip()
        return result
    return ""


def get_css(file_path: str) -> str:
    """
    Function to load the CSS properties from the given file_path

    :param str file_path: file path to the desired CSS file
    :return: CSS as a string
    :rtype: str
    """
    # create variable to store the string and return
    css = ""

    # check if the filepath exists before trying to open it
    if os.path.exists(file_path):
        # file exists so open the file
        with open(file_path, "r", encoding="utf-8") as file:
            # store the contents of the file in the css str variable
            css = file.read()
    # return the css variable
    return css


def epoch_to_datetime(
    epoch: str,
    epoch_type: str = "seconds",
    dt_format: Optional[str] = "%Y-%m-%d %H:%M:%S",
) -> str:
    """
    Return datetime from unix epoch

    :param str epoch: unix epoch
    :param str epoch_type: type of epoch, defaults to 'seconds'
    :param Optional[str] dt_format: datetime string format, defaults to "%Y-%m-%d %H:%M:%S"
    :return: datetime string
    :rtype: str
    """
    if epoch_type == "milliseconds":
        return datetime.fromtimestamp(int(epoch) / 1000).strftime(dt_format)
    return datetime.fromtimestamp(int(epoch)).strftime(dt_format)


def get_current_datetime(dt_format: Optional[str] = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Return current datetime

    :param Optional[str] dt_format: desired format for datetime string, defaults to "%Y-%m-%d %H:%M:%S"
    :return: Current datetime as a string
    :rtype: str
    """
    return datetime.now().strftime(dt_format)


def cci_control_mapping(file_path: Path) -> list:
    """
    Simple function to read csv artifact to help with STIG mapping

    :param Path file_path: file path to the csv artifact
    :return: List of the csv contents
    :rtype: list
    """
    with open(file_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        return list(reader)


def copy_and_overwrite(from_path: Path, to_path: Path) -> None:
    """
    Copy and overwrite files recursively in a given path

    :param Path from_path: Path to copy from
    :param Path to_path: Path to copy to
    :return: None
    """
    if os.path.exists(to_path):
        rmtree(to_path)
    copytree(from_path, to_path)


def create_progress_object() -> Progress:
    """
    Function to create and return a progress object

    :return: Progress object for live progress in console
    :rtype: Progress
    """
    return Progress(
        "{task.description}",
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    )


def get_file_type(file_name: str) -> str:
    """
    Function to get the file type of the provided file_path and returns it as a string

    :param str file_name: Path to the file
    :return: Returns string of file type
    :rtype: str
    """
    file_type = Path(file_name).suffix
    return file_type.lower()


def xml_file_to_dict(file_path: Path) -> dict:
    """
    Function to convert an XML file to a dictionary

    :param Path file_path: Path to the XML file
    :return: Dictionary of the XML file
    :rtype: dict
    """
    # create variable to store the dictionary
    xml_dict = {}

    # check if the file exists
    if os.path.exists(file_path):
        # file exists so open the file
        with open(file_path, "r", encoding="utf-8") as file:
            # store the contents of the file in the xml_dict variable
            xml_dict = xmltodict.parse(file.read())
    # return the xml_dict variable
    return xml_dict


def get_file_name(file_path: str) -> str:
    """
    Function to parse the provided file path and returns the file's name as a string

    :param str file_path: path to the file
    :return: File name
    :rtype: str
    """
    # split the provided file_path with ntpath
    directory, file_name = ntpath.split(file_path)
    # return the file_path or directory
    return file_name or ntpath.basename(directory)


def get_recent_files(file_path: Path, file_count: int, file_type: str = None) -> list:
    """
    Function to go to the provided file_path and get the x number of recent items
    optional argument of file_type to filter the directory

    :param Path file_path: Directory to get recent files in
    :param int file_count: # of files to return
    :param str file_type: file type to sort directory for, defaults to none
    :return: list of recent files in the provided directory
    :rtype: list
    """
    # verify the provided file_path exists
    if os.path.exists(file_path):
        # get the list of files from the provided path, get the desired
        # file_type if provided
        file_list = (
            glob.glob(f"{file_path}/*{file_type}")
            if file_type
            else glob.glob(f"{file_path}/*")
        )

        # sort the file_list by modified date in descending order
        file_list.sort(key=os.path.getmtime, reverse=True)

        # check if file_list has more items than the provided number, remove the rest
        if len(file_list) > file_count:
            file_list = file_list[:file_count]
    else:
        error_and_exit(f"The provided file path doesn't exist! Provided: {file_path}")
    # return the list of files
    return file_list


def check_config_for_issues(config, issue: str, key: str) -> Union[str, int, None]:
    """
    Function to check config keys

    :return: Value from config or None
    :rtype: Union[str, int, None]
    """
    return (
        config["issues"][issue][key]
        if "issues" in config.keys()
        and issue in config["issues"].keys()
        and config["issues"][issue].get(key) is not None
        else None
    )


def find_uuid_in_str(str_to_search: str) -> str:
    """
    Find a UUID in a long string

    :param str_to_search: Long string
    :return: Matching string
    :rtype: str
    """
    if dat := re.findall(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
        str_to_search,
    ):
        return dat[0]
    return str_to_search


def recursive_items(nested: Union[abc.Mapping, dict]):
    """
    Function to recursively move through a dictionary and pull out key value pairs

    :param dict nested: Nested dict to recurse through
    :return: generated iterable key value pairs
    """
    for key, value in nested.items():
        if isinstance(value, abc.Mapping):
            yield from recursive_items(value)
        if isinstance(value, list):
            for dictionary in value:
                if isinstance(dictionary, dict):
                    yield from recursive_items(dictionary)
        else:
            yield key, value


def check_file_path(file_path, output: bool = True) -> None:
    """
    Function to check the provided file path, if it doesn't exist it will be created

    :param file_path: Path to the directory
    :param output: If the function should output to the console, defaults to True
    :return: None
    """
    # see if the provided directory exists, if not create it
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        # notify user directory has been created
        if output:
            logger.info("%s didn't exist, but has been created.", file_path)


def capitalize_words(word: str) -> str:
    """
    Function to convert string to title case

    :param str word: Desired string to process
    :return: String with words titlecased
    :rtype: str
    """
    return re.sub(r"\w+", lambda m: m.group(0).capitalize(), word)


def error_and_exit(error_desc: str) -> None:
    """
    Function to display and log the provided error_desc and exits the application

    :param str error_desc: Description of the error encountered
    :return: None
    """
    logger.error(error_desc)
    sys.exit(1)


def check_url(url: str) -> bool:
    """
    Function to check if the provided url is valid

    :param str url: URL to check
    :return: True if URL is valid, False if not
    :rtype: bool
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def download_file(
    url: str, download_path: str = gettempdir(), verify: bool = True
) -> Path:
    """
    Download file from the provided url and save it to the provided download_path

    :param str url: URL location of the file to download
    :param Path download_path: Path to download the file to
    :param bool verify: SSL verification for requests, defaults to True
    :return: Path to the downloaded file
    :rtype: Path
    """
    path = Path(download_path)
    local_filename = url.split("/")[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True, timeout=10, verify=verify) as response:
        response.raise_for_status()
        with open(path / local_filename, "wb+") as file:
            for chunk in response.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                file.write(chunk)
    return path / local_filename


def check_supported_file_type(file: Path) -> None:
    """
    Check if the file type is supported.

    :param Path file: Path to the file.
    :raises: RuntimeError if the file type is not supported.
    """
    if file.suffix.lower() not in [".csv", ".json", ".xlsx"]:
        raise RuntimeError(f"Unsupported file type: {file.suffix}")


def save_to_csv(file: Path, data, output_log: bool) -> None:
    """
    Save data to a CSV file.

    :param Path file: Path to the file.
    :param data: The data to save.
    :param bool output_log: Whether to output logs.
    """
    d_frame = pd.DataFrame(data).transpose()
    d_frame.to_csv(file)
    if output_log:
        logger.info("Data successfully saved to: %s", file.name)


def save_to_excel(file: Path, data, output_log: bool) -> None:
    """
    Save data to an Excel file.

    :param Path file: Path to the file.
    :param data: The data to save.
    :param bool output_log: Whether to output logs.
    """
    d_frame = pd.DataFrame(data).transpose()
    d_frame.to_excel(file)
    if output_log:
        logger.info("Data successfully saved to: %s", file.name)


def save_to_json(file: Path, data, output_log: bool) -> None:
    """
    Save data to a JSON file. Attempts to use json.dump and falls back to write if needed.

    :param Path file: Path to the file.
    :param data: The data to save.
    :param bool output_log: Whether to output logs.
    :raises: TypeError if data cannot be converted to a json object.
    """
    try:
        with open(file, "w", encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=4)
    except TypeError:
        with open(file, "w", encoding="utf-8") as outfile:
            outfile.write(str(data))
    if output_log:
        logger.info("Data successfully saved to %s", file.name)


def save_data_to(file: Path, data, output_log: bool = True) -> None:
    """
    Save the provided data to the specified file.

    :param Path file: Path to the file.
    :param data: The data to save.
    :param bool output_log: Output logs during execution, defaults to True.
    :raises: PermissionError if the file already exists and is opened.
    :return: None.
    """
    check_supported_file_type(file)

    if output_log:
        logger.info("Prepping data to be saved to %s", file.name)

    try:
        if file.suffix.lower() == ".csv":
            save_to_csv(file, data, output_log)
        elif file.suffix.lower() == ".xlsx":
            save_to_excel(file, data, output_log)
        elif file.suffix.lower() == ".json":
            save_to_json(file, data, output_log)
    except PermissionError:
        error_and_exit(
            f"Unable to save {file.name}. Please verify it is closed and try again."
        )


def remove_nested_dict(data: dict, skip_keys: list = None) -> dict:
    """
    Function to remove nested dictionaries in the provided dictionary,
    also allows the option to remove a key from the provided dictionary

    :param dict data: The raw data that needs to have nested dictionaries removed
    :param list skip_keys: List of Keys to skip during iteration of the provided dict
    :return: Clean dictionary without nested dictionaries
    :rtype: dict
    """
    # create blank dictionary to store the clean dictionary
    result = {}
    # iterate through the keys and values in the provided dictionary
    for key, value in data.items():
        # see if skip_key was provided and if the current key == skip_key
        if skip_keys and key in skip_keys:
            # continue to the next key
            continue
        # check if the item is a nested dictionary
        if isinstance(value, dict):
            # evaluate the nested dictionary passing the nested dictionary and skip_key
            new_keys = remove_nested_dict(value, skip_keys=skip_keys)
            # update the value to a non-nested dictionary
            # result[key] = value  FIXME remove for now, is causing issues
            # iterate through the keys of the nested dictionary
            for inner_key in new_keys:
                # make sure key doesn't already exist in result
                if f"{key}_{inner_key}" in result:
                    last_char = inner_key[-1]
                    # see if the inner_key ends with a number
                    if isinstance(last_char, int):
                        # increment the number by 1 and replace the old one with the new one
                        last_char += 1
                        inner_key[-1] = last_char
                    else:
                        inner_key += "2"
                # combine the key + nested key and store it into the clean dictionary
                result[f"{key}_{inner_key}"] = result[key][inner_key]
        else:
            # item isn't a nested dictionary, save the data
            result[key] = value
    # return the un-nested dictionary
    return result


def flatten_dict(data: abc.MutableMapping) -> abc.MutableMapping:
    """
    Flattens a dictionary

    :param data: data that needs to be flattened
    :return: A flattened dictionary that has camelcase keys
    :rtype: MutableMapping
    """
    # create variable to store the clean and flattened dictionary
    flat_dict_clean = {}

    # flatten the dictionary using panda's json_normalize function
    [flat_dict] = pd.json_normalize(data, sep="@").to_dict(orient="records")

    # iterate through the keys to camelcase them and
    for key, value in flat_dict.items():
        # find the location of all the @, which are the separator for nested keys
        sep_locations = key.find("@")

        # check if there are more than one period
        if isinstance(sep_locations, list):
            # iterate through the period locations
            for period in sep_locations:
                # capitalize the character following the period
                key = key[:period] + key[period + 1].upper() + key[period + 2 :]

                # remove the @
                key = key.replace("@", "")
        elif sep_locations != -1:
            # capitalize the character following the @
            key = (
                key[:sep_locations]
                + key[sep_locations + 1].upper()
                + key[sep_locations + 2 :]
            )

            # remove the @
            key = key.replace("@", "")

        # add the cleaned key with the original value
        flat_dict_clean[key] = value
    return flat_dict_clean


def days_between(vuln_time: str, fmt: Optional[str] = "%Y-%m-%dT%H:%M:%SZ") -> int:
    """
    Find the difference in days between 2 datetimes

    :param str vuln_time: date published
    :param str fmt: datetime string format, defaults to "%Y-%m-%d %H:%M:%S"
    :return: days between 2 dates
    :rtype: int
    """
    start = datetime.strptime(vuln_time, fmt)
    today = datetime.strftime(datetime.now(), fmt)
    end = datetime.strptime(today, fmt)
    difference = relativedelta.relativedelta(end, start)
    return difference.days


def parse_url_for_pagination(raw_string: str) -> str:
    """
    Function to parse the provided string and get the URL for pagination

    :param str raw_string: string that needs to be parsed for the pagination URL
    :return: URL for pagination in Okta API
    :rtype: str
    """
    # split the string at the < signs
    split_urls = raw_string.split("<")

    # get the last entry
    split_url = split_urls[-1]

    # remove the remaining text from the last entry and return it
    return split_url[: split_url.find(">")]


def random_hex_color() -> str:
    """Return a random hex color

    :return: hex color
    :rtype: str
    """
    return "#%02X%02X%02X" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )


def format_dict_to_html(data: dict, indent: int = 1) -> str:
    """Format a dictionary to HTML

    :param data: Dictionary of data
    :param indent: Indentation. Defaults to 1.
    :return: String representing HTML
    """
    htmls = []
    for key, val in data.items():
        htmls.append(
            f"<span style='font-style: italic; color: #888'>{key}</span>: {format_data_to_html(val, indent + 1)}"
        )

    return f'<div style="margin-left: {indent}em">{",<br>".join(htmls)}</div>'


def format_data_to_html(obj, indent=1) -> str:
    """Format a list or a dict object to HTML

    :param obj: list or dict of data
    :param indent: Indentation. Defaults to 1.
    :return: String representing HTML
    """
    htmls = []

    if isinstance(obj, list):
        htmls.extend(format_data_to_html(key, indent + 1) for key in obj)
    if isinstance(obj, dict):
        htmls.extend(
            f"<span style='font-style: italic; color: #888'>{key}</span>: {format_data_to_html(val, indent + 1)}"
            for key, val in obj.items()
        )
    if htmls:
        return f'<div style="margin-left: {indent}em">{",<br>".join(htmls)}</div>'
    return str(obj)


def get_env_variable(key) -> Optional[any]:
    """Return environment variable value regardless of case.

    :param key: Environment variable key
    :return: Environment variable value
    :rtype: Optional[any]
    """
    return next((v for k, v in os.environ.items() if k.lower() == key.lower()), None)


def find_keys(node, kv):
    """
    Python generator function to traverse deeply nested lists or dictionaries to
    extract values of every key found in a given node

    :param node: A string, dict or list to parse.
    :param kv: Key, Value pair
    """
    if isinstance(node, list):
        for i in node:
            yield from find_keys(i, kv)
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            yield from find_keys(j, kv)


def get_user_names() -> pd.DataFrame:
    """This function uses API Endpoint to retrieve all user names in database

    :return: pandas dataframe with usernames
    :rtype: pd.dataframe
    """
    app = Application()
    config = app.config
    api = Api()
    accounts = api.get(url=config["domain"] + "/api/accounts").json()

    user_names = [[" ".join(item["name"].split()), item["id"]] for item in accounts]
    return pd.DataFrame(
        user_names,
        index=None,
        columns=["User", "UserId"],
    )


def check_empty_nan(value, default_return: Any = None) -> Union[str, float, None]:
    """This function takes a given value and checks if value is empty or NaN based on value type

    :param value: A string or float object
    :param default_return: The default return value, defaults to None
    :return: A string value, float value. or None
    :rtype: Union[str, float, None]
    """
    if isinstance(value, str) and value.strip() == "":
        return default_return
    if isinstance(value, float) and math.isnan(value):
        return default_return
    return value


def compute_hash(file, chunk_size: int = 8192) -> str:
    """
    Computes the SHA-256 hash of a file-like object using chunks to avoid using too much memory

    :param file: File-like object that supports .read() and .seek()
    :param int chunk_size: Size of the chunks to read from the file, defaults to 8192
    :return: SHA-256 hash of the file
    """
    hasher = hashlib.sha256()

    # Read the file in small chunks to avoid using too much memory
    while True:
        if chunk := file.read(chunk_size):
            hasher.update(chunk)
        else:
            break
    # Reset the file's position, so it can be read again later
    file.seek(0)
    return hasher.hexdigest()


def compute_hashes_in_directory(directory: Union[str, Path]) -> dict:
    """
    Computes the SHA-256 hash of all files in a directory

    :param Union[str, Path] directory: Directory to compute hashes for
    :return: Dictionary of hashes keyed by file path
    :rtype: dict
    """
    file_hashes = {}
    for file in os.listdir(directory):
        with open(os.path.join(directory, file), "rb") as in_file:
            file_hash = compute_hash(in_file)
        file_hashes[file_hash] = os.path.join(directory, file)
    return file_hashes


def walk_directory_for_files(
    directory: str, extension: str = ".ckl"
) -> tuple[list, int]:
    """
    Recursively search a directory for files with a given extension

    :param str directory: Directory to search for files
    :param str extension: File extension to search for
    :return: Tuple of list of files and total file count analyzed
    :rtype: Tuple[list, int]
    """
    desired_files = []
    total_file_count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            total_file_count += 1
            if file.endswith(extension):
                file_path = os.path.join(root, file)
                desired_files.append(file_path)
    return desired_files, total_file_count


def detect_shell() -> str:
    """
    Function to detect the current shell and returns it as a string

    :return: String of the current shell
    :rtype: str
    """
    if os.name == "posix":
        shell_path = os.getenv("SHELL")
        if shell_path:
            return os.path.basename(shell_path)
    elif os.name == "nt":
        try:
            process = psutil.Process(os.getpid())
            while process.name().lower() not in [
                "cmd.exe",
                "powershell.exe",
            ]:
                process = process.parent()
                if process is None:
                    return "Unknown"
            terminal_process = process.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return "Unknown"
        if "cmd.exe" in terminal_process.lower():
            return "CMD"
        elif "powershell.exe" in terminal_process.lower():
            return "PowerShell"
        else:
            return "Unknown"
    return "Unknown"


def convert_to_string(data: Union[str, list, datetime, bool, dict]) -> str:
    """
    Convert any data type to a string

    :param Union[str, list, datetime, bool, dict] data: Data to convert to a string
    :return: Representation of the data as a string
    :rtype: str
    """
    if isinstance(data, datetime):
        return data.strftime("%b %d, %Y")
    # see if the value is a boolean
    elif isinstance(data, bool):
        return "True" if data else "False"
    elif isinstance(data, dict):
        # Convert each key and value in the dictionary to a string
        str_dict = ""
        for key, value in data.items():
            str_dict += f"{convert_to_string(key)}: {convert_to_string(value)}\n"
        return str_dict
    elif isinstance(data, list):
        # Convert each item in the list to a string
        str_list = []
        for item in data:
            str_list.append(convert_to_string(item))
        return ", ".join(str_list)
    else:
        return str(data)


def remove_timezone_from_date_str(date: str) -> str:
    """
    Function to remove the timezone from a date string

    :param str date: Date as a string to process
    :return: Clean date string
    :rtype: str
    """
    tz_pattern = r"\s[A-Za-z]{3,4}\s*\+*\d*|[+-]\d{4}"

    # Use re.sub to remove the time zone if it exists
    clean_date = re.sub(tz_pattern, "", date).rstrip(" ")
    return clean_date


def update_keys_to_lowercase_first_letter(original_dict: Dict) -> Dict:
    """
    Function to update dictionary keys to have the first letter lowercase
    :param Dict original_dict: Dictionary to update
    :return: Dictionary with updated keys
    """
    updated_dict = {}
    for key, value in original_dict.items():
        # Lowercase the first letter of the key and combine it with the rest of the string
        updated_key = key[0].lower() + key[1:] if key else key
        updated_dict[updated_key] = value
    return updated_dict


def remove_keys(dictionary: dict, keys_to_remove: list) -> None:
    """
    Removes specified keys from a dictionary

    :param dict dictionary: The dictionary to remove keys from
    :param keys_to_remove: List of keys to remove
    :return: None
    """
    for key in keys_to_remove:
        dictionary.pop(key, None)


def log_memory():
    """
    Function to log the current memory usage in a cross-platform fashion

    :return: None
    """
    logger.debug("RAM Percent Used: %i", psutil.virtual_memory()[2])
