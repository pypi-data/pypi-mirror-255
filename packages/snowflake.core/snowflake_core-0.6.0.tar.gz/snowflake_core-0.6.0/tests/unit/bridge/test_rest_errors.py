#
# Copyright (c) 2012-2023 Snowflake Computing Inc. All rights reserved.
#

import json

import pytest

from snowflake.core._internal.bridge.rest_errors import (
    BadGateway,
    BadRequest,
    Forbidden,
    GatewayTimeout,
    InternalServerError,
    NotFound,
    RestError,
    ServiceUnavailable,
    UnauthorizedRequest,
)


class TestRestErrors:
    def test_rest_error_default_values(self):
        r = RestError()
        assert r.msg != "", "message cannot be empty"
        assert r.status_code == 500, "status code mismatch!"

    def test_rest_error_details(self):
        error_details = {
            "errno": "2345",
            "query": "sample query",
            "sqlstate": "test_state",
            "sfqid": "sf_id",
        }
        r = RestError("sample error", error_details=error_details)
        assert r.msg != "", "message cannot be empty"
        assert r.status_code == 500, "status code mismatch!"
        response_data = r.get_http_response().data
        actual_response = json.loads(response_data)

        assert (
            actual_response["message"]
            == f'{{error: "sample error", details: "{error_details}"}}'
        ), "error details mismatch!"

    @pytest.mark.parametrize(
        "status_code, error",
        [
            (400, BadRequest),
            (401, UnauthorizedRequest),
            (403, Forbidden),
            (404, NotFound),
            (500, InternalServerError),
            (502, BadGateway),
            (503, ServiceUnavailable),
            (504, GatewayTimeout),
        ],
    )
    def test_status_codes(self, status_code, error):
        with pytest.raises(error) as http_error:
            raise error("test error!")
        assert http_error.value.status_code == status_code
