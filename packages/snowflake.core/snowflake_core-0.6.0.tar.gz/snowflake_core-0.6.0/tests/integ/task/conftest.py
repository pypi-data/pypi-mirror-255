# Copyright (c) 2012-2023 Snowflake Computing Inc. All rights reserved.

import os
import uuid

import pytest

from snowflake.core import Root
from snowflake.core.database import DatabaseCollection  # noqa: F401
from snowflake.core.task import TaskCollection


RUNNING_ON_GH = os.getenv("GITHUB_ACTIONS") == "true"
TEST_SCHEMA = "GH_JOB_{}".format(str(uuid.uuid4()).replace("-", "_"))


@pytest.fixture(scope="module")
def tasks(root: Root, db_parameters, test_schema) -> TaskCollection:
    return root.databases[db_parameters["database"]].schemas[test_schema].tasks
