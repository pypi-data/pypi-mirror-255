# Copyright (c) 2012-2023 Snowflake Computing Inc. All rights reserved.

import os
import uuid

from io import BytesIO
from textwrap import dedent
from typing import Dict, Generator, Iterator

import pytest

import snowflake.connector

from snowflake.core import Root
from snowflake.core.compute_pool import (
    ComputePool,
    ComputePoolCollection,
)
from snowflake.core.database import (
    Database,
    DatabaseCollection,
    DatabaseResource,
)
from snowflake.core.image_repository import (
    ImageRepository,
    ImageRepositoryCollection,
)
from snowflake.core.schema import (
    Schema,
    SchemaCollection,
    SchemaResource,
)
from snowflake.core.service import (
    Service,
    ServiceCollection,
    ServiceResource,
    ServiceSpecInlineText,
    ServiceSpecStageFile,
)
from snowflake.core.warehouse import WarehouseCollection
from snowflake.snowpark import Session

from .utils import random_string


RUNNING_ON_GH = os.getenv("GITHUB_ACTIONS") == "true"
TEST_SCHEMA = "GH_JOB_{}".format(str(uuid.uuid4()).replace("-", "_"))


def running_on_public_ci() -> bool:
    """Whether or not tests are currently running on one of our public CIs."""
    return RUNNING_ON_GH


def print_help() -> None:
    print(
        """Connection parameter must be specified in parameters.py,
    for example:
CONNECTION_PARAMETERS = {
    'account': 'testaccount',
    'user': 'user1',
    'password': 'test',
    'database': 'testdb',
    'schema': 'public',
}
"""
    )


@pytest.fixture(scope="session")
def db_parameters() -> Dict[str, str]:
    # If its running on our public CI, replace the schema
    # If its running on our public CI, replace the schema
    #
    # For legacy purposes, look to see if there's a parameters.py file and if
    # so, use its credentials.  To use the newer ~/.snowflake/config.toml file
    # credentials, delete parameters.py.
    try:
        from ..parameters import CONNECTION_PARAMETERS
    except ImportError:
        CONNECTION_PARAMETERS = None
        from snowflake.connector.config_manager import CONFIG_MANAGER

    # 2023-06-23(warsaw): By default, we read out of the [connections.snowflake] section in the config.toml file, but by
    # setting the environment variable SNOWFLAKE_CONNECTION you can read out of a different section.  For example
    # SNOWFLAKE_CONNECTION='connections.test' reads out of [connections.test]

    section = os.environ.get('SNOWFLAKE_CONNECTION', '')
    level0, dot, level1 = section.partition('.')
    if dot != '.':
        level0, level1 = ('connections', 'snowflake')

    if CONNECTION_PARAMETERS is None:
        config = CONFIG_MANAGER[level0][level1].unwrap()
    else:
        config = CONNECTION_PARAMETERS

    config["schema"] = TEST_SCHEMA
    return config


# 2023-06-21(warsaw): WARNING!  If any of these fixtures fail, they will print
# db_parameters in the traceback, and that **will** leak the password.  pytest
# doesn't seem to have any way to suppress the password, and I've tried lots
# of things to get that to work, to no avail.

@pytest.fixture(scope="session")
def connection(db_parameters):
    _keys = [
        "user",
        "password",
        "host",
        "port",
        "database",
        "account",
        "protocol",
        "role",
        "warehouse"
    ]
    with snowflake.connector.connect(
        # This works around SNOW-998521, by forcing JSON results
        session_parameters={"python_connector_query_result_format": "json"},
        **{k: db_parameters[k] for k in _keys if k in db_parameters}
    ) as con:
        yield con


@pytest.fixture(scope="session")
def session(connection):
    return Session.builder.config("connection", connection).create()


@pytest.fixture(scope="session")
def root(connection) -> Root:
    return Root(connection)


@pytest.fixture(scope="session")
def database(root, db_parameters) -> DatabaseResource:
    return root.databases[db_parameters["database"]]


@pytest.fixture(scope="session")
def schema(schemas, db_parameters) -> SchemaResource:
    return schemas[db_parameters["schema"]]


@pytest.fixture(scope="module")
def image_repositories(schema) -> ImageRepositoryCollection:
    return schema.image_repositories


@pytest.fixture(scope="module")
def compute_pools(root) -> ComputePoolCollection:
    return root.compute_pools


@pytest.fixture(scope="module")
def warehouses(root) -> WarehouseCollection:
    return root.warehouses


@pytest.fixture(scope="session")
def services(schema) -> ServiceCollection:
    return schema.services

@pytest.fixture(scope="session")
def databases(root, db_parameters) -> DatabaseCollection:
    return root.databases

@pytest.fixture(scope="session")
def schemas(database) -> SchemaCollection:
    return database.schemas


@pytest.fixture(scope="session", autouse=True)
def test_schema(connection) -> Generator[str, None, None]:
    """Set up and tear down the test schema. This is automatically called per test session."""
    with connection.cursor() as cursor:
        database = cursor.execute("SELECT CURRENT_DATABASE()").fetchone()[0]
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {TEST_SCHEMA}")
        yield TEST_SCHEMA
        cursor.execute(f"USE DATABASE {database}")
        cursor.execute(f"DROP SCHEMA IF EXISTS {TEST_SCHEMA}")


@pytest.fixture
def temp_ir(image_repositories) -> Generator[ImageRepository, None, None]:
    ir_name = random_string(5, "test_ir_")
    test_ir = ImageRepository(
        name=ir_name,
    )
    image_repositories.create(test_ir)
    yield test_ir
    image_repositories[test_ir.name].delete()


@pytest.fixture
def temp_cp(compute_pools) -> Generator[ComputePool, None, None]:
    cp_name = random_string(5, "test_cp_")
    test_cp = ComputePool(
        name=cp_name,
        instance_family="STANDARD_1",
        min_nodes=1,
        max_nodes=1,
    )
    compute_pools.create(test_cp)
    yield test_cp
    compute_pools[test_cp.name].delete()


@pytest.fixture
def imagerepo() -> str:
    # When adding an inlined image repository YAML file, don't hard code the path to the test image
    # repository.  Instead, use this fixture and f-string this value in for the `{imagrepo}` substitution.
    # This way, there's only one thing to change across the entire test suite.
    return 'sfengineering-ss-lprpr-test2.registry.snowflakecomputing.com/testdb_python/public/ci_image_repository'


@pytest.fixture
def temp_service(root, services, session, imagerepo) -> Iterator[ServiceResource]:
    stage_name = random_string(5, "test_stage_")
    s_name = random_string(5, "test_service_")
    session.sql(f"create temp stage {stage_name};").collect()
    spec_file = "spec.yaml"
    stage_file = f"@{stage_name}"
    spec = f"{stage_file}/{spec_file}"
    session.file.put_stream(
        BytesIO(
            dedent(
                f"""
                spec:
                  containers:
                  - name: hello-world
                    image: {imagerepo}/hello-world:latest
                 """
            ).encode()
        ),
        spec,
    )
    test_s = Service(
        name=s_name,
        compute_pool="ci_compute_pool",
        spec=ServiceSpecStageFile(stage_location=stage_file, spec_file=spec_file),
        min_instances=1,
        max_instances=1,
    )
    s = services.create(test_s)
    yield test_s
    s.delete()


@pytest.fixture
def temp_service_from_spec_inline(root, services, session, imagerepo) -> Iterator[ServiceResource]:
    s_name = random_string(5, "test_service_")
    inline_spec = dedent(
        f"""
        spec:
          containers:
          - name: hello-world
            image: {imagerepo}/hello-world:latest
         """
    )
    test_s = Service(
        name=s_name,
        compute_pool="ci_compute_pool",
        spec=ServiceSpecInlineText(specification=inline_spec),
        min_instances=1,
        max_instances=1,
    )
    s = services.create(test_s)
    yield test_s
    s.delete()

@pytest.fixture
def temp_db(connection, databases: DatabaseCollection) -> Iterator[DatabaseResource]:
    with connection.cursor() as cursor:
        # being able to reset
        database = cursor.execute("SELECT CURRENT_DATABASE()").fetchone()[0]
        schema = cursor.execute("SELECT CURRENT_SCHEMA()").fetchone()[0]
        # create temp database
        db_name = random_string(5, "test_database_")
        test_db = Database(
            name=db_name,
        )
        db = databases.create(test_db)
        yield db
        db.delete()
        if schema is not None:
            cursor.execute(f"USE SCHEMA {database}.{schema}")
        elif database is not None:
            cursor.execute(f"USE DATABASE {database}")

@pytest.fixture
def temp_schema(connection, schemas):
    with connection.cursor() as cursor:
        # being able to reset
        database = cursor.execute("SELECT CURRENT_DATABASE()").fetchone()[0]
        schema = cursor.execute("SELECT CURRENT_SCHEMA()").fetchone()[0]
        # create temp database
        schema_name = random_string(5, "test_schema_")
        test_schema = Schema(
            name=schema_name,
        )
        sc = schemas.create(test_schema)
        yield sc
        sc.delete()
        if schema is not None:
            cursor.execute(f"USE SCHEMA {database}.{schema}")
        elif database is not None:
            cursor.execute(f"USE DATABASE {database}")
