#
# Copyright (c) 2012-2023 Snowflake Computing Inc. All rights reserved.
#

from urllib.parse import urlparse

import pytest

from snowflake.connector import connect
from snowflake.core._internal.bridge.resources.task_resource import TaskResource
from snowflake.core._internal.bridge.snow_request import SnowRequest


@pytest.mark.skip()
def test_create():
    req_body = {
        "name": "t1",
        "warehouse": "snowapi_wh",
        "schedule": {"minutes": "1"},
        "comment": "test comment",
        "paramsSpec": {
            "abort_detached_query": "true",
            "autocommit": "true",
            "client_prefetch_thread": "4",
        },
        "definition": "desc warehouse snowapi_wh",
        "predecessors": ["t2", "snowapi_db.snowapi_schema.t3"],
        "when": "1=1",
        "allow_overlapping_execution": "true",
        "error_integration": "something",
    }

    method = "POST"
    url = urlparse(
        "https://api.snowflakecomputing.comapi/v2/databases/snowapi_db/schemas/snowapi_schema/tasks"
    )
    query_params = {"createMode": "orReplace"}
    body = req_body
    conn_obj = connect(user="snowapi_user", password="<>", account="sfctest0")
    req = SnowRequest(method=method, url=url, query_params=query_params, body=body)
    task_obj = TaskResource(req, conn_obj)
    retVal = task_obj.execute()
    assert retVal == "{description: successful}"
