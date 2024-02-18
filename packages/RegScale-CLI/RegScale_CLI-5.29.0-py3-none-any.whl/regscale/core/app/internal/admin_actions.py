#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RegScale Email Reminders"""

# standard python imports
import click

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import (
    check_license,
)
from regscale.core.app.utils.regscale_utils import (
    verify_provided_module,
)
from regscale.models.app_models.click import regscale_id, regscale_module
from regscale.models.integration_models.send_reminders import SendReminders


@click.group(name="admin_actions")
def actions():
    """Performs administrative actions on the RegScale platform."""


@actions.command(name="update_compliance_history")
@regscale_id()
@regscale_module()
def update_compliance_history(regscale_id: int, regscale_module: str):
    """
    Update the daily compliance score for a given RegScale System Security Plan.
    """
    verify_provided_module(regscale_module)
    update_compliance(regscale_id, regscale_module)


@actions.command(name="send_reminders")
@click.option(
    "--days",
    type=click.INT,
    help="RegScale will look for Assessments, Tasks, Issues, Security Plans, "
    + "Data Calls, and Workflows using today + # of days entered. Default is 30 days.",
    default=30,
    show_default=True,
    required=True,
)
def send_reminders(days: int):
    """
    Get Assessments, Issues, Tasks, Data Calls, Security Plans, and Workflows
    for the users that have email notifications enabled, email comes
    from support@regscale.com.
    """
    SendReminders(check_license(), days).get_and_send_reminders()


def update_compliance(regscale_parent_id: int, regscale_parent_module: str) -> None:
    """
    Update RegScale compliance history with a System Security Plan ID

    :param int regscale_parent_id: RegScale parent ID
    :param str regscale_parent_module: RegScale parent module
    :return: None
    """
    app = Application()
    api = Api()
    headers = {
        "accept": "*/*",
        "Authorization": app.config["token"],
    }

    response = api.post(
        headers=headers,
        url=app.config["domain"]
        + f"/api/controlImplementation/SaveComplianceHistoryByPlan?intParent={regscale_parent_id}&strModule={regscale_parent_module}",
        data="",
    )
    if not response.raise_for_status():
        if response.status_code == 201:
            if (
                "application/json" in response.headers.get("content-type")
                and "message" in response.json()
            ):
                app.logger.warning(response.json()["message"])
            else:
                app.logger.warning("Resource not created.")
        if response.status_code == 200:
            app.logger.info(
                "Updated Compliance Score for RegScale Parent ID: %i.\nParent module: %s.",
                regscale_parent_id,
                regscale_parent_module,
            )
