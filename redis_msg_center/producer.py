import json
from log.logHelper import get_logger
from .message import Message  # 添加这行来导入 Message 类

logger = get_logger()

class MessageProducer:
    def __init__(self, config):
        self.redis_client = config.redis_client
        self.queue_key = config.queue_key

    def publish_message(self, topic, content, ttl=3600):
        try:
            message = Message(topic, content, ttl)
            self._publish(message)
        except Exception as e:
            logger.error(f"发布消息时出错: {str(e)}")
            raise

    def publish_permanent_message(self, topic, content):
        try:
            message = Message(topic, content, ttl=None)
            self._publish(message)
        except Exception as e:
            logger.error(f"发布永久消息时出错: {str(e)}")
            raise

    def _publish(self, message):
        self.redis_client.rpush(self.queue_key, message.to_json())
        # 移除日志输出
