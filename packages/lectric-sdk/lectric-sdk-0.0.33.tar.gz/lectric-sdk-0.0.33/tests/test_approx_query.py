import pytest
import random
from typing import Dict, List
from .utils import (
    del_collection_if_exists,
    gen_random_fp_collection_spec,
    gen_random_name,
    create_collection, gen_random_fp_vectors)
import lectric as lc

DIM = 8
NUM_ELEMS = 20

METRIC_TYPE = lc.VectorSpace.L2

@pytest.fixture(scope="module")
def collection(client: lc.LectricClient) -> lc.Collection:
    coll: lc.Collection = create_collection(client, gen_random_fp_collection_spec(8, random_field=True))

    # Ingest some data
    input_data = lc.InputData(
        collection_name=coll.name,
        data=[gen_random_fp_vectors(DIM, NUM_ELEMS),
                [float(random.randrange(-20, -10)) for _ in range(NUM_ELEMS)]
            ]
    )

    client.ingest(input_data)
    client.create_index(lc.IndexInSpec(
        coll.name, "vecs", index=lc.Index(
            lc.IndexType.IVF_FLAT, metric_type=METRIC_TYPE
        )
    ))

    yield coll

    del_collection_if_exists(coll.name, client)

def test_query_vectors(client: lc.LectricClient, collection: lc.Collection):
    K = 10
    spec: lc.VectorQuerySpec = lc.VectorQuerySpec(
        data=gen_random_fp_vectors(DIM, 2),
        collection_name=collection.name,
        search_field="vecs",
        search_params=lc.QueryParams(metric_type=METRIC_TYPE,
                                params=lc.QueryMetaParams(
                                nprobe=5
                            )),
        output_fields=["id", "random"], # NOTE: You cannot get vector field back as output_field
        limit=K
        )

    qres: lc.QueryResponse = client.query(spec)
    assert len(qres.hits) == 2

    for hit in qres.hits:
        assert len(hit) == K

    # Assert our output fields are there
    assert "id" in qres.hits[0][0].result
    assert "random" in qres.hits[0][0].result

def test_query_fields(client: lc.LectricClient, collection: lc.Collection):
    spec: lc.QuerySpec = lc.QuerySpec(
        expr="random > -14",
        collection_name=collection.name,
        output_fields=["random", "vecs"]
    )

    qres = client.query(spec)

    assert "id" in qres[0] # ID will always be in the response
    assert "vecs" in qres[0]
    assert "random" in qres[0]
    assert len(qres[0]["vecs"]) == DIM


def test_varchar_field(client: lc.LectricClient):
    coll_dim = 8

    fields: List[lc.FieldSchema] = [
        lc.FieldSchema(name="id", dtype=lc.DataType.INT64, is_primary=True,
            auto_id=True, description="Primary key"),
        lc.FieldSchema(name="vecs", dtype=lc.DataType.FLOAT_VECTOR,
                        dim=coll_dim, description="floating point embeddings"),
        lc.FieldSchema(name="foreign_id", dtype=lc.DataType.VARCHAR, max_length=10,
                       description="foreign ID key", is_primary=False),
    ]

    schema: lc.CollectionSchema = lc.CollectionSchema(fields=fields, description="Test collection schema")

    collection: lc.Collection = None
    try:
        collection = client.create_collection(lc.CollectionInSpec(name=gen_random_name(10), coll_schema=schema))

        # Ingest
        vecs: List[List[float]] = gen_random_fp_vectors(coll_dim, 3)
        fids: List[str] = [gen_random_name(6) for i in range(len(vecs))]

        data = [vecs, fids]
        client.ingest(lc.InputData(collection_name=collection.name, data=data))

        # FIXME: Add index
        client.create_index(lc.IndexInSpec(
            collection.name, "vecs", index=lc.Index(
                lc.IndexType.IVF_FLAT, metric_type=METRIC_TYPE
            )
        ))

        # Query for string prop back (emulate foreign key lookup)
        for fid in fids:
            qres: List[Dict] = client.query(lc.QuerySpec(collection_name=collection.name,
                    expr=f"foreign_id == \"{fid}\"", output_fields=["foreign_id", "vecs"]))

            assert qres[0]["foreign_id"] == fid

    finally:
        if collection:
            del_collection_if_exists(collection_name=collection.name, client=client)
