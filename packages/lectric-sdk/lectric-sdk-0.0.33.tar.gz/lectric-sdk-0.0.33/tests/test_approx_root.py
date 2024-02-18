from lectric import LectricClient

def test_list_connections(client: LectricClient):
    connections = client.list_connections()
    assert len(connections)