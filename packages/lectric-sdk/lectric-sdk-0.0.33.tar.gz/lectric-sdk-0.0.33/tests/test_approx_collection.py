import pytest
from typing import List

from .utils import *
import lectric as lc

COLL_DIM = 8

@pytest.fixture(scope='module')
def collection_name() -> str:
    coll_name: str = gen_random_name(10)
    return coll_name


@pytest.fixture(scope="module")
def collection_in_spec(collection_name: str) -> lc.CollectionInSpec:
    fields: List[lc.FieldSchema] = [
        lc.FieldSchema(name="id", dtype=lc.DataType.INT64, is_primary=True,
            auto_id=True, description="Primary key"),
        lc.FieldSchema(name="vecs", dtype=lc.DataType.FLOAT_VECTOR,
            dim=COLL_DIM, description="Data embeddings")
    ]
    return lc.CollectionInSpec(collection_name,
            coll_schema=lc.CollectionSchema(fields=fields, description="Test Schema description"))

# Also a test for create
@pytest.fixture(scope="module")
def collection(client: lc.LectricClient, collection_in_spec: lc.CollectionInSpec) -> lc.Collection:
    del_collection_if_exists(collection_in_spec.name, client)

    # Create
    coll: lc.Collection = client.create_collection(collection_in_spec)

    assert coll.name == collection_in_spec.name
    assert coll.coll_schema.to_dict() == collection_in_spec.coll_schema.to_dict()
    yield coll

    del_collection_if_exists(collection_in_spec.name, client)


@pytest.fixture(scope="module")
def three_collections(client: lc.LectricClient) -> List[lc.Collection]:
    NUM_COLLS = 3

    coll_in_specs = [gen_random_binary_collection_spec(COLL_DIM) for _ in range(NUM_COLLS)]

    collections: List[lc.Collection] = []

    for coll_in_spec in coll_in_specs:
        coll: lc.Collection = client.create_collection(coll_in_spec)

        assert coll.name == coll_in_spec.name
        assert coll.consistency_level == coll_in_spec.consistency_level
        assert coll.coll_schema.to_dict() == coll_in_spec.coll_schema.to_dict()

        collections.append(coll)

    yield collections

    # Delete the ones just created them
    for coll in collections:
        del_collection_if_exists(coll.name, client)


# NOTE: Done in fixtures
def test_create(collection: lc.Collection):
    assert collection

def test_empty(client: lc.LectricClient , collection: lc.Collection):
    assert client.is_collection_empty(collection.name)

def test_size(client: lc.LectricClient , collection: lc.Collection):
    assert client.sizeof(collection.name) == 0

def test_get(client: lc.LectricClient, collection: lc.Collection):
    coll: lc.Collection = client.get_collection(collection.name)
    assert coll.name == collection.name


def test_list(client: lc.LectricClient, three_collections: List[lc.Collection]):
    q_colls: List[lc.Collection] = client.list_collections()
    assert len(q_colls) >= len(three_collections)


# NOTE: Done in fixtures
def test_delete(collection: lc.Collection):
    assert collection

