import pytest
import lectric as lc
from typing import List
import os
from .utils import (
    del_collection_if_exists,
)
import urllib
PRIMARY_FIELD_NAME = "id"
FOREIGN_ID_FIELD_NAME = "fk"
LINK_FIELD_NAME = "link"
METADATA_FIELD_NAME = "metadata"
IS_FILE_UPLOAD_FIELD_NAME = "is_file_upload"
IS_MARKED_FOR_DELETION = "is_marked_for_deletion"
INGESTOR = "ingestor"
SOFT_DELETER = "soft_deleter"
TEST_COLLECTION_NAME = 'test'
USERNAME = 'dummy@dummy.com'

TEST_IMAGE_URI = 'https://picsum.photos/seed/picsum/200/300'
HASH_ALGO= 'md5'
TEST_METADATA = {'traits': 'Artistic Imagery'}
SOFT_DELETED_ENTRIES_SIZE = 'Soft-deleted entries size'

@pytest.fixture(scope='function')
def collection(client: lc.LectricClient) -> lc.Collection:
    fields: List[lc.FieldSchema] = [lc.FieldSchema(PRIMARY_FIELD_NAME, lc.DataType.VARCHAR,
                                                                                max_length=128, is_primary=True)]
    fields.append(lc.FieldSchema(name=LINK_FIELD_NAME, dtype=lc.DataType.STRING, description="link field"))
    fields.append(lc.FieldSchema(name=METADATA_FIELD_NAME, dtype=lc.DataType.JSON, description="JSONB metadata"))
    fields.append(lc.FieldSchema(name=IS_FILE_UPLOAD_FIELD_NAME, dtype=lc.DataType.BOOL, description="Is File Upload"))
    fields.append(lc.FieldSchema(name=IS_MARKED_FOR_DELETION, dtype=lc.DataType.BOOL, description="Is marked for deletion"))
    fields.append(lc.FieldSchema(name=INGESTOR, dtype=lc.DataType.STRING, description="MSFT alias of the ingestor"))
    fields.append(lc.FieldSchema(name=SOFT_DELETER, dtype=lc.DataType.STRING, description="MSFT alias of the user who moved an entry to the trash can"))
    enable_dupe_counter: bool = False
    collection = client.create_collection(lc.CollectionInSpec(name=TEST_COLLECTION_NAME, approx=False,
                                            coll_schema=lc.CollectionSchema(fields=fields)),
                                            with_dupe_counter=enable_dupe_counter,
                                            hash_algo=lc.HashAlgo[HASH_ALGO])
    yield collection

    del_collection_if_exists(collection.name, client, exact=True)

@pytest.fixture(scope='function')
def exact_entry_id(collection: lc.Collection, client: lc.LectricClient) -> str:
    entry_id = client.put_exact(collection_name=collection.name,
                    uri=TEST_IMAGE_URI,
                    metadata=TEST_METADATA,
                    upsert=True,
                    store_raw_data=True,
                    ingestor=USERNAME)
    yield entry_id

    client.hard_delete_entities(collection_name=collection.name, ids=[entry_id], is_approx=False)

def test_ingest(client: lc.LectricClient, exact_entry_id: str, collection: lc.Collection):
    lookup_result = client.lookup_exact(collection.name, uri=TEST_IMAGE_URI)

    assert lookup_result[METADATA_FIELD_NAME] == TEST_METADATA
    assert lookup_result[PRIMARY_FIELD_NAME] == exact_entry_id
    assert lookup_result[INGESTOR] == USERNAME

# check the collection info after doing soft_delete
def test_soft_delete(client: lc.LectricClient, exact_entry_id: str, collection: lc.Collection):
    client.soft_delete_entities(collection_name=collection.name, ids=[exact_entry_id], is_approx=False, deleter=USERNAME)
    collection_info_str = client.info(collection_name=collection.name, exact=True)
    collection_info_dict = convert_info_str_to_dict(collection_info_str=collection_info_str)

    assert int(collection_info_dict[SOFT_DELETED_ENTRIES_SIZE]) == 1

    lookup_result = client.lookup_exact(collection.name, uri=TEST_IMAGE_URI)
    assert lookup_result[IS_MARKED_FOR_DELETION] == True
    assert lookup_result[INGESTOR] == USERNAME
    assert lookup_result[SOFT_DELETER] == USERNAME

def test_soft_delete_then_recover(client: lc.LectricClient, exact_entry_id: str, collection: lc.Collection):
    lookup_result = client.lookup_exact(collection.name, uri=TEST_IMAGE_URI)
    assert lookup_result[PRIMARY_FIELD_NAME] == exact_entry_id
    assert lookup_result[INGESTOR] == USERNAME

    client.soft_delete_entities(collection_name=collection.name, ids=[exact_entry_id], is_approx=False, deleter=USERNAME)
    lookup_result = client.lookup_exact(collection.name, uri=TEST_IMAGE_URI)
    collection_info_str = client.info(collection_name=collection.name, exact=True)
    collection_info_dict = convert_info_str_to_dict(collection_info_str=collection_info_str)

    assert int(collection_info_dict[SOFT_DELETED_ENTRIES_SIZE]) == 1
    assert lookup_result[IS_MARKED_FOR_DELETION] == True
    assert lookup_result[SOFT_DELETER] == USERNAME
    assert lookup_result[INGESTOR] == USERNAME

    client.recover_entries(collection_name=collection.name, ids=[exact_entry_id], is_approx=False)
    lookup_result = client.lookup_exact(collection.name, uri=TEST_IMAGE_URI)
    collection_info_str = client.info(collection_name=collection.name, exact=True)
    collection_info_dict = convert_info_str_to_dict(collection_info_str=collection_info_str)
    assert int(collection_info_dict[SOFT_DELETED_ENTRIES_SIZE]) == 0
    assert lookup_result[IS_MARKED_FOR_DELETION] == False
    assert lookup_result[SOFT_DELETER] is None
    assert lookup_result[INGESTOR] == USERNAME

def convert_info_str_to_dict(collection_info_str: str) -> dict:
    collection_info_dict = {}
    for item in collection_info_str:
        # Split each item into key and value
        key, value = item.split(': ', 1)
        # Remove any leading or trailing whitespace from the value
        value = value.strip()
        # Add the key-value pair to the dictionary
        collection_info_dict[key] = value
    return collection_info_dict
