from contextlib import suppress
from datetime import timedelta

import pytest

from snowflake.core._internal.utils import normalize_name
from snowflake.core.task import Cron, StoredProcedureCall, Task
from snowflake.snowpark import Session
from snowflake.snowpark._internal.utils import parse_table_name

from ..utils import random_object_name


def test_create_or_update(tasks, db_parameters):
    task_name1 = random_object_name()
    task_name2 = random_object_name()
    try:
        task1 = tasks[task_name1]
        task1.create_or_update(
            Task(
                name=task_name1,
                definition="select current_version()",
                schedule=timedelta(minutes=100),
                warehouse=db_parameters["warehouse"],
                allow_overlapping_execution=True,
                suspend_task_after_num_failures=100,
                config={"a": 1}

                # TODO: testing with error_integration requires setup of notification channel first.
                # error_integration=,
            ),
        )
        task1_data = task1.fetch()
        assert task1_data.name == task_name1.upper()
        assert task1_data.definition == "select current_version()"
        assert task1_data.schedule == timedelta(minutes=100)
        assert task1_data.allow_overlapping_execution is True
        assert task1_data.suspend_task_after_num_failures == 100
        assert task1_data.config == {"a": 1}
        task1_data.schedule = Cron("* * * * *", "America/Los_Angeles")
        task1_data.warehouse = None
        task1_data.allow_overlapping_execution = False
        task1_data.suspend_task_after_num_failures = 200
        task1.create_or_update(task1_data)
        task1_data_again = tasks[task_name1].fetch()
        assert task1_data_again.schedule == Cron("* * * * *", "America/Los_Angeles")
        assert task1_data_again.allow_overlapping_execution is False
        assert task1_data_again.warehouse is None
        assert task1_data.suspend_task_after_num_failures == 200

        task2 = tasks[task_name2]
        task2.create_or_update(
            Task(
                name=task_name2,
                definition="select current_version()",
                user_task_managed_initial_warehouse_size="XSMALL",
                user_task_timeout_ms=1000000,
                comment="abc",
                predecessors=[task1.name],
                condition="1=1",
                session_parameters={
                    "SNOWPARK_REQUEST_TIMEOUT_IN_SECONDS": 80000,
                    "SNOWPARK_LAZY_ANALYSIS": False,
                },
            )
        )
        task2_data = task2.fetch()
        assert task2_data.name == task_name2.upper()
        assert task2_data.definition == "select current_version()"
        assert task2_data.user_task_managed_initial_warehouse_size == "XSMALL"
        assert task2_data.user_task_timeout_ms == 1000000
        assert task2_data.comment == "abc"
        assert task2_data.condition == "1=1"
        assert task2_data.session_parameters == {
            "SNOWPARK_REQUEST_TIMEOUT_IN_SECONDS": 80000,
            "SNOWPARK_LAZY_ANALYSIS": False,
        }
        assert [parse_table_name(x)[-1] for x in task2_data.predecessors] == [
            normalize_name(task_name1)
        ]
        task2_data.definition = "select 3"
        task2_data.comment = "def"
        task2_data.condition = "2=2"
        task2_data.session_parameters = {
            "SNOWPARK_REQUEST_TIMEOUT_IN_SECONDS": 90000,
            "TIMEZONE": "America/New_York",
        }
        task2.create_or_update(task2_data)
        task2_data_again = task2.fetch()
        assert task2_data_again.name == task_name2.upper()
        assert task2_data_again.definition == "select 3"
        assert task2_data_again.comment == "def"
        assert task2_data_again.condition == "2=2"
        assert task2_data_again.session_parameters == {
            "SNOWPARK_REQUEST_TIMEOUT_IN_SECONDS": 90000,
            "TIMEZONE": "America/New_York",
        }
        assert [parse_table_name(x)[-1] for x in task2_data_again.predecessors] == [
            normalize_name(task_name1)
        ]

    finally:
        with suppress(Exception):
            tasks[task_name1].delete()
        with suppress(Exception):
            tasks[task_name2].delete()


def test_create_or_update_config_and_schedule(tasks, db_parameters):
    task_name1 = random_object_name()
    try:
        task1 = tasks[task_name1]
        task1.create_or_update(
            Task(
                name=task_name1,
                definition="select current_version()",
                schedule=timedelta(minutes=100),
                config={"a": 1}
            )
        )

        task1.create_or_update(
            Task(
                name=task_name1,
                definition="select current_version()",
            )
        )
        fetched = task1.fetch()
        assert fetched.config is None
        assert fetched.schedule is None

        task1.create_or_update(
            Task(
                name=task_name1,
                definition="select current_version()",
                schedule=timedelta(minutes=101),
                config={"b": 1}
            )
        )
        fetched_again = task1.fetch()
        assert fetched_again.config == {"b": 1}
        assert fetched_again.schedule == timedelta(minutes=101)
        task1.create_or_update(
            Task(
                name=task_name1,
                definition="select current_version()",
                schedule=Cron("0 0 10-20 * TUE,THU", "America/Los_Angeles"),
            )
        )
        fetched_3rd = task1.fetch()
        fetched_3rd.schedule = Cron("0 0 10-20 * TUE,THU", "America/Los_Angeles")
    finally:
        with suppress(Exception):
            tasks[task_name1].delete()


def test_create_or_update_definition_python(tasks, db_parameters):
    def foo1(session: Session) -> None:
        session.sql("select 1").collect()

    def foo2(session: Session) -> None:
        session.sql("select 2").collect()

    test_stage = random_object_name()
    test_task = random_object_name()
    tasks._connection.execute_string(f"create or replace stage {test_stage}")
    try:
        task1 = Task(
            test_task,
            StoredProcedureCall(
                foo1, stage_location=test_stage, packages=["snowflake-snowpark-python"]
            ),
            warehouse=db_parameters["warehouse"],
        )
        task_ref = tasks[test_task]
        task_ref.create_or_update(task1)
        try:
            fetched = task_ref.fetch()
            assert "foo1" in fetched.definition
            fetched.definition = StoredProcedureCall(
                foo2, stage_location=test_stage, packages=["snowflake-snowpark-python"]
            )
            task_ref.create_or_update(fetched)
            fetched_again = task_ref.fetch()
            assert "foo2" in fetched_again.definition
        finally:
            task_ref.delete()
    finally:
        tasks._connection.execute_string(f"drop stage {test_stage}")


def test_iter_then_create_or_update(tasks):
    task_handle = tasks.create(Task(name=random_object_name(), definition='select 1'))
    try:
        listed_task = next(tasks.iter(limit=1))
        with pytest.raises(ValueError) as ex:
            tasks[listed_task.name].create_or_update(listed_task)
        assert ex.match("The input task is not a full picture of of the Task object.")

        with pytest.raises(ValueError) as ex2:
            task_handle.create_or_update(task_handle.fetch_task_dependents()[0])
        assert ex2.match("The input task is not a full picture of of the Task object.")
    finally:
        task_handle.delete()
