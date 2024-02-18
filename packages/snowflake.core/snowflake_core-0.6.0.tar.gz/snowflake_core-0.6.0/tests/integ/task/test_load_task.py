#
# Copyright (c) 2012-2023 Snowflake Computing Inc. All rights reserved.
#

from datetime import timedelta
from typing import Generator, List

import pytest

from snowflake.connector import DictCursor
from snowflake.core.exceptions import NotFoundError
from snowflake.snowpark._internal.utils import parse_table_name

from ..utils import random_object_name


task_name1 = random_object_name()
task_name2 = random_object_name()
task_name3 = random_object_name()


@pytest.fixture(scope="module", autouse=True)
def setup(tasks, session) -> Generator[None, None, None]:
    warehouse_name: str = session.get_current_warehouse()
    create_task2 = (
        f"create or replace task {task_name2} "
        "ALLOW_OVERLAPPING_EXECUTION = true SUSPEND_TASK_AFTER_NUM_FAILURES = 10 "
        "TIMEZONE='America/Los_Angeles' SNOWPARK_REQUEST_TIMEOUT_IN_SECONDS = 100 QUERY_RESULT_FORMAT='ARROW'"
        "schedule = '10 minute' as select current_version()"
    )
    session.sql(create_task2).collect()
    create_task3 = (
        f"create or replace task {task_name3} "
        "user_task_managed_initial_warehouse_size = 'xsmall' "
        "SCHEDULE = 'USING CRON 0 9-17 * * SUN America/Los_Angeles' as select current_version()"
    )
    session.sql(create_task3).collect()
    create_task1 = (
        f"create or replace task {task_name1} "
        f"warehouse = {warehouse_name} "
        "comment = 'test_task' "
        f"after {task_name2}, {task_name3} "
        "as select current_version()"
    )
    session.sql(create_task1).collect()
    yield
    drop_task1 = f"drop task if exists {task_name1}"
    session.sql(drop_task1).collect()
    drop_task2 = f"drop task if exists {task_name2}"
    session.sql(drop_task2).collect()
    drop_task3 = f"drop task if exists {task_name2}"
    session.sql(drop_task3).collect()


def test_load_task_basic(tasks, session):
    task = tasks[task_name1].fetch()
    result = session._conn._conn.cursor(DictCursor).execute(
        f"describe task {task_name1}"
    )
    for res in result:
        assert res["created_on"] == task.created_on
        assert res["name"] == task.name
        assert task.name == task_name1.upper()
        assert task.id == res["id"]
        assert task.database_name == res["database_name"]
        assert task.schema_name == res["schema_name"]
        assert task.owner == res["owner"]
        assert task.definition == res["definition"]
        assert task.warehouse == res["warehouse"]
        assert task.comment == res["comment"]
        assert task.comment == "test_task"
        assert task.state == res["state"]
        assert task.condition == res["condition"]
        assert task.error_integration == res["error_integration"]
        assert task.last_committed_on == res["last_committed_on"]
        assert task.last_suspended_on == res["last_suspended_on"]
        # check predecessors
        parent_ids: List[str] = sorted(
            map(lambda name: parse_table_name(name)[-1], task.predecessors)
        )
        expected = sorted(
            [
                tasks[task_name2].fetch().name,
                tasks[task_name3].fetch().name,
            ]
        )
        assert expected == parent_ids


def test_load_task_allow_overlapping_execution(tasks):
    task = tasks[task_name2].fetch()
    assert task.allow_overlapping_execution


def test_load_task_user_task_managed_initial_warehouse_size(tasks):
    task = tasks[task_name3]
    assert task.fetch().user_task_managed_initial_warehouse_size == "XSMALL"


def test_show_parameters(tasks):
    task = tasks[task_name2]
    task_payload = task.fetch()
    local_parameters = task_payload.session_parameters
    assert (
        local_parameters["TIMEZONE"]
        == "America/Los_Angeles"
    )
    assert (
        local_parameters["SNOWPARK_REQUEST_TIMEOUT_IN_SECONDS"]
        == 100
    )
    assert (
        local_parameters["QUERY_RESULT_FORMAT"]
        == "ARROW"
    )


def test_load_task_failure(tasks):
    # lazy, no error
    task = tasks["task_not_exists"]

    with pytest.raises(NotFoundError):
        task.fetch()


def test_load_task_schedule(tasks):
    task2 = tasks[task_name2].fetch()
    assert task2.schedule == timedelta(minutes=10)
    task3 = tasks[task_name3].fetch()
    assert task3.schedule.expr == "0 9-17 * * SUN"
    assert task3.schedule.timezone == "America/Los_Angeles"
