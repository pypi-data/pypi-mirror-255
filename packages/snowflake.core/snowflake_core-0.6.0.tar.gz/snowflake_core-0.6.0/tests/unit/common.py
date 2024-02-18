#
# Copyright (c) 2012-2023 Snowflake Computing Inc. All rights reserved.
#

from unittest.mock import MagicMock

from snowflake.core._common import (
    CreateMode,
    SchemaObjectCollectionParent,
    SchemaObjectReferenceMixin,
)
from snowflake.core.database import DatabaseCollection
from snowflake.core.schema import SchemaResource


class XyzCollection(SchemaObjectCollectionParent["XyzReference"]):
    def __init__(self, schema: "SchemaResource") -> None:
        super().__init__(schema, XyzReference)


class XyzReference(SchemaObjectReferenceMixin):
    def __init__(self, name: str, collection: "XyzCollection") -> None:
        self.collection = collection
        self.name = name


def test_collection_and_references():
    mock_session = MagicMock()
    db_collection = DatabaseCollection(mock_session)
    my_db_ref = db_collection["my_db"]
    assert my_db_ref.name == "my_db"
    assert my_db_ref.schemas.database.collection is db_collection

    my_schema_ref = my_db_ref.schemas["my_schema"]
    assert my_schema_ref.name == "my_schema"
    assert my_schema_ref.database.name == "my_db"
    assert my_schema_ref.collection is my_db_ref.schemas
    assert my_schema_ref.collection.database is my_db_ref is my_schema_ref.database

    xyz_collection = XyzCollection(my_schema_ref)
    my_xyz_ref = xyz_collection["my_xyz"]

    assert my_xyz_ref.name == "my_xyz"
    assert my_xyz_ref.schema.name == "my_schema"
    assert my_xyz_ref.database.name == "my_db"
    assert my_xyz_ref.schema is my_schema_ref
    assert my_xyz_ref.database is my_db_ref
    assert my_xyz_ref.collection is xyz_collection
    assert my_xyz_ref.fully_qualified_name == "my_db.my_schema.my_xyz"

    for key in xyz_collection:
        assert key == "my_xyz"

    for key in xyz_collection.keys():
        assert key == "my_xyz"

    for item in xyz_collection.items():
        assert item[0] == "my_xyz"
        assert item[1] is my_xyz_ref

    for value in xyz_collection.values():
        assert value is my_xyz_ref


def test_createmode():
    assert CreateMode["orREPlace"] is CreateMode.or_replace
    assert CreateMode["orREPlace"] == CreateMode.or_replace.value
    assert CreateMode["ifNOTExists"] is CreateMode.if_not_exists
    assert CreateMode["ErroRifexists"] is CreateMode.error_if_exists
