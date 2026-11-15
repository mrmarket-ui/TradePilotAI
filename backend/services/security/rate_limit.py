"""
A small sliding-window rate limiter.

It lives in this server process's memory, which is right for a single server.
If TradePilot AI later runs on several servers, replace the storage with
Redis; the rest of the code does not need to change.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from typing import Callable


class SlidingWindowLimiter:
    def __init__(
        self,
        limit: int,
        window_seconds: int,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.limit = limit
        self.window = window_seconds
        self._clock = clock
        self._hits: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def _recent(self, key: str, now: float) -> deque[float]:
        hits = self._hits.setdefault(key, deque())

        while hits and now - hits[0] >= self.window:
            hits.popleft()

        return hits

    def _cleanup(self, now: float) -> None:
        if len(self._hits) < 5000:
            return

        for key in list(self._hits):
            if not self._recent(key, now):
                del self._hits[key]

    def count(self, key: str) -> int:
        with self._lock:
            return len(self._recent(key, self._clock()))

    def add(self, key: str) -> None:
        """Record one event without checking the limit (used to count failures)."""

        with self._lock:
            now = self._clock()
            self._recent(key, now).append(now)
            self._cleanup(now)

    def blocked(self, key: str) -> bool:
        return self.count(key) >= self.limit

    def allow(self, key: str) -> bool:
        """Record one event if the limit has not been reached. Returns whether it was allowed."""

        with self._lock:
            now = self._clock()
            hits = self._recent(key, now)

            if len(hits) >= self.limit:
                return False

            hits.append(now)
            self._cleanup(now)

            return True

    def retry_after(self, key: str) -> int:
        with self._lock:
            now = self._clock()
            hits = self._recent(key, now)

            if not hits:
                return 1

            return max(1, int(self.window - (now - hits[0])) + 1)

    def clear(self, key: str | None = None) -> None:
        with self._lock:
            if key is None:
                self._hits.clear()
            else:
                self._hits.pop(key, None)
