#
# Copyright (c) 2012-2023 Snowflake Computing Inc. All rights reserved.
#

from contextlib import ExitStack
from unittest.mock import patch

import pytest

from snowflake.connector import SnowflakeConnection, errors
from snowflake.connector.cursor import DictCursor
from snowflake.core._internal.bridge.executor import SnowExecute
from snowflake.core._internal.bridge.rest_errors import NotFound


class TestSnowExecutor:
    @patch("snowflake.connector.cursor", spec=DictCursor)
    @patch("snowflake.connector", spec=SnowflakeConnection)
    def test_execute(self, mocked_conn, mocked_cursor):
        mocked_response = [
            {"col1": "row1", "col2": "row1", "col3": "row1"},
            {"col1": "row2", "col2": "row2", "col3": "row2"},
        ]

        with ExitStack() as stack:
            stack.enter_context(
                patch.object(mocked_conn, "cursor", return_value=mocked_cursor)
            )
            stack.enter_context(
                patch.object(mocked_cursor, "fetchall", return_value=mocked_response)
            )
            executor = SnowExecute(mocked_conn)
            actual_response = executor.execute("select * from test_table")

            assert mocked_response == actual_response, "Response mismatch!"

    @patch("snowflake.connector.cursor", spec=DictCursor)
    @patch("snowflake.connector", spec=SnowflakeConnection)
    def test_execute_desired_properties(self, mocked_conn, mocked_cursor):
        mocked_response = [
            {"col1": "row1", "col2": "row1", "col3": "row1"},
            {"col1": "row2", "col2": "row2", "col3": "row2"},
        ]

        with ExitStack() as stack:
            stack.enter_context(
                patch.object(mocked_conn, "cursor", return_value=mocked_cursor)
            )
            stack.enter_context(
                patch.object(mocked_cursor, "fetchall", return_value=mocked_response)
            )
            executor = SnowExecute(mocked_conn)
            actual_response = executor.execute(
                "select * from test_table",
                desired_properties=["col1", "non_existent_col"],
            )
            assert len(mocked_response) == len(actual_response), "Length mismatch!"
            for actual_row, expected_row in zip(actual_response, mocked_response):
                assert "non_existent_col" in actual_row
                assert actual_row["col1"] == expected_row["col1"]

    @patch("snowflake.connector.cursor", spec=DictCursor)
    @patch("snowflake.connector", spec=SnowflakeConnection)
    def test_execute_empty_result(self, mocked_conn, mocked_cursor):
        mocked_response = []
        with ExitStack() as stack:
            stack.enter_context(
                patch.object(mocked_conn, "cursor", return_value=mocked_cursor)
            )
            stack.enter_context(
                patch.object(mocked_cursor, "fetchall", return_value=mocked_response)
            )
            executor = SnowExecute(mocked_conn)
            actual_response = executor.execute("show tasks like 'asdf'")
            assert len(mocked_response) == len(actual_response), "Length mismatch!"

    @patch("snowflake.connector.cursor", spec=DictCursor)
    @patch("snowflake.connector", spec=SnowflakeConnection)
    def test_execute_successful_response(self, mocked_conn, mocked_cursor):
        mocked_response = [{"status": "successful"}]
        with ExitStack() as stack:
            stack.enter_context(
                patch.object(mocked_conn, "cursor", return_value=mocked_cursor)
            )
            stack.enter_context(
                patch.object(mocked_cursor, "fetchall", return_value=mocked_response)
            )
            executor = SnowExecute(mocked_conn)
            actual_response = executor.execute("create task t1 as AS SELECT 1;")
            assert "description" in actual_response[0]
            assert actual_response[0]["description"] == "successful"

    @patch("snowflake.connector.cursor", spec=DictCursor)
    @patch("snowflake.connector", spec=SnowflakeConnection)
    def test_execute_throws_error(self, mocked_conn, mocked_cursor):
        with ExitStack() as stack:
            stack.enter_context(
                patch.object(mocked_conn, "cursor", return_value=mocked_cursor)
            )
            stack.enter_context(
                patch.object(
                    mocked_cursor,
                    "execute",
                    side_effect=Exception("runtime exception"),
                )
            )
            executor = SnowExecute(mocked_conn)
            try:
                executor.execute("invalid query")
                pytest.fail("test_execute_throws_error failed!")
            except Exception:
                pass

    @patch("snowflake.connector.cursor", spec=DictCursor)
    @patch("snowflake.connector", spec=SnowflakeConnection)
    def test_execute_not_found_error(self, mocked_conn, mocked_cursor):
        with ExitStack() as stack:
            stack.enter_context(
                patch.object(mocked_conn, "cursor", return_value=mocked_cursor)
            )
            stack.enter_context(
                patch.object(
                    mocked_cursor,
                    "execute",
                    side_effect=errors.ProgrammingError(
                        msg="Object Not Found", errno=2003
                    ),
                )
            )
            executor = SnowExecute(mocked_conn)
            try:
                executor.execute("invalid query")
                pytest.fail("test_execute_throws_error failed!")
            except NotFound as e:
                assert isinstance(e, NotFound)

    @pytest.mark.skip()
    @patch("snowflake.connector.cursor", spec=DictCursor)
    @patch("snowflake.connector", spec=SnowflakeConnection)
    def test_execute_many(self, mocked_conn, mocked_cursor):
        mocked_response = [
            [
                {"col1": "row1", "col2": "row1", "col3": "row1"},
                {"col1": "row2", "col2": "row2", "col3": "row2"},
            ],
            [{"1": 1}],
        ]

        with ExitStack() as stack:
            stack.enter_context(
                patch.object(mocked_conn, "cursor", return_value=mocked_cursor)
            )
            mocked_fetchall = stack.enter_context(
                patch.object(mocked_cursor, "fetchall", autospec=True)
            )
            mocked_nextset = stack.enter_context(
                patch.object(mocked_cursor, "nextset", autospec=True)
            )
            mocked_fetchall.side_effect = [
                [
                    {"col1": "row1", "col2": "row1", "col3": "row1"},
                    {"col1": "row2", "col2": "row2", "col3": "row2"},
                ],
                [{"1": 1}],
            ]
            mocked_nextset.side_effect = [{}, None]
            executor = SnowExecute(mocked_conn)
            actual_response = executor.execute_many(
                "select * from test_table; select 1"
            )

            assert mocked_response == actual_response, "Response mismatch!"
