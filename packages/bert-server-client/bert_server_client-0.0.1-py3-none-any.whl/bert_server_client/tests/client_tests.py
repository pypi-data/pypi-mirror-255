import pytest
from unittest.mock import MagicMock, patch
from bert_server_client.client import BertClient
from bert_server_client.schema.embedding import EmbeddingRequest, Embedding


@pytest.fixture
def bert_client():
    with patch('bert_server_client.client.zmq.Context'):
        yield BertClient("tcp://localhost:5555")


def test_initialization(bert_client):
    assert bert_client.host == "tcp://localhost:5555"
    assert bert_client.context is not None
    assert bert_client.socket is not None


def test_destructor(bert_client):
    with patch.object(bert_client, 'close') as mock_close:
        del bert_client
        mock_close.assert_called_once()


def test_initialize_client(bert_client):
    bert_client.initialize_client()
    assert bert_client.context is not None
    assert bert_client.socket is not None


def test_close(bert_client):
    bert_client.close()
    bert_client.socket.close.assert_called_once()
    bert_client.context.term.assert_called_once()


def test_send_request_valid_input(bert_client):
    bert_client.socket = MagicMock()
    bert_client.socket.recv.return_value = b"packed_response"

    with patch('bert_server_client.client.msgpack.packb') as mock_pack, \
            patch('bert_server_client.client.msgpack.unpackb') as mock_unpack, \
            patch('bert_server_client.client.from_dict') as mock_from_dict:
        mock_unpack.return_value = {}
        mock_from_dict.return_value = Embedding

        request = EmbeddingRequest(input="test", model="test-model")
        response = bert_client.send_request(request)

        assert response is not None
        mock_pack.assert_called_once_with({'input': 'test', 'model': 'test-model'})
        bert_client.socket.send.assert_called_once()
        bert_client.socket.recv.assert_called_once()


def test_send_request_invalid_input(bert_client):
    with pytest.raises(ValueError):
        bert_client.send_request("not an EmbeddingRequest")


def test_send_request_exception(bert_client):
    bert_client.socket.send = MagicMock(side_effect=Exception("test error"))

    with patch('bert_server_client.client.msgpack.packb') as mock_pack, \
            patch('bert_server_client.client.BertClient.initialize_client') as mock_initialize:
        request = EmbeddingRequest(input="test", model='test-model')

        with pytest.raises(Exception) as excinfo:
            bert_client.send_request(request)

        assert "test error" in str(excinfo.value)

        mock_pack.assert_called_once_with({'input': 'test', 'model': 'test-model'})
        bert_client.socket.send.assert_called_once()
        mock_initialize.assert_called_once()
