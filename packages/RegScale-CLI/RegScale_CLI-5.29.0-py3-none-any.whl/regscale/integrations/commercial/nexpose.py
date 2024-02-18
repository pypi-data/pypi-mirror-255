#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nexpose RegScale integration"""
from pathlib import Path

import click

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.models.integration_models.prisma_nexpose import PrismaNexpose


@click.group()
def nexpose():
    """Performs actions on Nexpose files."""


@nexpose.command(name="import_nexpose")
@click.option(
    "--folder_path",
    help="File path to the folder containing Nexpose .csv files to process to RegScale.",
    prompt="File path for Nexpose files",
    type=click.Path(exists=True, dir_okay=True, resolve_path=True),
)
@click.option(
    "--regscale_ssp_id",
    type=click.INT,
    help="The ID number from RegScale of the System Security Plan.",
    prompt="Enter RegScale System Security Plan ID",
    required=True,
)
def import_nexpose(folder_path: click.Path, regscale_ssp_id: click.INT):
    """
    Import Nessus scans, vulnerabilities and assets to RegScale from Nexpose files

    """
    app = Application()
    if len(list(Path(folder_path).glob("*.csv"))) == 0:
        app.logger.warning("No Nexpose(csv) files found in the specified folder.")
        return
    for file in Path(folder_path).glob("*.csv"):
        PrismaNexpose(
            name="Nexpose", app=app, file_path=file, regscale_ssp_id=regscale_ssp_id
        )
