import pytest
from bert_server_client.client import BertClient
from bert_server_client.schema.embedding import EmbeddingRequest, Embedding


@pytest.fixture
def bert_client():
    host = "tcp://localhost:5555"
    client = BertClient(host)
    yield client
    client.close()


def test_request_to_bert_server(bert_client):
    request = EmbeddingRequest(input="test", model="test_model")
    response = bert_client.send_request(request)

    assert response is not None
    assert isinstance(response, Embedding)
