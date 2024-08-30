import pytest
from redis_msg_center.consumer import MessageConsumer
from redis_msg_center.message_config import MessageConfig
from redis_msg_center.message import Message
from unittest.mock import Mock, patch

@pytest.fixture
def mock_redis_client():
    return Mock()

@pytest.fixture
def mock_config(mock_redis_client):
    config = MessageConfig()
    config.redis_client = mock_redis_client
    config.queue_key = 'test_queue'
    return config

def test_consume_message(mock_config):
    mock_redis_msg_center = Mock()
    consumer = MessageConsumer(mock_config, mock_redis_msg_center)
    mock_config.redis_client.blpop.return_value = ('test_queue', b'{"id": "test-id", "topic": "test", "content": "Test message", "expiration": null}')
    
    message = consumer.consume_message()
    
    assert message is not None
    assert message.id == "test-id"
    assert message.topic == "test"
    assert message.content == "Test message"
    mock_config.redis_client.blpop.assert_called_once_with('test_queue', timeout=1)

@patch('redis_msg_center.consumer.logger')
def test_handle_message(mock_logger, mock_config):
    mock_redis_msg_center = Mock()
    consumer = MessageConsumer(mock_config, mock_redis_msg_center)
    message = Message("test_topic", "Test message content")
    
    consumer.handle_message(message)
    
    mock_redis_msg_center.handle_message.assert_called_once_with(message)
