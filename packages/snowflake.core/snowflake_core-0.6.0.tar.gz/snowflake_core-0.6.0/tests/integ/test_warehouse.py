# Copyright (c) 2012-2023 Snowflake Computing Inc. All rights reserved.
import time

from contextlib import suppress

import pytest

from snowflake.core._common import CreateMode
from snowflake.core.exceptions import NotFoundError
from snowflake.core.warehouse import Warehouse

from ..utils import random_string


def test_create_and_delete(warehouses, session):
    warehouse_name = random_string(5, "test_create_and_delete_warehouse_")
    test_warehouse = Warehouse(
        name=warehouse_name,
        warehouse_size="SMALL",
        auto_suspend=500,
    )

    warehouse_ref = None
    try:
        # Test warehouse create.
        warehouse_ref = warehouses.create(test_warehouse, mode=CreateMode.or_replace)
        warehouse_list = warehouses.iter(like=warehouse_name)
        result = next(warehouse_list)
        assert warehouse_name.upper() == result.name.upper()
        assert result.size.upper() == "SMALL"
        assert result.auto_suspend == 500
        with pytest.raises(TypeError):
            test_empty_name_warehouse = Warehouse() # noqa: F841
    finally:
        # This cleans things up but also covers warehouse deletion.
        with suppress(NotFoundError):
            warehouse_ref.delete()
        warehouse_list = warehouses.iter(like=warehouse_name)
        for warehouse in warehouse_list:
            if warehouse is not None:
                assert warehouse_name.upper() != warehouse.name.upper()
        session.sql("USE WAREHOUSE TESTWH_PYTHON").collect()


def test_create_or_update(warehouses, session):
    warehouse_name = random_string(5, "test_create_or_update_warehouse_")
    test_warehouse = Warehouse(name=warehouse_name)
    warehouse_ref = None
    try:
        # Test create when the warehouse does not exist.
        warehouse_ref = warehouses[warehouse_name]
        warehouse_ref.create_or_update(test_warehouse)
        warehouse_list = warehouses.iter(like=warehouse_name)
        result = next(warehouse_list)
        assert warehouse_name.upper() == result.name.upper()

    finally:
        with suppress(NotFoundError):
            warehouse_ref.delete()
        session.sql("USE WAREHOUSE TESTWH_PYTHON").collect()

    # Test altering the warehouse.
    warehouse_name = random_string(5, "test_create_or_update_warehouse_")
    test_warehouse = Warehouse(
        name=warehouse_name,
        warehouse_size="SMALL",
    )

    test_alter_warehouse = Warehouse(
        name=warehouse_name,
        warehouse_size="LARGE",
    )
    try:
        # Test create when the warehouse exists.
        warehouse_ref = warehouses[warehouse_name]
        warehouse_ref.create_or_update(test_warehouse)
        warehouse_list = warehouses.iter(like=warehouse_name)
        result = next(warehouse_list)
        assert result.size.upper() == "SMALL"

        warehouse_ref.create_or_update(test_alter_warehouse)
        warehouse_list = warehouses.iter(like=warehouse_name)
        result = next(warehouse_list)
        assert result.size.upper() == "LARGE"

    finally:
        with suppress(NotFoundError):
            warehouse_ref.delete()
        session.sql("USE WAREHOUSE TESTWH_PYTHON").collect()


def test_create_or_update_with_wildcardish_name(warehouses, session):
    # 2023-10-20(bwarsaw): Don't forget we have to filter out pre-existing warehouses, since we do not
    # have a clean test environment.

    # Create multiple warehouses with similar names.  Because the underscore is a wildcard character, and SHOW
    # WAREHOUSE does not support ILIKE or RLIKE, names can overlap.
    warehouse1_name = random_string(5, "warehouseXabcdef_")
    warehouse2_name = random_string(5, "warehouse_abcdef_")

    warehouse_refs = []
    try:
        test1_warehouse = Warehouse(name=warehouse1_name)
        test2_warehouse = Warehouse(name=warehouse2_name)
        w1_ref = warehouses[warehouse1_name]
        w2_ref = warehouses[warehouse2_name]
        w1_ref.create_or_update(test1_warehouse)
        w2_ref.create_or_update(test2_warehouse)
        warehouse_refs.append(w1_ref)
        warehouse_refs.append(w2_ref)
        warehouse_names = set(
            warehouse.name
            for warehouse in warehouses.iter())
        assert warehouse1_name.upper() in warehouse_names
        assert warehouse2_name.upper() in warehouse_names
    finally:
        for warehouse_ref in warehouse_refs:
            with suppress(NotFoundError):
                warehouse_ref.delete()
        session.sql("USE WAREHOUSE TESTWH_PYTHON").collect()


def test_create_or_update_twice_without_change(warehouses, session):
    # Create multiple warehouses with the same name and no parameter change.
    warehouse1_name = random_string(5, "test_wh_pattern1_")
    warehouse2_name = warehouse1_name

    warehouse_refs = []
    try:
        test1_warehouse = Warehouse(name=warehouse1_name)
        test2_warehouse = Warehouse(name=warehouse2_name)
        warehouse_refs.append(warehouses[warehouse1_name])
        warehouse_refs.append(warehouses[warehouse2_name])
        warehouse_refs[0].create_or_update(test1_warehouse)
        warehouse_refs[1].create_or_update(test2_warehouse)
        warehouse_names = set(
            warehouse.name.lower()
            for warehouse in warehouses.iter(like="%test_wh_pattern1_%"))
        assert warehouse1_name in warehouse_names
        assert warehouse_refs[0].fetch().size.upper() == 'X-SMALL'
    finally:
        for warehouse_ref in warehouse_refs:
            with suppress(NotFoundError):
                warehouse_ref.delete()
        session.sql("USE WAREHOUSE TESTWH_PYTHON").collect()


def test_create_or_update_twice_with_change(warehouses, session):
    # Create multiple warehouses with the same name, but this time the second one has a parameter change, so
    # it gets updated.
    warehouse1_name = random_string(5, "test_wh_pattern1_")
    warehouse2_name = warehouse1_name

    warehouse_refs = []
    try:
        test1_warehouse = Warehouse(name=warehouse1_name)
        test2_warehouse = Warehouse(
            name=warehouse2_name,
            warehouse_size='XSMALL',
        )
        w1_ref = warehouses[warehouse1_name]
        w2_ref = warehouses[warehouse2_name]
        w1_ref.create_or_update(test1_warehouse)
        w2_ref.create_or_update(test2_warehouse)
        warehouse_refs.append(w1_ref)
        warehouse_refs.append(w2_ref)
        warehouse_names = set(
            warehouse.name.lower()
            for warehouse in warehouses.iter(like="%test_wh_pattern1_%"))
        assert warehouse1_name in warehouse_names
        assert warehouse_refs[0].fetch().size.upper() == 'X-SMALL'
    finally:
        for warehouse_ref in warehouse_refs:
            with suppress(NotFoundError):
                warehouse_ref.delete()
        session.sql("USE WAREHOUSE TESTWH_PYTHON").collect()


def test_iter(warehouses, session):
    warehouse_test_name_list = [
        random_string(5, "test_warehouse_"),
        random_string(5, "test_warehouse_"),
    ]
    warehouse_ref = []

    try:
        for name in warehouse_test_name_list:
            test_warehouse = Warehouse(name=name)
            warehouse_ref.append(warehouses.create(warehouse=test_warehouse))

        warehouse_list = []
        test_warehouses = warehouses.iter(like="%test_warehouse_%")
        for warehouse in test_warehouses:
            warehouse_list.append(warehouse.name.upper())
        for name in warehouse_test_name_list:
            assert name.upper() in warehouse_list

    finally:
        with suppress(NotFoundError):
            for ref in warehouse_ref:
                ref.delete()
        session.sql("USE WAREHOUSE TESTWH_PYTHON").collect()


def test_suspend_and_resume(warehouses, session):
    warehouse_name = random_string(5, "test_suspend_and_resume_warehouse_")
    test_warehouse = Warehouse(name=warehouse_name)

    warehouse_ref = None
    try:
        warehouse_ref = warehouses.create(test_warehouse)
        # Test warehouse suspend.
        warehouse_ref.suspend()
        result = next(warehouses.iter(like=warehouse_name))
        assert result.state in ("SUSPENDED", "SUSPENDING")

        # Test warehouse resume.
        warehouse_ref.resume()
        result = next(warehouses.iter(like=warehouse_name))
        assert result.state in ("STARTED", "RESUMING")

    finally:
        with suppress(NotFoundError):
            warehouse_ref.delete()
        session.sql("USE WAREHOUSE TESTWH_PYTHON").collect()


def test_fetch(warehouses, session):
    warehouse_name = random_string(5, "test_fetch_warehouse_")
    test_warehouse = Warehouse(name=warehouse_name)

    warehouse_ref = None
    try:
        warehouse_ref = warehouses.create(test_warehouse)
        result = warehouse_ref.fetch()
        assert warehouse_name.upper() == result.name.upper()
    finally:
        with suppress(NotFoundError):
            warehouse_ref.delete()
        session.sql("USE WAREHOUSE TESTWH_PYTHON").collect()


def test_fetch_property(warehouses, session):
    warehouse_name = random_string(5, "test_fetch_warehouse_")
    test_warehouse = Warehouse(
        name=warehouse_name,
        warehouse_size='XSMALL',
    )

    warehouse_ref = None
    try:
        warehouse_ref = warehouses.create(test_warehouse)
        result = warehouse_ref.fetch()
        assert result.name.upper() == warehouse_name.upper()
        assert result.size.upper() == 'X-SMALL'
    finally:
        with suppress(NotFoundError):
            warehouse_ref.delete()
        session.sql("USE WAREHOUSE TESTWH_PYTHON").collect()


def test_abort_all_queries(warehouses, session):
    warehouse_name = random_string(5, "test_abort_all_queries_warehouse_")
    test_warehouse = Warehouse(name=warehouse_name)

    warehouse_ref = None
    try:
        warehouse_ref = warehouses.create(test_warehouse)
        time.sleep(5)
        warehouse_ref.abort_all_queries()
        time.sleep(5)
        result = next(warehouses.iter(like=warehouse_name))
        assert result.running == 0 and result.queued == 0

    finally:
        with suppress(NotFoundError):
            warehouse_ref.delete()
        session.sql("USE WAREHOUSE TESTWH_PYTHON").collect()


def test_rename(warehouses, session):
    warehouse_name = random_string(5, "test_rename_warehouse_")
    test_warehouse = Warehouse(name=warehouse_name)

    warehouse_new_name = random_string(5, "test_new_name_warehouse_")
    assert warehouse_name != warehouse_new_name
    # test_new_name_warehouse = Warehouse(name=warehouse_new_name)

    warehouse_ref = None
    try:
        with pytest.raises(TypeError):
            test_empty_name_warehouse = Warehouse() # noqa: F841

        # Rename the warehouse to a new name.
        warehouse_ref = warehouses.create(test_warehouse)
        warehouse_ref.rename(warehouse_new_name)
        result1 = warehouses.iter(like=warehouse_name)
        result2 = warehouses.iter(like=warehouse_new_name)
        assert len(list(result1)) == 0 and len(list(result2)) == 1

        # Change the warehouse name back.
        warehouses[warehouse_new_name].rename(warehouse_name)
        result1 = warehouses.iter(like=warehouse_name)
        result2 = warehouses.iter(like=warehouse_new_name)
        assert len(list(result1)) == 1 and len(list(result2)) == 0
    finally:
        with suppress(NotFoundError):
            warehouse_ref.delete()
        session.sql("USE WAREHOUSE TESTWH_PYTHON").collect()


def test_properties(warehouses, session):
    warehouse_name = random_string(5, "test_create_and_delete_warehouse_")
    test_warehouse = Warehouse(
        name=warehouse_name,
        warehouse_size="SMALL",
        warehouse_type="STANDARD",
        auto_suspend=500,
        auto_resume="true",
        max_concurrency_level=10,
        statement_timeout_in_seconds=17000
    )

    warehouse_ref = None
    try:
        warehouse_ref = warehouses.create(test_warehouse)
        warehouse_list = warehouses.iter(like=warehouse_name)
        result = next(warehouse_list)

        assert warehouse_name.upper() == result.name.upper()
        assert result.size.upper() == "SMALL"
        assert result.type.upper() == "STANDARD"
        assert result.auto_suspend == 500
        assert result.auto_resume.upper() == "TRUE"
        assert result.max_concurrency_level == 10
        assert result.statement_timeout_in_seconds == 17000
        with pytest.raises(TypeError):
            test_empty_name_warehouse = Warehouse() # noqa: F841

    finally:
        with suppress(NotFoundError):
            warehouse_ref.delete()
        session.sql("USE WAREHOUSE TESTWH_PYTHON").collect()

@pytest.mark.skip(reason="instable because no isolation of test env")
def test_no_warehouses(warehouses, session):
    found = list(wh.name for wh in warehouses.iter())
    pre_existing = list(wh.name for wh in warehouses._pre_existing)
    new_warehouses = set(found) - set(pre_existing)
    assert len(new_warehouses) == 0
