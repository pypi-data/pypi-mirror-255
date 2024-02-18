#
# Copyright (c) 2012-2023 Snowflake Computing Inc. All rights reserved.
#
from io import BytesIO
from operator import attrgetter
from textwrap import dedent
from time import sleep

import pytest

from snowflake.core.exceptions import APIError, NotFoundError
from snowflake.core.service import Service, ServiceSpecStageFile

from ..utils import random_string


@pytest.fixture(scope="session")
def seed_temp_service_data():
    return


def test_fetch(services, temp_service, database):
    service = services[temp_service.name].fetch()
    assert (
        service.name == temp_service.name  # for mixed case names
        or service.name.upper()
        == temp_service.name.upper()  # for upper/lower case names
    )
    service.database_name = database.name
    for _ in range(5):
        try:
            assert (
                "This message shows that your installation appears to be working "
                "correctly"
                in services[temp_service.name].get_service_logs(0, "hello-world")
            )
            break
        except APIError as e:
            if (
                "container: hello-world"
            ) not in str(e):
                raise
            sleep(1)


def test_delete(services, session, imagerepo):
    service_name = random_string(5, "test_service_")
    stage_name = random_string(5, "test_stage_")
    session.sql(f"create temp stage {stage_name};").collect()
    spec_file = "spec.yaml"
    stage_file = f"@{stage_name}"
    spec = f"{stage_file}/{spec_file}"
    session.file.put_stream(
        BytesIO(
            dedent(
                f"""
                spec:
                  containers:
                  - name: hello-world
                    image: {imagerepo}/hello-world:latest
                """
            ).encode()
        ),
        spec,
    )
    test_service = Service(
        name=service_name,
        compute_pool="ci_compute_pool",
        spec=ServiceSpecStageFile(stage_location=stage_file, spec_file=spec_file),
        min_instances=1,
        max_instances=1,
    )
    s = services.create(test_service)
    s.delete()
    with pytest.raises(
        NotFoundError,
    ):
        # TODO: HTTP response body: {"description": "list index out of range", "error_details": null}
        #  Looks wrong
        s.fetch()


def test_iter(services, temp_service):
    assert any(
        map(
            lambda e: e
            in tuple(
                map(
                    attrgetter("name"),
                    services.iter(),
                )
            ),
            (
                temp_service.name,  # for mixed case names
                temp_service.name.upper(),  # for upper/lower case names
            ),
        )
    )


def test_suspend_resume(root, services, session, imagerepo):
    stage_name = random_string(5, "test_stage_")
    s_name = random_string(5, "test_service_")
    session.sql(f"create temp stage {stage_name};").collect()
    spec_file = "spec.yaml"
    stage_file = f"@{stage_name}"
    spec = f"{stage_file}/{spec_file}"
    session.file.put_stream(
        BytesIO(
            dedent(
                f"""
                spec:
                  containers:
                  - name: web-server
                    image: {imagerepo}/nginx:latest
                 """
            ).encode()
        ),
        spec,
    )
    test_s = Service(
        name=s_name,
        compute_pool="ci_compute_pool",
        spec=ServiceSpecStageFile(stage_location=stage_file, spec_file=spec_file),
        min_instances=1,
        max_instances=1,
    )
    s = services.create(test_s)
    try:
        for _ in range(10):
            web_server = s.get_service_status(1)[0]
            if web_server["status"] in ("READY",):
                break
            sleep(1)
        else:
            pytest.fail("web_server never came online")
        services[test_s.name].suspend()
        for _ in range(10):
            web_server = s.get_service_status(1)[0]
            if web_server["status"] in ("SUSPENDED",):
                break
            sleep(1)
        else:
            pytest.fail("web_server never went to sleep")
        services[test_s.name].resume()
        for _ in range(60):
            web_server = s.get_service_status(1)[0]
            if web_server["status"] in ("READY",):
                break
            print(f"{web_server['status']}")
            sleep(1)
        else:
            pytest.fail("web_server never resumed")
    finally:
        s.delete()


def test_create_with_spec_inline(services, temp_service_from_spec_inline, database):
    service = services[temp_service_from_spec_inline.name].fetch()
    assert (
            service.name == temp_service_from_spec_inline.name  # for mixed case names
            or service.name.upper()
            == temp_service_from_spec_inline.name.upper()  # for upper/lower case names
    )
    assert 'name: "hello-world"' in service.spec.specification
