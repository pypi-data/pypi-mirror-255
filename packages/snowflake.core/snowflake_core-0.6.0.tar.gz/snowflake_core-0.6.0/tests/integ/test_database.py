#
# Copyright (c) 2012-2023 Snowflake Computing Inc. All rights reserved.
#
from operator import attrgetter

import pytest

from snowflake.core import Clone
from snowflake.core.database import Database, DatabaseCollection, DatabaseResource
from snowflake.core.exceptions import APIError, NotFoundError

from ..utils import random_string


@pytest.fixture(scope="module", autouse=True)
def revert_database(connection):
    """Since this module messes with the databases.

    Let's revert back to whatever database was used before these
    tests were run.
    """
    with connection.cursor() as cursor:
        database = cursor.execute("SELECT CURRENT_DATABASE()").fetchone()[0]
        schema = cursor.execute("SELECT CURRENT_SCHEMA()").fetchone()[0]
        yield
        if schema is not None:
            cursor.execute(f"USE SCHEMA {database}.{schema}")
        elif database is not None:
            cursor.execute(f"USE DATABASE {database}")

def test_fetch(databases, temp_db):
    database = databases[temp_db.name].fetch()
    assert (
        database.name == temp_db.name  # for mixed case names
        or database.name.upper()
        == temp_db.name.upper()  # for upper/lower case names
    )

def test_delete(databases):
    new_database = Database(
        name=random_string(5, "test_db_")
    )
    new_db = databases.create(new_database)
    new_db.delete()
    with pytest.raises(
        NotFoundError,
    ):
        new_db.fetch()

def test_iter(databases, temp_db):
    assert any(
        map(
            lambda e: e
            in tuple(
                map(
                    attrgetter("name"),
                    databases.iter(),
                )
            ),
            (
                temp_db.name,  # for mixed case names
                temp_db.name.upper(),  # for upper/lower case names
            ),
        )
    )


def test_iter_limit(databases):
    data = list(databases.iter(limit=10))
    assert len(data) <= 10


def test_create_or_update_database(databases, temp_db: DatabaseResource):
    db_def = temp_db.fetch()
    db_def.comment = "my new comment"
    db_def.data_retention_time_in_days = 0
    db_def.default_ddl_collation = "en_US-trim"
    db_def.log_level = "INFO"
    db_def.max_data_extension_time_in_days = 7
    db_def.suspend_task_after_num_failures = 1
    db_def.trace_level = "ALWAYS"
    db_def.user_task_managed_initial_warehouse_size = "SMALL"
    db_def.user_task_timeout_ms = 3600001
    temp_db.create_or_update(db_def)
    new_db = databases[temp_db.name].fetch()
    assert new_db.name in (temp_db.name, temp_db.name.upper())
    assert new_db.comment == "my new comment"
    assert new_db.data_retention_time_in_days == 0
    assert new_db.default_ddl_collation == "en_US-trim"
    assert new_db.log_level == "INFO"
    assert new_db.max_data_extension_time_in_days == 7
    assert new_db.suspend_task_after_num_failures == 1
    assert new_db.trace_level == "ALWAYS"
    assert new_db.user_task_managed_initial_warehouse_size == "SMALL"
    assert new_db.user_task_timeout_ms == 3600001

@pytest.mark.xfail(reason="there seems to be a server-side error when running this")
def test_create_clone(databases: DatabaseCollection):
    new_db_def = Database(name="TEST_CLONE_TESTDB_PYTHON")
    db = databases.create(
        new_db_def,
        clone=Clone(source="TESTDB_PYTHON"),
        mode='orreplace',
    )
    db.fetch()

def test_create_from_share(databases: DatabaseCollection):
    new_db_name = random_string(3, "test_db_from_share_")
    db = databases._create_from_share(
        new_db_name,
        share='SFSALESSHARED.SFC_SAMPLES_PROD3."SAMPLE_DATA"',
    )
    try:
        assert db.fetch().is_current
    finally:
        db.delete()


def test_resist_multi_statement_sql_injection(databases: DatabaseCollection):
    new_db_name = random_string(3, "test_db_resist_multi_statement_sql_injection_")
    sql_injection_comment = "'comment for disguise'; select '1'"

    new_db = Database(
        name=new_db_name,
        comment=sql_injection_comment,
    )
    with pytest.raises(APIError) as exec_info:
        databases.create(new_db)
    assert "\"error_code\": \"400\"" in exec_info.value.body
    assert "Actual statement count 2 did not match the desired statement count 1" in exec_info.value.body
