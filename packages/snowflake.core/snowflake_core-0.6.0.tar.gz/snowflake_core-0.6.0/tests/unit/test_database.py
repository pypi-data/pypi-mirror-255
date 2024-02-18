from contextlib import suppress
from unittest import mock

from snowflake.core.database import Database, DatabaseCollection


fake_root = mock.MagicMock()
dbs = DatabaseCollection(fake_root)

def test_fetch():
    with suppress(Exception):
        with mock.patch(
            "snowflake.core.database._generated.api_client.ApiClient.request"
        ) as mocked_request:
            dbs["my_db"].fetch()
    mocked_request.assert_called_once_with(
        'GET',
        'https://org-account.snowflakecomputing.com/api/v2/databases/my_db',
        query_params=[],
        headers={'Accept': 'application/json', 'User-Agent': 'OpenAPI-Generator/1.0.0/python'},
        post_params=[],
        body=None,
        _preload_content=True,
        _request_timeout=None,
    )

def test_delete():
    with mock.patch(
        "snowflake.core.database._generated.api_client.ApiClient.request"
    ) as mocked_request:
        dbs["my_db"].delete()
    mocked_request.assert_called_once_with(
        'DELETE',
        'https://org-account.snowflakecomputing.com/api/v2/databases/my_db',
        query_params=[],
        headers={'Accept': 'application/json', 'User-Agent': 'OpenAPI-Generator/1.0.0/python'},
        post_params=[],
        body=None,
        _preload_content=True,
        _request_timeout=None,
    )

def test_create():
    with mock.patch(
        "snowflake.core.database._generated.api_client.ApiClient.request"
    ) as mocked_request:
        dbs.create(
            Database(
                name="sophie_db",
                comment="This is Sophie's database",
                trace_level="always",
            ),
            kind="transient",
        )
    mocked_request.assert_called_once_with(
        'POST',
        'https://org-account.snowflakecomputing.com/api/v2/databases?createMode=errorIfExists&kind=transient',
        query_params=[
            ('createMode', 'errorIfExists'),
            ('kind', 'transient'),
        ],
        headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'OpenAPI-Generator/1.0.0/python',
        },
        post_params=[],
        body={'name': 'sophie_db', 'comment': "This is Sophie's database", 'trace_level': 'always', 'dropped_on': None},
        _preload_content=True,
        _request_timeout=None,
    )

def test_create_from_share():
    with mock.patch(
        "snowflake.core.database._generated.api_client.ApiClient.request"
    ) as mocked_request:
        dbs._create_from_share(
            name="name",
            share="share",
            # TODO: kind?
        )
    mocked_request.assert_called_once_with(
        'POST',
        'https://org-account.snowflakecomputing.com/api/v2/databases/from_share?createMode=errorIfExists&kind=&name=name&share=share',
        query_params=[
            ('createMode', 'errorIfExists'),
            ('kind', ''),
            ('name', 'name'),
            ('share', 'share'),
        ],
        headers={'Accept': 'application/json', 'User-Agent': 'OpenAPI-Generator/1.0.0/python'},
        post_params=[],
        body=None,
        _preload_content=True,
        _request_timeout=None,
    )

def test_enable_replication():
    with mock.patch(
        "snowflake.core.database._generated.api_client.ApiClient.request"
    ) as mocked_request:
        dbs["my_db2"].enable_replication(
            ["fake_identifier1", "fake_identifier2"]
        )
    mocked_request.assert_called_once_with(
        'POST',
        'https://org-account.snowflakecomputing.com/api/v2/databases/my_db2/replication:enable?accountIdentifiers=fake_identifier1&accountIdentifiers=fake_identifier2&ignore_edition_check=False',
        query_params=[
            ('accountIdentifiers', ['fake_identifier1', 'fake_identifier2']),
            ('ignore_edition_check', False),
        ],
        headers={'Accept': 'application/json', 'User-Agent': 'OpenAPI-Generator/1.0.0/python'},
        post_params=[],
        body=None,
        _preload_content=True,
        _request_timeout=None,
    )

def test_disable_replication():
    with mock.patch(
        "snowflake.core.database._generated.api_client.ApiClient.request"
    ) as mocked_request:
        dbs["my_db2"].disable_replication()
    mocked_request.assert_called_once_with(
        'POST',
        'https://org-account.snowflakecomputing.com/api/v2/databases/my_db2/replication:disable?',
        query_params=[('accountIdentifiers', [])],
        headers={'Accept': 'application/json', 'User-Agent': 'OpenAPI-Generator/1.0.0/python'},
        post_params=[],
        body=None,
        _preload_content=True,
        _request_timeout=None,
    )

def test_refresh_replication():
    with mock.patch(
        "snowflake.core.database._generated.api_client.ApiClient.request"
    ) as mocked_request:
        dbs["my_db2"].refresh_replication()
    mocked_request.assert_called_once_with(
        'POST',
        'https://org-account.snowflakecomputing.com/api/v2/databases/my_db2/replication:refresh',
        query_params=[],
        headers={'Accept': 'application/json', 'User-Agent': 'OpenAPI-Generator/1.0.0/python'},
        post_params=[],
        body=None,
        _preload_content=True,
        _request_timeout=None,
    )

def test_enable_failover():
    with mock.patch(
        "snowflake.core.database._generated.api_client.ApiClient.request"
    ) as mocked_request:
        dbs["my_db2"].enable_failover(
            ["fake_identifier1", "fake_identifier2"]
        )
    mocked_request.assert_called_once_with(
        'POST',
        'https://org-account.snowflakecomputing.com/api/v2/databases/my_db2/failover:enable?accountIdentifiers=fake_identifier1&accountIdentifiers=fake_identifier2',
        query_params=[('accountIdentifiers', ['fake_identifier1', 'fake_identifier2']),],
        headers={'Accept': 'application/json', 'User-Agent': 'OpenAPI-Generator/1.0.0/python'},
        post_params=[],
        body=None,
        _preload_content=True,
        _request_timeout=None,
    )

def test_disable_failover():
    with mock.patch(
        "snowflake.core.database._generated.api_client.ApiClient.request"
    ) as mocked_request:
        dbs["my_db2"].disable_failover()
    mocked_request.assert_called_once_with(
        'POST',
        'https://org-account.snowflakecomputing.com/api/v2/databases/my_db2/failover:disable?',
        query_params=[('accountIdentifiers', [])],
        headers={'Accept': 'application/json', 'User-Agent': 'OpenAPI-Generator/1.0.0/python'},
        post_params=[],
        body=None,
        _preload_content=True,
        _request_timeout=None,
    )

def test_promote_to_primary_failover():
    with mock.patch(
        "snowflake.core.database._generated.api_client.ApiClient.request"
    ) as mocked_request:
        dbs["my_db2"].promote_to_primary_failover()
    mocked_request.assert_called_once_with(
        'POST',
        'https://org-account.snowflakecomputing.com/api/v2/databases/my_db2/failover:primary',
        query_params=[],
        headers={'Accept': 'application/json', 'User-Agent': 'OpenAPI-Generator/1.0.0/python'},
        post_params=[],
        body=None,
        _preload_content=True,
        _request_timeout=None,
    )
