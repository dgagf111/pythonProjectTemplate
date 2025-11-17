from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from typing import Dict, Optional, Protocol

from redis import Redis
from redis.exceptions import RedisError

from pythonprojecttemplate.config.settings import settings
from pythonprojecttemplate.log.logHelper import get_logger

logger = get_logger()


@dataclass
class TokenRecord:
    username: str
    access_token: str
    refresh_token: str
    access_expires_at: datetime
    refresh_expires_at: datetime
    issued_at: datetime

    def to_dict(self) -> Dict[str, str]:
        payload = asdict(self)
        payload["access_expires_at"] = self.access_expires_at.isoformat()
        payload["refresh_expires_at"] = self.refresh_expires_at.isoformat()
        payload["issued_at"] = self.issued_at.isoformat()
        return payload

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "TokenRecord":
        return cls(
            username=data["username"],
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            access_expires_at=datetime.fromisoformat(data["access_expires_at"]),
            refresh_expires_at=datetime.fromisoformat(data["refresh_expires_at"]),
            issued_at=datetime.fromisoformat(data["issued_at"]),
        )


class TokenStore(Protocol):
    def save(self, username: str, record: TokenRecord, ttl_seconds: int) -> None: ...

    def read(self, username: str) -> Optional[TokenRecord]: ...

    def delete(self, username: str) -> None: ...

    def mark_revoked(self, token_hash: str, ttl_seconds: int) -> None: ...

    def is_revoked(self, token_hash: str) -> bool: ...


class RedisTokenStore:
    def __init__(self, client: Redis | None = None) -> None:
        cfg = settings.security.revocation
        redis_cfg = cfg.redis
        self._client = client or Redis(
            host=redis_cfg.host,
            port=redis_cfg.port,
            db=redis_cfg.db,
            username=redis_cfg.username or None,
            password=redis_cfg.password or None,
            ssl=redis_cfg.ssl,
            decode_responses=True,
        )
        self._client.ping()
        self._prefix = cfg.key_prefix
        self._default_ttl = cfg.default_ttl_seconds

    def _user_key(self, username: str) -> str:
        return f"{self._prefix}:active:{username}"

    def _revoked_key(self, token_hash: str) -> str:
        return f"{self._prefix}:revoked:{token_hash}"

    def save(self, username: str, record: TokenRecord, ttl_seconds: int) -> None:
        ttl = ttl_seconds if ttl_seconds > 0 else self._default_ttl
        ttl = max(ttl, 1)
        payload = json.dumps(record.to_dict())
        self._client.setex(self._user_key(username), ttl, payload)

    def read(self, username: str) -> Optional[TokenRecord]:
        raw = self._client.get(self._user_key(username))
        if not raw:
            return None
        return TokenRecord.from_dict(json.loads(raw))

    def delete(self, username: str) -> None:
        self._client.delete(self._user_key(username))

    def mark_revoked(self, token_hash: str, ttl_seconds: int) -> None:
        ttl = ttl_seconds if ttl_seconds > 0 else self._default_ttl
        ttl = max(ttl, 1)
        self._client.setex(self._revoked_key(token_hash), ttl, "1")

    def is_revoked(self, token_hash: str) -> bool:
        return bool(self._client.exists(self._revoked_key(token_hash)))


class InMemoryTokenStore:
    def __init__(self) -> None:
        self._records: Dict[str, tuple[TokenRecord, datetime]] = {}
        self._revoked: Dict[str, datetime] = {}

    def save(self, username: str, record: TokenRecord, ttl_seconds: int) -> None:
        expires_at = datetime.now(UTC) + timedelta(seconds=max(ttl_seconds, 1))
        self._records[username] = (record, expires_at)

    def read(self, username: str) -> Optional[TokenRecord]:
        item = self._records.get(username)
        if not item:
            return None
        record, expires_at = item
        if expires_at < datetime.now(UTC):
            self.delete(username)
            return None
        return record

    def delete(self, username: str) -> None:
        self._records.pop(username, None)

    def mark_revoked(self, token_hash: str, ttl_seconds: int) -> None:
        self._revoked[token_hash] = datetime.now(UTC) + timedelta(seconds=max(ttl_seconds, 1))

    def is_revoked(self, token_hash: str) -> bool:
        expiry = self._revoked.get(token_hash)
        if not expiry:
            return False
        if expiry < datetime.now(UTC):
            self._revoked.pop(token_hash, None)
            return False
        return True


class TokenRegistry:
    def __init__(self, store: TokenStore | None = None):
        self.store = store or self._build_store()

    def _build_store(self) -> TokenStore:
        cfg = settings.security.revocation
        if cfg.backend == "redis":
            try:
                logger.info("Initializing Redis token store for revocation tracking")
                return RedisTokenStore()
            except RedisError as exc:
                logger.warning("Redis token store unavailable (%s); falling back to in-memory store", exc)
        return InMemoryTokenStore()

    def persist(self, record: TokenRecord) -> TokenRecord:
        ttl_seconds = max(int((record.refresh_expires_at - datetime.now(UTC)).total_seconds()), 1)
        self.store.save(record.username, record, ttl_seconds)
        return record

    def read(self, username: str) -> Optional[TokenRecord]:
        return self.store.read(username)

    def delete(self, username: str) -> None:
        self.store.delete(username)

    def mark_revoked_token(self, token: str, expires_at: datetime) -> None:
        ttl_seconds = max(int((expires_at - datetime.now(UTC)).total_seconds()), 1)
        self.store.mark_revoked(self._hash_token(token), ttl_seconds)

    def is_token_revoked(self, token: str) -> bool:
        return self.store.is_revoked(self._hash_token(token))

    def revoke_user(self, username: str) -> None:
        record = self.read(username)
        if not record:
            return
        self.mark_revoked_token(record.access_token, record.access_expires_at)
        self.mark_revoked_token(record.refresh_token, record.refresh_expires_at)
        self.delete(username)

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()


class TokenAuditLogger:
    def __init__(self):
        self._settings = settings.security.audit

    def log(self, action: str, username: str, **context: object) -> None:
        if not self._settings.enabled:
            return
        safe_username = username if self._settings.include_username else "***"
        flattened = ", ".join(f"{key}={value}" for key, value in context.items() if value is not None)
        suffix = f" {flattened}" if flattened else ""
        logger.info("token.%s user=%s%s", action, safe_username, suffix)


token_registry = TokenRegistry()
token_audit_logger = TokenAuditLogger()
