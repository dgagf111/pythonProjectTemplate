import json
from datetime import datetime, timedelta
import uuid
import pytz

# 使用 pytz.UTC 替代 datetime.UTC
UTC = pytz.UTC

class Message:
    def __init__(self, topic, content, ttl=None):
        self.id = str(uuid.uuid4())  # 生成唯一ID
        self.topic = topic
        self.content = content
        self.expiration = datetime.now(UTC) + timedelta(seconds=ttl) if ttl else None

    def to_json(self):
        return json.dumps({
            'id': self.id,
            'topic': self.topic,
            'content': self.content,
            'expiration': self.expiration.isoformat() if self.expiration else None
        })

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        msg = cls(data.get('topic', ''), data.get('content', ''))
        msg.id = data.get('id', str(uuid.uuid4()))
        if 'expiration' in data and data['expiration']:
            try:
                msg.expiration = datetime.fromisoformat(data['expiration'])
            except ValueError:
                # logger.warning(f"Invalid expiration format: {data['expiration']}")
                msg.expiration = None
        else:
            msg.expiration = None
        return msg

    def is_expired(self):
        return self.expiration is not None and datetime.now(UTC) > self.expiration
