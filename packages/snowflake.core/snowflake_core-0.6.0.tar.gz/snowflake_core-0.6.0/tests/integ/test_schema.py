from operator import attrgetter

import pytest

from snowflake.core import Clone
from snowflake.core.exceptions import NotFoundError
from snowflake.core.schema import Schema, SchemaCollection, SchemaResource

from .utils import random_string


@pytest.fixture(scope="module", autouse=True)
def revert_schema(connection):
    """Ensure that the original schema is restored after the test runs.

    This module messes with the current schema, we have to clean things up by reverting back to whatever
    schema was used before these tests were run.
    """
    with connection.cursor() as cursor:
        database = cursor.execute("SELECT CURRENT_DATABASE()").fetchone()[0]
        schema = cursor.execute("SELECT CURRENT_SCHEMA()").fetchone()[0]
        yield
        if schema is not None:
            cursor.execute(f"USE SCHEMA {database}.{schema}")
        elif database is not None:
            cursor.execute(f"USE DATABASE {database}")


def test_fetch(schemas, temp_schema):
    schema = temp_schema.fetch()
    assert (
        schema.name == temp_schema.name  # for mixed case names
        or temp_schema.name.upper()
        == temp_schema.name.upper()  # for upper/lower case names
    )

def test_delete(schemas):
    new_schema = Schema(
        name=random_string(5, "test_schema_")
    )
    new_schema = schemas.create(new_schema)
    new_schema.delete()
    with pytest.raises(
        NotFoundError,
    ):
        new_schema.fetch()


def test_iter(schemas, temp_schema):
    schema_names = tuple(
                map(
                    attrgetter("name"),
                    schemas.iter(),
                )
    )
    assert any(
        map(
            lambda e: e
            in schema_names,
            (
                temp_schema.name,  # for mixed case names
                temp_schema.name.upper(),  # for upper/lower case names
            ),
        )
    )


def test_iter_limit(schemas):
    data = list(schemas.iter(limit=10))
    assert len(data) <= 10


def test_update_all_params(schemas, temp_schema: SchemaResource):
    new_sc_def = temp_schema.fetch()
    new_sc_def.comment = "my new comment"
    new_sc_def.data_retention_time_in_days = 0
    new_sc_def.default_ddl_collation = "en_US-trim"
    new_sc_def.log_level = "INFO"
    new_sc_def.pipe_execution_paused = True
    new_sc_def.max_data_extension_time_in_days = 7
    new_sc_def.suspend_task_after_num_failures = 1
    new_sc_def.trace_level = "ALWAYS"
    new_sc_def.user_task_managed_initial_warehouse_size = "SMALL"
    new_sc_def.user_task_timeout_ms = 3600001
    temp_schema.create_or_update(new_sc_def)
    new_sc = schemas[temp_schema.name].fetch()
    assert new_sc.name in (temp_schema.name, temp_schema.name.upper())
    assert new_sc.comment == "my new comment"
    assert new_sc.data_retention_time_in_days == 0
    assert new_sc.default_ddl_collation == "en_US-trim"
    assert new_sc.log_level == "INFO"
    assert new_sc.pipe_execution_paused is True
    assert new_sc.max_data_extension_time_in_days == 7
    assert new_sc.suspend_task_after_num_failures == 1
    assert new_sc.trace_level == "ALWAYS"
    assert new_sc.user_task_managed_initial_warehouse_size == "SMALL"
    assert new_sc.user_task_timeout_ms == 3600001

def test_create_clone(schemas: SchemaCollection, temp_schema: SchemaResource):
    new_schema_def = Schema(name="TEST_CLONE_TESTSCHEMA_PYTHON")
    schema = schemas.create(
        new_schema_def,
        clone=Clone(source=temp_schema.name),
        mode='orreplace',
    )
    try:
        schema.fetch()
    finally:
        schema.delete()
