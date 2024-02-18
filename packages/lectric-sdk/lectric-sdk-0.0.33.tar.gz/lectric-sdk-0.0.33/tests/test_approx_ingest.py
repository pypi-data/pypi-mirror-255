import lectric as lc
import pytest
from typing import List

from .utils import (
    del_collection_if_exists,
    gen_random_fp_collection_spec,
    gen_random_name,
    gen_random_fp_vectors,
    create_collection)

COLL_DIM = 12

@pytest.fixture(scope='module')
def collection_name() -> str:
    return gen_random_name(10)

@pytest.fixture(scope='module')
def collection_spec() -> lc.CollectionInSpec:
    spec = gen_random_fp_collection_spec(COLL_DIM)
    yield spec

@pytest.fixture(scope='module')
def collection(client: lc.LectricClient, collection_spec: lc.CollectionInSpec) -> lc.Collection:
    coll: lc.Collection = create_collection(client, collection_spec)

    yield coll
    del_collection_if_exists(coll.name, client)


def test_ingest(client: lc.LectricClient, collection: lc.Collection):

    num_elements = 200
    vecs: List[List[float]] = gen_random_fp_vectors(COLL_DIM, num_elements)

    input_data: lc.InputData = lc.InputData(
        collection_name=collection.name,
        data=[vecs]
    )

    # Test the collection is empty
    assert client.is_collection_empty(collection.name)

    # Ingest
    client.ingest(input_data)

    # Get the collection and test it's not empty
    assert not client.is_collection_empty(collection.name)


@pytest.mark.parametrize("pk_dtype",
            [
                lc.DataType.INT64,
                lc.DataType.VARCHAR
            ]
            )
def test_delete_collection_entity(client: lc.LectricClient, pk_dtype: lc.DataType):
    coll_dim = 8
    num_entities = 5
    num_del_entities = 2

    coll: lc.Collection = None

    # NOTE: Consistency level at Strong is necessary for deletion
    spec: lc.CollectionInSpec = gen_random_fp_collection_spec(coll_dim=coll_dim,
                            random_field=False, auto_id=False, consistency_level="Strong",
                            pk_type=pk_dtype)
    try:
        ids = []
        coll = client.create_collection(spec)

        assert client.is_collection_empty(coll.name)

        if pk_dtype == lc.DataType.INT64:
            ids = list(range(num_entities))

        elif pk_dtype == lc.DataType.VARCHAR:
            # NOTE: If you use IDs that can be cast to an int they might be turned into ints within the vdb
            ids = [ gen_random_name(4) for _ in  range(num_entities) ]

        input_data = lc.InputData(
            collection_name=coll.name,
            data=[ids, gen_random_fp_vectors(coll_dim, num_entities)]
        )

        assert input_data
        client.ingest(input_data)

        assert client.sizeof(coll.name) == num_entities

        client.hard_delete_entities(coll.name, ids=ids[:num_del_entities])
        # assert client.sizeof(coll.name) == (num_entities-num_del_entities) # FIXME
    finally:
        if coll:
            client.hard_drop_collection(coll.name)

