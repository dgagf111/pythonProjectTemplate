import threading
from log.logHelper import get_logger
from .producer import MessageProducer
from .consumer import MessageConsumer
from .message_config import MessageConfig
import random

logger = get_logger()

class RedisMsgCenter:
    def __init__(self):
        self.config = MessageConfig()
        self.producer = MessageProducer(self.config)
        self.consumer = MessageConsumer(self.config, self)
        self.subscribers = {}
        self.is_running = False

    def subscribe(self, topic, handler):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(handler)

    def start(self):
        if not self.is_running:
            logger.info("Redis消息中心启动中...")
            self.consumer_thread = threading.Thread(target=self.consumer.start_consuming)
            self.consumer_thread.daemon = True
            self.consumer_thread.start()
            self.is_running = True
            logger.info("Redis消息中心已启动")

    def shutdown(self):
        if self.is_running:
            logger.info("Redis消息中心正在关闭...")
            self.is_running = False
            if self.consumer_thread:
                self.consumer.stop_consuming()
                self.consumer_thread.join()
            logger.info("Redis消息中心已关闭")

    def publish_message(self, topic, content, ttl=3600):
        # logger.debug(f"Publishing message: Topic={topic}, Content={content}, TTL={ttl}")
        self.producer.publish_message(topic, content, ttl)

    def publish_permanent_message(self, topic, content):
        self.producer.publish_permanent_message(topic, content)

    def handle_message(self, message):
        error_count = 0
        for topic, handlers in self.subscribers.items():
            if topic == message.topic or (topic.endswith('*') and message.topic.startswith(topic[:-1])):
                for handler in handlers:
                    try:
                        handler(message)
                    except Exception as e:
                        error_count += 1
                        if error_count % 10 == 0:  # 每10次错误输出一次日志
                            logger.error(f"处理消息时出错 (已发生 {error_count} 次): {str(e)}")

redis_msg_center = RedisMsgCenter()

def start():
    redis_msg_center.start()

def shutdown():
    redis_msg_center.shutdown()

if __name__ == "__main__":
    import signal
    import sys

    def signal_handler(signum, frame):
        logger.info(f"接收到信号: {signal.Signals(signum).name}")
        shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    start()

    try:
        signal.pause()
    except KeyboardInterrupt:
        pass
    finally:
        shutdown()
