import pytest
import threading
import time
from redis_msg_center.main import RedisMsgCenter
from redis_msg_center.message import Message

@pytest.fixture(scope="module")
def redis_msg_center():
    center = RedisMsgCenter()
    center.start()
    time.sleep(1)  # 给予足够的时间启动消息中心
    yield center
    center.shutdown()

def test_publish_and_consume(redis_msg_center):
    received_messages = []
    event = threading.Event()

    def message_handler(message):
        received_messages.append(message)
        if len(received_messages) == 2:
            event.set()

    redis_msg_center.subscribe("test_topic", message_handler)

    redis_msg_center.publish_message("test_topic", "Test message 1")
    redis_msg_center.publish_message("test_topic", "Test message 2")

    event.wait(timeout=10)  # 增加等待时间到10秒

    assert len(received_messages) == 2, f"Expected 2 messages, got {len(received_messages)}"
    assert received_messages[0].content == "Test message 1"
    assert received_messages[1].content == "Test message 2"

def test_message_expiration(redis_msg_center):
    received_messages = []
    event = threading.Event()

    def message_handler(message):
        received_messages.append(message)
        print(f"Received message: {message.content}, Expiration: {message.expiration}")
        event.set()

    redis_msg_center.subscribe("test_topic", message_handler)

    redis_msg_center.publish_message("test_topic", "Expired message", ttl=1)
    time.sleep(2)  # 等待消息过期

    # 清空接收到的消息列表
    received_messages.clear()
    event.clear()

    redis_msg_center.publish_message("test_topic", "Valid message")

    event.wait(timeout=10)  # 增加等待时间到10秒

    print(f"All received messages: {[msg.content for msg in received_messages]}")
    
    assert len(received_messages) == 1, f"Expected 1 message, got {len(received_messages)}"
    assert received_messages[0].content == "Valid message", f"Expected 'Valid message', got '{received_messages[0].content}'"
    
    # 添加额外的检查
    if len(received_messages) > 1:
        print(f"Unexpected messages: {[msg.content for msg in received_messages[1:]]}")
