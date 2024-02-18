from unittest import mock

import pytest

from snowflake.core import Clone, PointOfTimeOffset
from snowflake.core._internal.bridge.rest_errors import NotFound
from snowflake.core.database import DatabaseCollection
from snowflake.core.exceptions import NotFoundError, ServerError
from snowflake.core.schema import Schema, SchemaCollection


fake_root = mock.MagicMock()
dbs = DatabaseCollection(fake_root)
db = dbs["my_db"]
schemas = SchemaCollection(db)

def test_fetch():
    with mock.patch(
        "snowflake.core._internal.bridge.executor.SnowExecute.execute"
    ) as mocked_execute:
        with pytest.raises(NotFoundError):
            schemas["my_schema"].fetch()
    mocked_execute.assert_called_once_with(
        "SHOW SCHEMAS LIKE 'MY_SCHEMA' IN DATABASE MY_DB "
    )

def test_create():
    with mock.patch(
        "snowflake.core._internal.bridge.executor.SnowExecute.execute"
    ) as mocked_execute:
        with pytest.raises(ServerError):
            schemas.create(
                Schema(
                    name="my_schema",
                    comment="my comment",
                    max_data_extension_time_in_days=1,
                ),
                kind="transient",
            )
    mocked_execute.assert_called_once_with(
        "CREATE transient SCHEMA MY_DB.MY_SCHEMA MAX_DATA_EXTENSION_TIME_IN_DAYS = 1 COMMENT = 'my comment' "
    )

def test_create_clone():
    with mock.patch(
        "snowflake.core._internal.bridge.executor.SnowExecute.execute"
    ) as mocked_execute:
        with pytest.raises(ServerError):
            schemas.create(
                Schema(
                    name="my_schema",
                    comment="my comment",
                ),
                clone=Clone(
                    source="other_schema",
                    point_of_time=PointOfTimeOffset(reference="at", when="-1800"),
                ),
                kind="transient",
            )
    mocked_execute.assert_called_once_with(
        "CREATE transient SCHEMA MY_DB.MY_SCHEMA CLONE other_schema AT OFFSET => -1800 COMMENT = 'my comment' "
    )

def test_create_or_update_create():
    with mock.patch(
        "snowflake.core._internal.bridge.executor.SnowExecute.execute"
    ) as mocked_execute:
        with mock.patch(
            "snowflake.core._internal.bridge.resources.schema_resource.SchemaResource.desc_schema",
            side_effect=NotFound(),
        ):
            with pytest.raises(ServerError):
                schemas["new_schema"].create_or_update(
                    Schema(
                        name="new_schema",
                        comment="new comment",
                        max_data_extension_time_in_days=1,
                    ),
                )
    mocked_execute.assert_called_once_with(
        "CREATE SCHEMA MY_DB.NEW_SCHEMA MAX_DATA_EXTENSION_TIME_IN_DAYS = 1 COMMENT = 'new comment' "
    )

def test_create_or_update_update():
    old_db = Schema(
        name="schema",
        comment="old comment",
        max_data_extension_time_in_days=0,
    )
    with mock.patch(
        "snowflake.core._internal.bridge.executor.SnowExecute.execute"
    ) as mocked_execute:
        with mock.patch(
            "snowflake.core._internal.bridge.resources.schema_resource.SchemaResource.desc_schema",
            return_value=("fake sql", old_db.to_dict()),
        ):
            with pytest.raises(ServerError):
                schemas["schema"].create_or_update(
                    Schema(
                        name="schema",
                        comment="new comment",
                        max_data_extension_time_in_days=1,
                    ),
                )
    mocked_execute.assert_called_once_with(
        "ALTER SCHEMA MY_DB.SCHEMA SET comment = 'new comment' max_data_extension_time_in_days = 1"
    )

def test_delete():
    with mock.patch(
        "snowflake.core._internal.bridge.executor.SnowExecute.execute"
    ) as mocked_execute:
        with pytest.raises(ServerError):
            schemas["schema"].delete()
    mocked_execute.assert_called_once_with(
        "DROP SCHEMA MY_DB.SCHEMA"
    )
