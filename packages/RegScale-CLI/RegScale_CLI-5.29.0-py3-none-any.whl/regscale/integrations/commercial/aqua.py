#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aqua RegScale integration"""
from pathlib import Path

import click

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.models.integration_models.aqua import Aqua
from regscale.validation.record import validate_regscale_object


@click.group()
def aqua():
    """Performs actions on Aqua Scanner artifacts."""


@aqua.command(name="import_aqua")
@click.option(
    "--folder_path",
    help="File path to the folder containing Aqua files to process to RegScale.",
    prompt="File path for Aqua files",
    type=click.Path(exists=True, dir_okay=True, resolve_path=True),
)
@click.option(
    "--regscale_ssp_id",
    type=click.INT,
    help="The ID number from RegScale of the System Security Plan.",
    prompt="Enter RegScale System Security Plan ID",
    required=True,
)
def import_aqua(folder_path: click.Path, regscale_ssp_id: click.INT):
    """
    Import Aqua scans, vulnerabilities and assets to RegScale from Aqua CSV files

    """
    app = Application()
    if not validate_regscale_object(regscale_ssp_id, "securityplans"):
        app.logger.warning(
            "SSP #%i is not a valid RegScale Security Plan.", regscale_ssp_id
        )
        return
    if len(list(Path(folder_path).glob("*.csv"))) == 0:
        app.logger.warning("No Aqua files found in the specified folder.")
        return
    for file in Path(folder_path).glob("*.csv"):
        Aqua(
            app=app,
            name="Aqua",
            file_path=file,
            parent_id=regscale_ssp_id,
            parent_module="securityplans",
        )
