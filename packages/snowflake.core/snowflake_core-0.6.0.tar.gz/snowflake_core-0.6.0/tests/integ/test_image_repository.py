#
# Copyright (c) 2012-2023 Snowflake Computing Inc. All rights reserved.
#

from operator import attrgetter

import pytest

from snowflake.core.exceptions import ServerError
from snowflake.core.image_repository import ImageRepository

from ..utils import random_string


def test_fetch(image_repositories, temp_ir):
    ir: ImageRepository = image_repositories[temp_ir.name].fetch()
    assert (
        ir.name == temp_ir.name  # for mixed case names
        or ir.name.upper() == temp_ir.name.upper()  # for upper/lower case names
    )
    assert ir.created_on
    assert ir.repository_url


def test_delete(image_repositories):
    ir_name = random_string(5, "test_ir_")
    test_ir = ImageRepository(
        name=ir_name,
    )
    image_repositories.create(test_ir)
    image_repositories[test_ir.name].delete()
    with pytest.raises(
        ServerError,
    ):
        # TODO: HTTP response body: {"description": "list index out of range", "error_details": null}
        #  Looks wrong
        image_repositories[test_ir.name].fetch()


def test_iter(image_repositories, temp_ir):
    assert any(
        map(
            lambda e: e
            in tuple(
                map(
                    attrgetter("name"),
                    image_repositories.iter(),
                )
            ),
            (
                temp_ir.name,  # for mixed case names
                temp_ir.name.upper(),  # for upper/lower case names
            ),
        )
    )
