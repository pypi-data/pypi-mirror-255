"""Define pre-made TaskGroups for usage across DAGs."""

from uuid import uuid4

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup

from regscale.airflow.hierarchy import AIRFLOW_CLICK_OPERATORS as OPERATORS
from regscale.airflow.tasks.click import execute_click_command


def setup_task_group(
    dag: DAG,
    setup_tag: str = None,
) -> TaskGroup:
    """Create a TaskGroup for setting up the init.yaml and initialization of the DAG

    :param DAG dag: an Airflow DAG
    :param str setup_tag: a unique identifier for the task
    :return: a setup TaskGroup
    :rtype TaskGroup:
    """
    if not setup_tag:
        setup_tag = str(uuid4())[
            :8
        ]  # give the task setup group a unique name for tracking
    setup_name = f"setup-{setup_tag}"
    with TaskGroup(setup_name, dag=dag) as setup:
        login = PythonOperator(
            task_id=f"login-{setup_tag}",
            task_group=setup,
            python_callable=execute_click_command,
            op_kwargs={
                "command": OPERATORS["login"]["command"],
                "token": '{{ dag_run.conf.get("token") }}',
                "domain": '{{ dag_run.conf.get("domain") }}',
            },
        )
        login
        return setup
