import pytest
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from redis_msg_center.main import RedisMsgCenter
from redis_msg_center.message import Message

@pytest.fixture(scope="module")
def redis_msg_center():
    center = RedisMsgCenter()
    center.start()
    time.sleep(1)  # 给予足够的时间启动消息中心
    yield center
    center.shutdown()

def test_multiple_producers(redis_msg_center):
    received_messages = []
    event = threading.Event()

    def message_handler(message):
        received_messages.append(message)
        if len(received_messages) == 1000:
            event.set()

    redis_msg_center.subscribe("test_topic", message_handler)

    def produce_messages(producer_id):
        for i in range(200):
            redis_msg_center.publish_message("test_topic", f"Message from producer {producer_id}: {i}")

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(produce_messages, i) for i in range(5)]
        for future in as_completed(futures):
            future.result()

    event.wait(timeout=30)
    assert len(received_messages) == 1000, f"Expected 1000 messages, got {len(received_messages)}"

def test_multiple_consumers(redis_msg_center):
    received_messages = [set() for _ in range(5)]
    consumer_counts = [0] * 5
    event = threading.Event()

    def message_handler(consumer_id):
        def handler(message):
            received_messages[consumer_id].add(message.content)
            consumer_counts[consumer_id] += 1
            if sum(len(msgs) for msgs in received_messages) == 5000:
                event.set()
        return handler

    for i in range(5):
        redis_msg_center.subscribe("test_topic", message_handler(i))

    for i in range(1000):
        redis_msg_center.publish_message("test_topic", f"Message {i}")

    event.wait(timeout=60)  # 增加等待时间

    total_unique_messages = set().union(*received_messages)
    assert len(total_unique_messages) == 1000, f"Expected 1000 unique messages, got {len(total_unique_messages)}"
    print(f"Consumer message counts: {consumer_counts}")
    assert sum(consumer_counts) == 5000, f"Total processed messages should be 5000, got {sum(consumer_counts)}"

def test_producer_consumer_high_load(redis_msg_center):
    received_messages = []
    event = threading.Event()

    def message_handler(message):
        received_messages.append(message)
        if len(received_messages) == 10000:
            event.set()

    redis_msg_center.subscribe("test_topic", message_handler)

    def produce_messages():
        for i in range(2000):
            redis_msg_center.publish_message("test_topic", f"Message {i}")

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(produce_messages) for _ in range(5)]
        for future in as_completed(futures):
            future.result()

    event.wait(timeout=60)
    assert len(received_messages) == 10000, f"Expected 10000 messages, got {len(received_messages)}"

def test_message_order(redis_msg_center):
    received_messages = []
    event = threading.Event()

    def message_handler(message):
        received_messages.append(message)
        if len(received_messages) == 1000:
            event.set()

    redis_msg_center.subscribe("test_topic", message_handler)

    for i in range(1000):
        redis_msg_center.publish_message("test_topic", f"Message {i}")

    event.wait(timeout=30)
    assert len(received_messages) == 1000, f"Expected 1000 messages, got {len(received_messages)}"
    
    for i, message in enumerate(received_messages):
        assert message.content == f"Message {i}", f"Expected 'Message {i}', got '{message.content}'"

def test_error_recovery(redis_msg_center):
    received_messages = []
    event = threading.Event()

    def message_handler(message):
        received_messages.append(message)
        if len(received_messages) == 1000:
            event.set()
        if random.random() < 0.1:  # 10% 的概率抛出异常
            raise Exception("Random error")

    redis_msg_center.subscribe("test_topic", message_handler)

    for i in range(1000):
        redis_msg_center.publish_message("test_topic", f"Message {i}")

    event.wait(timeout=30)
    assert len(received_messages) == 1000, f"Expected 1000 messages, got {len(received_messages)}"

def test_multiple_producers_and_consumers(redis_msg_center):
    topics = ["topic1", "topic2", "topic3"]
    messages_per_topic = 1000
    total_messages = len(topics) * messages_per_topic
    received_messages = {topic: [] for topic in topics}
    events = {topic: threading.Event() for topic in topics}

    def message_handler(topic):
        def handler(message):
            received_messages[topic].append(message.content)
            if len(received_messages[topic]) == messages_per_topic:
                events[topic].set()
        return handler

    for topic in topics:
        redis_msg_center.subscribe(topic, message_handler(topic))

    def produce_messages(topic):
        for i in range(messages_per_topic):
            redis_msg_center.publish_message(topic, f"Message {i} for {topic}")

    with ThreadPoolExecutor(max_workers=len(topics)) as executor:
        futures = [executor.submit(produce_messages, topic) for topic in topics]
        for future in as_completed(futures):
            future.result()

    for event in events.values():
        event.wait(timeout=60)

    for topic in topics:
        assert len(received_messages[topic]) == messages_per_topic, f"Expected {messages_per_topic} messages for {topic}, got {len(received_messages[topic])}"
        assert all(msg.startswith(f"Message ") and msg.endswith(f"for {topic}") for msg in received_messages[topic]), f"Incorrect message format for {topic}"

    print(f"Total messages received: {sum(len(msgs) for msgs in received_messages.values())}")
    assert sum(len(msgs) for msgs in received_messages.values()) == total_messages, f"Total processed messages should be {total_messages}, got {sum(len(msgs) for msgs in received_messages.values())}"
