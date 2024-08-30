import pytest
from redis_msg_center.message import Message
from datetime import datetime, timedelta, UTC

def test_message_creation():
    message = Message("test_topic", "test_content", ttl=3600)
    assert message.topic == "test_topic"
    assert message.content == "test_content"
    assert message.expiration is not None

def test_message_to_json():
    message = Message("test_topic", "test_content", ttl=3600)
    json_str = message.to_json()
    assert "test_topic" in json_str
    assert "test_content" in json_str
    assert "expiration" in json_str

def test_message_from_json():
    json_str = '{"id": "test-id", "topic": "test_topic", "content": "test_content", "expiration": "2023-08-30T10:00:00+00:00"}'
    message = Message.from_json(json_str)
    assert message.id == "test-id"
    assert message.topic == "test_topic"
    assert message.content == "test_content"
    assert message.expiration == datetime(2023, 8, 30, 10, 0, tzinfo=UTC)

def test_message_is_expired():
    expired_message = Message("test_topic", "test_content", ttl=-1)
    assert expired_message.is_expired()

    future_message = Message("test_topic", "test_content", ttl=3600)
    assert not future_message.is_expired()

    permanent_message = Message("test_topic", "test_content", ttl=None)
    assert not permanent_message.is_expired()
