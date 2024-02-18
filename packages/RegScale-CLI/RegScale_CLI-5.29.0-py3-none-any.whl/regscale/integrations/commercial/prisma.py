#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prisma RegScale integration"""
from pathlib import Path

import click

from regscale.core.app.application import Application
from regscale.models.integration_models.prisma_nexpose import PrismaNexpose
from regscale.validation.record import validate_regscale_object


@click.group()
def prisma():
    """Performs actions on Prisma export files."""


@prisma.command(name="import_prisma")
@click.option(
    "--folder_path",
    help="File path to the folder containing Prisma .csv files to process to RegScale.",
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
def import_prisma(folder_path: click.Path, regscale_ssp_id: click.INT):
    """
    Import scans, vulnerabilities and assets to RegScale from Prisma export files

    """
    app = Application()
    if not validate_regscale_object(regscale_ssp_id, "securityplans"):
        app.logger.warning(
            "SSP #%i is not a valid RegScale Security Plan.", regscale_ssp_id
        )
        return
    if len(list(Path(folder_path).glob("*.csv"))) == 0:
        app.logger.warning("No Prisma(csv) files found in the specified folder.")
        return
    for file in Path(folder_path).glob("*.csv"):
        PrismaNexpose(
            name="Prisma", app=app, file_path=file, regscale_ssp_id=regscale_ssp_id
        )
