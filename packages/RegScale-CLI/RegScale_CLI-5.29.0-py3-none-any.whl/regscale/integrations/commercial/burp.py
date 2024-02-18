#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Burp Scanner RegScale integration"""
from pathlib import Path

import click

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.models.integration_models.burp import Burp

logger = create_logger(__name__)


# Create group to handle OSCAL processing
@click.group()
def burp():
    """Performs actions on Burp Scanner artifacts."""


@burp.command(name="import_burp")
@click.option(
    "--folder_path",
    help="File path to the folder containing Burp files to process to RegScale.",
    prompt="File path for Burp files",
    type=click.Path(exists=True, dir_okay=True, resolve_path=True),
)
@click.option(
    "--regscale_ssp_id",
    type=click.INT,
    help="The ID number from RegScale of the System Security Plan.",
    prompt="Enter RegScale System Security Plan ID",
    required=True,
)
def import_burp(folder_path: click.Path, regscale_ssp_id: click.INT):
    """
    Import Nessus scans, vulnerabilities and assets to RegScale from burp files

    """
    app = Application()
    if len(list(Path(folder_path).glob("*.xml"))) == 0:
        logger.warning("No Burp files found in the specified folder.")
        return
    for file in Path(folder_path).glob("*.xml"):
        Burp(app, file, parentId=regscale_ssp_id, parentModule="securityplans")
