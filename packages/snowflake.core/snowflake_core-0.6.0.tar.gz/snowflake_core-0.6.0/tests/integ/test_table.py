import copy
import datetime

from contextlib import suppress
from typing import Dict, Generator

import pytest as pytest

from snowflake.core._internal.bridge.resources.table_resource import normalize_datatype
from snowflake.core._internal.utils import normalize_name
from snowflake.core.exceptions import APIError, NotFoundError
from snowflake.core.table import PrimaryKey, Table, TableCollection, TableColumn, TableResource, UniqueKey

from .utils import random_string


test_table_template = Table(
    name="<to be set>",
    columns=[
        TableColumn("c1", "int", nullable=False, identity=True, identity_start=0, identity_increment=1),
        TableColumn("c2", "string"),
        TableColumn("c3", "string", collate="FR"),
    ],
    cluster_by=["c1>1", "c2"],
    enable_schema_evolution=True,
    change_tracking=True,
    data_retention_time_in_days=1,
    max_data_extension_time_in_days=1,
    default_ddl_collation="en",
    constraints=[PrimaryKey(name="pk1", column_names=["c1"]), UniqueKey(name="uk1", column_names=["c2"])],
    comment="test table",
)


@pytest.fixture(scope="module")
def tables(schema) -> TableCollection:
    return schema.tables


@pytest.fixture(scope="module")
def table_handle(tables) -> Generator[TableResource, None, None]:
    table_name = random_string(10, "test_table_")
    test_table = copy.deepcopy(test_table_template)
    test_table.name = table_name
    test_table_handle = tables.create(test_table)
    yield test_table_handle
    test_table_handle.delete()


@pytest.mark.parametrize("create_mode", ["errorifexists", "orreplace", "ifnotexists"])
def test_create_from_model_create_mode(tables, create_mode):
    table_name = random_string(10, "test_table_")
    created_handle = tables.create(Table(table_name, columns=[
        TableColumn("c1", "varchar")
    ]), mode="orreplace")
    try:
        assert created_handle.name == table_name
    finally:
        with suppress(Exception):
            created_handle.delete()


def test_create_using_template(session, tables):
    session.sql("create or replace temp stage table_test_stage").collect()
    table_name = random_string(10, "test_table_")
    try:
        session.sql("CREATE or replace temp FILE FORMAT table_test_csv_format TYPE = csv parse_header=true").collect()
        session.file.put("./tests/resources/testCSVheader.csv", "@table_test_stage")
        handle = tables.create(
            table_name,
            template="select array_agg(object_construct(*)) "
                     "from table(infer_schema(location=>'@table_test_stage/testCSVheader.csv', "
                     "file_format=>'table_test_csv_format'))")
        table = handle.fetch(deep=True)
        assert table.columns[0].name == "id"
        assert table.columns[1].name == "name"
        assert table.columns[2].name == "rating"
    finally:
        with suppress(Exception):
            session.sql("drop file format if exists table_test_csv_file_format")
        with suppress(Exception):
            session.sql("drop stage if exists @table_test_stage").collect()
        with suppress(Exception):
            tables[table_name].delete()


@pytest.mark.parametrize("create_mode", ["errorifexists", "orreplace", "ifnotexists"])
def test_create_like(tables, table_handle, create_mode):
    table_name = random_string(10, "test_table_")
    created_handle = tables.create(
        table_name,
        like_table=f"{table_handle.database.name}.{table_handle.schema.name}.{table_handle.name}",
        copy_grants=True,
        mode="orreplace"
    )
    try:
        assert created_handle.name == table_name
    finally:
        with suppress(Exception):
            created_handle.delete()


@pytest.mark.parametrize("create_mode", ["errorifexists", "orreplace", "ifnotexists"])
def test_create_clone(tables, table_handle, create_mode):
    table_name = random_string(10, "test_table_")
    created_handle = tables.create(
        table_name,
        clone_table=f"{table_handle.database.name}.{table_handle.schema.name}.{table_handle.name}",
        copy_grants=True,
        mode="orreplace"
    )
    try:
        assert created_handle.name == table_name
    finally:
        with suppress(Exception):
            created_handle.delete()


@pytest.mark.parametrize("create_mode", ["errorifexists", "orreplace", "ifnotexists"])
def test_create_as_select(tables, table_handle, create_mode):
    table_name = random_string(10, "test_table_")
    copy_grants = True if create_mode == "orreplace" else False
    created_handle = tables.create(
        table_name,
        as_select=f"select * from {table_handle.database.name}.{table_handle.schema.name}.{table_handle.name}",
        copy_grants=copy_grants,
        mode=create_mode
    )
    try:
        assert created_handle.name == table_name
    finally:
        with suppress(Exception):
            created_handle.delete()


def test_create_or_update(tables, db_parameters):
    table_name = random_string(10, "test_table_")
    table_handle = tables[table_name]
    try:
        test_table = copy.deepcopy(test_table_template)
        test_table.name = table_name
        table_handle.create_or_update(test_table)  # new table is created for the first time.
        fetched = table_handle.fetch(deep=True)
        assert_table(fetched, table_name, True, db_parameters)

        test_table_v2 = copy.deepcopy(test_table_template)
        test_table_v2.name = table_name
        test_table_v2.enable_schema_evolution = False
        test_table_v2.change_tracking = False
        test_table_v2.data_retention_time_in_days = None
        test_table_v2.max_data_extension_time_in_days = None
        test_table_v2.default_ddl_collation = "en"
        test_table_v2.columns[1].nullable = False
        test_table_v2.columns.append(TableColumn("c4", "text"))
        test_table_v2.constraints[0].name = "pk2"
        test_table_v2.constraints[1].name = "uk2"
        test_table_v2.comment = "test table 2"
        table_handle.create_or_update(test_table_v2)
        fetched2 = table_handle.fetch(deep=True)
        assert fetched2.enable_schema_evolution is False
        assert fetched2.change_tracking is False
        assert fetched2.data_retention_time_in_days is None
        assert fetched2.max_data_extension_time_in_days is None
        assert len(fetched2.columns) == 4
        assert fetched2.columns[3].name == "C4"
        assert fetched2.columns[3].datatype == "TEXT"
        assert fetched2.columns[3].nullable is True
        assert fetched2.columns[3].identity is False
        assert fetched2.columns[3].identity_start is None
        assert fetched2.columns[3].identity_increment is None
        assert fetched2.constraints[0].name == "PK2"
        assert fetched2.constraints[1].name == "UK2"
    finally:
        with suppress(NotFoundError):
            table_handle.delete()


def test_iter(tables, table_handle, db_parameters):
    listed_tables_deep = list(tables.iter(like=table_handle.name, deep=True))
    assert_table(listed_tables_deep[0], table_handle.name, True, db_parameters)

    listed_tables_not_deep = list(tables.iter(like=table_handle.name, deep=False))
    assert_table(listed_tables_not_deep[0], table_handle.name, False, db_parameters)


def test_fetch(tables, table_handle, db_parameters):
    table_deep = table_handle.fetch(deep=True)
    assert_table(table_deep, table_handle.name, True, db_parameters)

    table_not_deep = table_handle.fetch(deep=False)
    assert_table(table_not_deep, table_handle.name, False, db_parameters)


def test_swap(tables, table_handle):
    table1_name = random_string(10, "test_table_")
    table2_name = random_string(10, "test_table_")
    test_table1_handle = tables[table1_name]
    test_table2_handle = tables[table2_name]

    test_table1 = Table(
        name=table1_name,
        columns=[
            TableColumn("c1", "int"),
        ],
    )
    try:
        _ = tables.create(test_table1)
        test_table2 = Table(
            name=table2_name,
            columns=[
                TableColumn("c2", "int"),
            ],
        )
        _ = tables.create(test_table2)
        test_table1_handle.swap_with(table2_name)
        fetched_table1 = test_table1_handle.fetch(deep=True)
        fetched_table2 = test_table2_handle.fetch(deep=True)
        assert fetched_table1.columns[0].name == "C2"
        assert fetched_table2.columns[0].name == "C1"
    finally:
        with suppress(NotFoundError):
            test_table1_handle.delete()
        with suppress(NotFoundError):
            test_table2_handle.delete()


def test_delete_and_undelete(tables, table_handle):
    table_handle.delete()
    with pytest.raises(NotFoundError):
        table_handle.fetch()
    table_handle.undelete()
    assert table_handle.fetch() is not None


def test_resume_and_suspend_cluster(tables, table_handle):
    table_handle.resume_recluster()
    table_handle.suspend_recluster()


def test_create_or_update_table_negative_no_columns(table_handle):
    not_deep_fetched = table_handle.fetch()
    with pytest.raises(APIError) as error:
        table_handle.create_or_update(not_deep_fetched)
    assert error.match("Columns must be provided for create_or_update")


def test_create_or_update_table_negative_remove_columns(table_handle):
    deep_fetched = table_handle.fetch(deep=True)
    deep_fetched.columns.pop(-1)
    with pytest.raises(APIError) as error:
        table_handle.create_or_update(deep_fetched)
    assert error.match("Can't remove a column for create_or_update.")


def assert_table(table: Table, name: str, deep: bool = False, db_parameters: Dict[str, str] = None) -> None:
    # `Table` is fetched from the server and its attributes are checked.
    assert table.name == normalize_name(name)
    if deep:
        for i in range(len(table.columns)):
            assert table.columns[i].name == normalize_name(table.columns[i].name)
            assert normalize_datatype(table.columns[i].datatype) == normalize_datatype(table.columns[i].datatype)
            assert bool(table.columns[i].nullable) == bool(test_table_template.columns[i].nullable)
            assert table.columns[i].default == test_table_template.columns[i].default
            assert table.columns[i].identity_start == test_table_template.columns[i].identity_start
            assert table.columns[i].identity_increment == test_table_template.columns[i].identity_increment
            assert bool(table.columns[i].identity) == bool(test_table_template.columns[i].identity)
            assert table.columns[i].comment == test_table_template.columns[i].comment
        assert table.columns[2].collate.upper() == "FR"

        fetched_constraints = sorted(table.constraints, key=lambda x: x.name)
        original_constraints = sorted(test_table_template.constraints, key=lambda x: x.name)
        for i in range(len(fetched_constraints)):
            assert fetched_constraints[i].__class__ == original_constraints[i].__class__
            assert normalize_name(fetched_constraints[i].name) == normalize_name(original_constraints[i].name)
            assert (
                [normalize_name(x) for x in fetched_constraints[i].column_names] ==
                [normalize_name(x) for x in original_constraints[i].column_names]
            )
    else:
        assert table.columns is None
        assert table.constraints is None
    assert table.cluster_by == test_table_template.cluster_by
    assert table.comment == test_table_template.comment
    assert table.enable_schema_evolution is test_table_template.enable_schema_evolution
    assert table.change_tracking is test_table_template.change_tracking
    assert table.data_retention_time_in_days == test_table_template.data_retention_time_in_days
    assert table.max_data_extension_time_in_days == test_table_template.max_data_extension_time_in_days
    assert table.default_ddl_collation == test_table_template.default_ddl_collation.upper()
    assert isinstance(table.created_on, datetime.datetime)
    assert table.dropped_on is None
    assert table.database_name == normalize_name(db_parameters["database"])
    assert table.schema_name == normalize_name(db_parameters["schema"])
    assert table.owner_role_type is not None
    assert table.rows == 0
    assert table.automatic_clustering is True
    assert table.search_optimization is False
    assert table.search_optimization_bytes is None
    assert table.search_optimization_progress is None
