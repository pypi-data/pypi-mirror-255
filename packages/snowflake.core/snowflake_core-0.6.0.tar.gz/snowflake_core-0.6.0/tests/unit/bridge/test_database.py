from unittest import mock

import pytest

from snowflake.core import Clone, PointOfTimeOffset
from snowflake.core._internal.bridge.rest_errors import NotFound
from snowflake.core.database import Database, DatabaseCollection
from snowflake.core.exceptions import NotFoundError, ServerError


fake_root = mock.MagicMock()
dbs = DatabaseCollection(fake_root)


def test_fetch():
    with mock.patch(
        "snowflake.core._internal.bridge.executor.SnowExecute.execute"
    ) as mocked_execute:
        with pytest.raises(NotFoundError):
            dbs["my_db"].fetch()
    mocked_execute.assert_called_once_with(
        "SHOW DATABASES LIKE 'MY_DB' "
    )

def test_create_clone():
    clone = Clone(
        source="other_db",
        point_of_time=PointOfTimeOffset(reference="at", when="-1800"),
    )
    with mock.patch(
        "snowflake.core._internal.bridge.executor.SnowExecute.execute"
    ) as mocked_execute:
        with pytest.raises(ServerError):
            dbs.create(
                Database(
                    name="my_db",
                    comment="my comment",
                ),
                kind="transient",
                clone=clone,
            )
    mocked_execute.assert_called_once_with(
        "CREATE transient DATABASE MY_DB CLONE OTHER_DB AT OFFSET => -1800 COMMENT = 'my comment' "
    )

def test_create():
    with mock.patch(
        "snowflake.core._internal.bridge.executor.SnowExecute.execute"
    ) as mocked_execute:
        with pytest.raises(ServerError):
            dbs.create(
                Database(
                    name="my_db",
                    comment="my comment",
                    max_data_extension_time_in_days=1,
                ),
                kind="transient",
            )
    mocked_execute.assert_called_once_with(
        "CREATE transient DATABASE MY_DB MAX_DATA_EXTENSION_TIME_IN_DAYS = 1 COMMENT = 'my comment' "
    )

def test_create_or_update_create():
    with mock.patch(
        "snowflake.core._internal.bridge.executor.SnowExecute.execute"
    ) as mocked_execute:
        with mock.patch(
            "snowflake.core._internal.bridge.resources.database_resource.DatabaseResource.desc_db",
            side_effect=NotFound(),
        ):
            with pytest.raises(ServerError):
                dbs["new_db"].create_or_update(
                    Database(
                        name="new_db",
                        comment="new comment",
                        max_data_extension_time_in_days=1,
                    ),
                )
    mocked_execute.assert_called_once_with(
        "CREATE DATABASE NEW_DB MAX_DATA_EXTENSION_TIME_IN_DAYS = 1 COMMENT = 'new comment' "
    )

def test_create_or_update_update():
    old_db = Database(
        name="db",
        comment="old comment",
        max_data_extension_time_in_days=0,
    )
    with mock.patch(
        "snowflake.core._internal.bridge.executor.SnowExecute.execute"
    ) as mocked_execute:
        with mock.patch(
            "snowflake.core._internal.bridge.resources.database_resource.DatabaseResource.desc_db",
            return_value=("fake sql", old_db.to_dict()),
        ):
            with pytest.raises(ServerError):
                dbs["db"].create_or_update(
                    Database(
                        name="db",
                        comment="new comment",
                        max_data_extension_time_in_days=1,
                    ),
                )
    mocked_execute.assert_called_once_with(
        "ALTER DATABASE DB SET comment = 'new comment' max_data_extension_time_in_days = 1"
    )


def test_create_from_share():
    with mock.patch(
        "snowflake.core._internal.bridge.executor.SnowExecute.execute"
    ) as mocked_execute:
        with pytest.raises(ServerError):
            dbs._create_from_share(
                name="my_own_db",
                share="share.db",
                kind="TRANSIENT",
            )
    mocked_execute.assert_called_once_with(
        "CREATE TRANSIENT DATABASE my_own_db FROM SHARE share.db "
    )

def test_delete():
    with mock.patch(
        "snowflake.core._internal.bridge.executor.SnowExecute.execute"
    ) as mocked_execute:
        with pytest.raises(ServerError):
            dbs["my_db"].delete()
    mocked_execute.assert_called_once_with(
        "DROP DATABASE MY_DB"
    )

def test_enable_replication():
    with mock.patch(
        "snowflake.core._internal.bridge.executor.SnowExecute.execute"
    ) as mocked_execute:
        with pytest.raises(ServerError):
            dbs["my_db"].enable_replication(
                accounts=["my_org.account2"],
            )
    mocked_execute.assert_called_once_with(
        "ALTER DATABASE MY_DB ENABLE REPLICATION TO ACCOUNTS my_org.account2",
    )

def test_disable_replication():
    with mock.patch(
        "snowflake.core._internal.bridge.executor.SnowExecute.execute"
    ) as mocked_execute:
        with pytest.raises(ServerError):
            dbs["my_db"].disable_replication(
                accounts=["my_org.account2"],
            )
    mocked_execute.assert_called_once_with(
        "ALTER DATABASE MY_DB DISABLE REPLICATION TO ACCOUNTS my_org.account2",
    )

def test_refresh_replication():
    with mock.patch(
        "snowflake.core._internal.bridge.executor.SnowExecute.execute"
    ) as mocked_execute:
        with pytest.raises(ServerError):
            dbs["my_db"].refresh_replication()
    mocked_execute.assert_called_once_with(
        "ALTER DATABASE MY_DB REFRESH",
    )

def test_enable_failover():
    with mock.patch(
        "snowflake.core._internal.bridge.executor.SnowExecute.execute"
    ) as mocked_execute:
        with pytest.raises(ServerError):
            dbs["my_db"].enable_failover(
                accounts=["my_org.account2"],
            )
    mocked_execute.assert_called_once_with(
        "ALTER DATABASE MY_DB ENABLE FAILOVER TO ACCOUNTS my_org.account2",
    )

def test_disable_failover():
    with mock.patch(
        "snowflake.core._internal.bridge.executor.SnowExecute.execute"
    ) as mocked_execute:
        with pytest.raises(ServerError):
            dbs["my_db"].disable_failover()
    mocked_execute.assert_called_once_with(
        "ALTER DATABASE MY_DB DISABLE FAILOVER ",
    )

def test_promote_to_primary_failover():
    with mock.patch(
        "snowflake.core._internal.bridge.executor.SnowExecute.execute"
    ) as mocked_execute:
        with pytest.raises(ServerError):
            dbs["my_db"].promote_to_primary_failover()
    mocked_execute.assert_called_once_with(
        "ALTER DATABASE MY_DB PRIMARY",
    )
