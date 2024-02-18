#
# Copyright (c) 2012-2023 Snowflake Computing Inc. All rights reserved.
#

from urllib.parse import urlparse

import pytest

from snowflake.connector import connect
from snowflake.core._internal.bridge.resources.computepools_resource import (
    ComputePoolsResource,
)
from snowflake.core._internal.bridge.snow_request import SnowRequest


@pytest.mark.skip()
def test_create():
    req_body = {
        "name": "cp1",
        "warehouse": "snowapi_wh",
        "min_nodes": "1",
        "max_nodes": "2",
        "instance_family": "random",
        "gpu_options": {"accelerator": "random accelerator"},
        "auto_resume": "true",
    }

    method = "POST"
    url = urlparse("https://api.snowflakecomputing.comapi/api/v2/compute-pools")
    query_params = {"createMode": "orReplace"}
    body = req_body
    conn_obj = connect(user="snowapi_user", password="<>", account="sfctest0")
    req = SnowRequest(method=method, url=url, query_params=query_params, body=body)
    cp_obj = ComputePoolsResource(req, conn_obj)
    retVal = cp_obj.execute()
    assert retVal == "{description: successful}"
