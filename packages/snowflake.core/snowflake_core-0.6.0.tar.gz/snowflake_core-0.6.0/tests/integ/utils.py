# Copyright (c) 2012-2023 Snowflake Computing Inc. All rights reserved.

from typing import List

from snowflake.snowpark import Row, Session

from ..utils import random_string


def random_object_name() -> str:
    return random_string(8, prefix="test_object_")


def get_task_history(session: Session, name: str) -> List[Row]:
    query = (
        f"select * from table(information_schema.task_history("
        f"scheduled_time_range_start=>dateadd('hour',-1,current_timestamp()),"
        f"result_limit => 10,task_name=>'{name}'))"
    )
    return session.sql(query).collect()
