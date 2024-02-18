#
# Copyright (c) 2012-2023 Snowflake Computing Inc. All rights reserved.
#
from contextlib import suppress

import pytest

from snowflake.core.compute_pool import ComputePool
from snowflake.core.exceptions import APIError, NotFoundError

from ..utils import random_string


def test_fetch(compute_pools, temp_cp):
    cp = compute_pools[temp_cp.name].fetch()
    assert (
        cp.name == temp_cp.name  # for mixed case names
        or cp.name.upper() == temp_cp.name.upper()  # for upper/lower case names
    )
    assert cp.min_nodes == 1
    assert cp.max_nodes == 1
    assert cp.created_on


def test_delete(compute_pools):
    cp_name = random_string(5, "test_cp_")
    test_cp = ComputePool(
        name=cp_name,
        instance_family="STANDARD_1",
        min_nodes=1,
        max_nodes=1,
    )
    compute_pools.create(test_cp)
    compute_pools[test_cp.name].delete()
    with pytest.raises(
        NotFoundError,
    ):
        compute_pools[test_cp.name].fetch()


def test_iter(compute_pools, temp_cp):
    for cp in compute_pools.iter(like=temp_cp.name):
        assert cp.name in (
            temp_cp.name,  # for mixed case names
            temp_cp.name.upper(),  # for upper/lower case names
        )
        assert cp.instance_family == "STANDARD_1"
        assert cp.min_nodes == 1
        assert cp.max_nodes == 1


def test_suspend_resume(compute_pools, temp_cp):
    assert compute_pools[temp_cp.name].fetch().state in (
        "IDLE",
        "RUNNING",
        "STARTING",
    )
    compute_pools[temp_cp.name].suspend()
    assert compute_pools[temp_cp.name].fetch().state == "SUSPENDED"
    compute_pools[temp_cp.name].resume()
    assert compute_pools[temp_cp.name].fetch().state in (
        "IDLE",
        "RUNNING",
        "STARTING",
        "IDLE",
    )


def test_stop_all_services(compute_pools, temp_cp):
    pytest.skip("TODO: add test for this once we add snowservice tests")


def test_create_or_update_compute_pool(compute_pools):
    cp_name = random_string(5, "test_cp_")
    test_cp = ComputePool(
        name=cp_name,
        instance_family="STANDARD_1",
        min_nodes=1,
        max_nodes=1,
        auto_resume=False,
        comment="abc",
    )
    cp_ref = compute_pools[cp_name]
    cp_ref.create_or_update(test_cp)
    try:
        fetched = cp_ref.fetch()
        assert fetched.instance_family == "STANDARD_1"
        assert fetched.min_nodes == 1
        assert fetched.max_nodes == 1
        assert fetched.auto_resume is False
        assert fetched.comment == "abc"

        fetched.min_nodes = 2
        fetched.max_nodes = 2
        fetched.auto_resume = None
        fetched.comment = "def"
        cp_ref.create_or_update(fetched)
        fetched_again = cp_ref.fetch()
        assert fetched_again.instance_family == "STANDARD_1"
        assert fetched_again.min_nodes == 2
        assert fetched_again.max_nodes == 2
        assert fetched_again.auto_resume is True
        assert fetched_again.comment == "def"

        with pytest.raises(APIError) as exinfo:
            fetched.instance_family = "STANDARD_2"
            cp_ref.create_or_update(fetched)
        assert exinfo.match("instance_family` of a computer pool can't be changed")
        assert exinfo.value.status == 400
    finally:
        with suppress(NotFoundError):
            cp_ref.delete()
