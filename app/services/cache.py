import hashlib
import threading
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from app.config.logger import logger
from app.config.settings import settings


class CacheInterface(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: str) -> None:
        raise NotImplementedError


class SimpleMemoryCache(CacheInterface):
    def __init__(self, ttl_seconds: int = settings.cache_ttl_seconds) -> None:
        self.ttl_seconds = ttl_seconds
        self._store: Dict[str, tuple[Any, float]] = {}
        self._lock = threading.Lock()

    def _now(self) -> float:
        return time.time()

    def _cleanup(self) -> None:
        expired = [key for key, (_, expires) in self._store.items() if expires <= self._now()]
        for key in expired:
            self._store.pop(key, None)
            logger.debug(f"Cache expired key={key}")

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            self._cleanup()
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires = entry
            if expires <= self._now():
                self._store.pop(key, None)
                return None
            logger.debug(f"Cache hit key={key}")
            return value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            expires = self._now() + self.ttl_seconds
            self._store[key] = (value, expires)
            logger.debug(f"Cached key={key} ttl={self.ttl_seconds}")

    def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)
            logger.debug(f"Cache deleted key={key}")


def build_cache_key(*parts: str) -> str:
    normalized = "||".join(part.strip().lower() for part in parts)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
