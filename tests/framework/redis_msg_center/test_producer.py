import pytest
from redis_msg_center.producer import MessageProducer
from redis_msg_center.message_config import MessageConfig
from unittest.mock import Mock

@pytest.fixture
def mock_redis_client():
    return Mock()

@pytest.fixture
def mock_config(mock_redis_client):
    config = MessageConfig()
    config.redis_client = mock_redis_client
    config.queue_key = 'test_queue'
    return config

def test_publish_message(mock_config):
    producer = MessageProducer(mock_config)
    producer.publish_message("test_topic", "test_content", ttl=3600)
    
    mock_config.redis_client.rpush.assert_called_once()
    args = mock_config.redis_client.rpush.call_args[0]
    assert args[0] == 'test_queue'
    assert 'test_topic' in args[1]
    assert 'test_content' in args[1]

def test_publish_permanent_message(mock_config):
    producer = MessageProducer(mock_config)
    producer.publish_permanent_message("test_topic", "test_content")
    
    mock_config.redis_client.rpush.assert_called_once()
    args = mock_config.redis_client.rpush.call_args[0]
    assert args[0] == 'test_queue'
    assert 'test_topic' in args[1]
    assert 'test_content' in args[1]
    assert '"expiration": null' in args[1]
