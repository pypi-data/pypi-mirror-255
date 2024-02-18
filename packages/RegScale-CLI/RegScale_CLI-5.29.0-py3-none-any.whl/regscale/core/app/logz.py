#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Rich Logging """

# standard python imports
import logging
import os
import tempfile
from typing import Optional
from logging.handlers import TimedRotatingFileHandler

import click
from rich.logging import RichHandler
from rich.traceback import install

from regscale import exceptions

if not os.getenv("REGSCALE_DEBUG", False):
    install(suppress=[click, exceptions])


def create_logger(
    propagate: Optional[bool] = None, custom_handler: Optional[any] = None
) -> logging.Logger:
    """
    Create a logger for use in all cases

    :param bool propagate: Whether to propagate the logger, defaults to None
    :param any custom_handler: Custom handler to add to the logger, defaults to None
    :return: logger object
    :rtype: logging.Logger
    """
    loglevel = os.environ.get("LOGLEVEL", "INFO").upper()
    rich_handler = RichHandler(rich_tracebacks=False, markup=True)
    file_handler = TimedRotatingFileHandler(
        filename=f"{tempfile.gettempdir()}{os.sep}RegScale.log",
        when="D",
        interval=3,
        backupCount=10,
    )

    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.basicConfig(
        level=loglevel,
        format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
        datefmt="[%Y/%m/%d %H:%M;%S]",
        handlers=(
            [rich_handler, file_handler, custom_handler]
            if custom_handler
            else [rich_handler, file_handler]
        ),
    )
    logger = logging.getLogger("rich")
    if propagate is not None:
        logger.propagate = propagate
    return logger
