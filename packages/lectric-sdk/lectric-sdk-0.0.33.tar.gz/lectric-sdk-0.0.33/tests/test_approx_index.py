from typing import List
import pytest
from .utils import (
    del_collection_if_exists,
    gen_random_fp_collection_spec,
    gen_random_name,
    gen_random_fp_vectors,
    create_collection)
import lectric as lc

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

def test_index(client: lc.LectricClient, collection: lc.Collection):

    assert client.is_collection_empty(collection.name)

    num_elements = 200
    vecs: List[List[float]] = gen_random_fp_vectors(COLL_DIM, num_elements)

    input_data: lc.InputData = lc.InputData(
        collection_name=collection.name,
        data=[vecs]
    )

    client.ingest(input_data)
    # Get the collection and test it's not empty
    assert not client.is_collection_empty(collection.name)

    vec_field: str = "vecs"

    index_spec: lc.IndexInSpec = lc.IndexInSpec(
        collection_name=collection.name,
        field_name=vec_field,
        index=lc.Index(index_type=lc.IndexType.IVF_FLAT,
                    metric_type=lc.VectorSpace.L2)
    )

    # Test create index
    client.create_index(index_spec)


    # Test get indexes defined for a collection
    indexes: List[str] = client.get_indexes(collection.name)

    assert len(indexes) == 1
    assert indexes[0] == index_spec.field_name


    # Query index ...
    k = 5

    res: lc.QueryResponse = client.query(lc.VectorQuerySpec(
        data=vecs[:2],
        collection_name=collection.name,
        search_field=vec_field,
        search_params=lc.QueryParams(metric_type=lc.VectorSpace.L2,
                                params=lc.QueryMetaParams(
                                nprobe=2
                            )),
        output_fields=[],
        limit=k)

        )
    assert len(res.hits) == 2
    assert len(res.hits[0]) == k

    # Test deleting the index
    client.drop_index(collection.name, index_spec.field_name)

    # Test deletion is successful
    assert len(client.get_indexes(collection.name)) == 0
