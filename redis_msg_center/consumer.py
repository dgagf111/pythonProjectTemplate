import json
import time
import threading
from log.logHelper import get_logger
from .message import Message
from concurrent.futures import ThreadPoolExecutor

logger = get_logger()

class MessageConsumer:
    def __init__(self, config, redis_msg_center, num_workers=5):
        self.config = config
        self.redis_client = config.redis_client
        self.queue_key = config.queue_key
        self.redis_msg_center = redis_msg_center
        self.stop_event = threading.Event()
        self.executor = ThreadPoolExecutor(max_workers=num_workers)
        self.consume_lock = threading.Lock()

    def consume_message(self):
        with self.consume_lock:
            try:
                message_data = self.redis_client.blpop(self.queue_key, timeout=1)
                if message_data and isinstance(message_data[1], bytes):
                    message = Message.from_json(message_data[1].decode('utf-8'))
                    if not message.is_expired():
                        # logger.debug(f"消费消息: {message.to_json()}")
                        return message
                    else:
                        # logger.warning(f"丢弃过期消息: {message.to_json()}")
                        return None
                return None
            except json.JSONDecodeError as e:
                logger.error(f"JSON 解码错误: {str(e)}")
                return None
            except Exception as e:
                logger.error(f"消费消息时出错: {str(e)}")
                return None

    def start_consuming(self):
        while not self.stop_event.is_set():
            messages = []
            for _ in range(10):  # 尝试一次性获取10条消息
                message = self.consume_message()
                if message:
                    messages.append(message)
                else:
                    break
            if messages:
                self.executor.submit(self.process_messages, messages)

    def process_messages(self, messages):
        for message in messages:
            self.redis_msg_center.handle_message(message)

    def handle_message(self, message):
        with threading.Lock():
            self.redis_msg_center.handle_message(message)

    def stop_consuming(self):
        self.stop_event.set()
        self.executor.shutdown(wait=True)
