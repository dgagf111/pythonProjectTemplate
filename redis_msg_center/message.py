import json
from datetime import datetime, timedelta, UTC

class Message:
    def __init__(self, topic, content, ttl=None):  # 修改默认值为 None
        self.topic = topic
        self.content = content
        self.expiration = (datetime.now(UTC) + timedelta(seconds=ttl)).isoformat() if ttl else None

    def to_json(self):
        return json.dumps({
            'topic': self.topic,
            'content': self.content,
            'expiration': self.expiration
        })

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        msg = cls(data['topic'], data['content'])
        msg.expiration = data['expiration']
        return msg

    def is_expired(self):
        if self.expiration is None:
            return False
        expiration_time = datetime.fromisoformat(self.expiration)
        return datetime.now(UTC) > expiration_time
