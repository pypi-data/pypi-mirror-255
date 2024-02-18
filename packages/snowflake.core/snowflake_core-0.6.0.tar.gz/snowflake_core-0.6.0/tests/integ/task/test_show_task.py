#
# Copyright (c) 2012-2023 Snowflake Computing Inc. All rights reserved.
#

from typing import Dict, Generator, Iterable

import pytest

from snowflake.core.task import Task

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
        "schedule = '10 minute' as select current_version()"
    )
    session.sql(create_task2).collect()
    create_task3 = (
        f"create or replace task {task_name3} "
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


def test_basic(tasks):
    result = _info_list_to_dict(tasks.iter())
    for t in [task_name1, task_name2, task_name3]:
        assert t.upper() in result
        res = result[t.upper()]
        task = tasks[t].fetch()
        assert res.created_on == task.created_on
        assert res.name == task.name
        assert task.id == res.id
        assert task.database_name == res.database_name
        assert task.schema_name == res.schema_name
        assert task.owner == res.owner
        assert task.definition == res.definition
        assert task.warehouse == res.warehouse
        assert task.comment == res.comment
        assert task.state == res.state
        assert task.condition == res.condition
        assert task.error_integration == res.error_integration
        assert task.last_committed_on == res.last_committed_on
        assert task.last_suspended_on == res.last_suspended_on


def test_pattern(tasks):
    result = _info_list_to_dict(tasks.iter(like=task_name1))
    assert task_name1.upper() in result
    assert len(result) == 1
    result = _info_list_to_dict(tasks.iter(like=random_object_name()))
    assert len(result) == 0
    result = _info_list_to_dict(tasks.iter(like="test_object%"))
    assert task_name1.upper() in result
    assert task_name2.upper() in result
    assert task_name3.upper() in result


def test_like(tasks):
    result = tasks.iter(like='')
    assert len(list(result)) == 0


def _info_list_to_dict(info_list: Iterable[Task]) -> Dict[str, Task]:
    result = {}
    for info in info_list:
        result[info.name] = info
    return result
