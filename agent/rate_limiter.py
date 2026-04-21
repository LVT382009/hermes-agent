"""
Client-side sliding-window rate limiter for Hermes Agent.

Paces outgoing API calls to stay within a configurable requests-per-minute
ceiling, preventing 429 errors before they occur.

Core classes:
- SlidingWindowRateLimiter: Exact windowed counting, no burst
- ProviderRateLimiterRegistry: Case-insensitive, prefix-aware provider routing
- make_registry(): Factory reads config + env var

Lock safety: time.sleep() always runs outside the lock.
Default: rpm=0 (disabled). Zero behaviour change for existing users.
No external dependencies — pure stdlib.
"""

import collections
import os
import threading
import time
from typing import Dict


class _NoOpLimiter:
    """Zero-cost NOOP limiter for disabled state."""
    rpm = 0

    def acquire(self) -> float:
        """Returns 0.0 instantly — no limiting."""
        return 0.0


_NOOP = _NoOpLimiter()


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter using exact windowed counting.

    Uses time.monotonic() for drift-free timing.
    Lock held only for window cleanup and slot claim operations.
    time.sleep() ALWAYS outside the lock (verified by test).
    """

    def __init__(self, rpm: int):
        self._rpm = rpm
        self._window = collections.deque()
        self._lock = threading.Lock()

    @property
    def rpm(self) -> int:
        """Current RPM setting."""
        return self._rpm

    def acquire(self) -> float:
        """
        Block until a request slot is available.

        Returns:
            Seconds waited (0.0 if no wait needed).

        Fail-safe: Returns 0.0 on any exception (degrade to no limiting).
        """
        if self._rpm == 0:
            return 0.0

        wait_start = time.monotonic()

        while True:
            try:
                with self._lock:
                    now = time.monotonic()

                    # Clean up expired timestamps
                    while self._window and now - self._window[0] >= 60.0:
                        self._window.popleft()

                    # Check if slot available
                    if len(self._window) < self._rpm:
                        self._window.append(now)
                        return time.monotonic() - wait_start

                    # Calculate wait time until next slot
                    sleep_for = 60.0 - (now - self._window[0])

            except Exception:
                # Fail-open: no limiting on errors (no state mutation)
                return 0.0

            # Sleep is ALWAYS outside the lock
            time.sleep(max(sleep_for, 0.01))


class ProviderRateLimiterRegistry:
    """
    Registry of per-provider rate limiters with thread-safe runtime updates.

    Lock separation:
    - SlidingWindowRateLimiter._lock: protects window operations within individual limiters
    - ProviderRateLimiterRegistry._registry_lock: protects mutation + snapshot only

    Immutability rules:
    - Provider-specific limiters are immutable (created once, never replaced)
    - Only default limiter is replaced via set_default_rpm()
    """

    def __init__(self, default_rpm: int, providers: Dict[str, int]):
        self._default = _NOOP if default_rpm == 0 else SlidingWindowRateLimiter(default_rpm)
        self._providers = {
            k.lower(): SlidingWindowRateLimiter(v)
            for k, v in providers.items()
        }
        self._registry_lock = threading.Lock()

    def resolve(self, provider: str | None) -> SlidingWindowRateLimiter:
        """
        Resolve the appropriate rate limiter for a provider.

        Uses zero-copy read pattern (providers are immutable).

        Args:
            provider: Provider name (case-insensitive, prefix-aware)

        Returns:
            Appropriate rate limiter (default if no match)
        """
        with self._registry_lock:
            default = self._default
            providers = self._providers  # no copy - providers are immutable

        # Do matching OUTSIDE lock to minimize contention
        if not provider:
            return default

        key = provider.lower()

        # Exact match
        if key in providers:
            return providers[key]

        # Prefix match (e.g., "nvidia-nim" → "nvidia")
        for name, limiter in providers.items():
            if key.startswith(name):
                return limiter

        return default

    def set_default_rpm(self, rpm: int) -> None:
        """
        Thread-safe runtime update of default RPM.

        Atomic replacement of default limiter instance.

        Args:
            rpm: New RPM setting (0 = disabled)
        """
        with self._registry_lock:
            self._default = _NOOP if rpm == 0 else SlidingWindowRateLimiter(rpm)


def make_registry(config: Dict) -> ProviderRateLimiterRegistry:
    """
    Factory function to create a rate limiter registry from config.

    Reads from config dict and HERMES_REQUESTS_PER_MINUTE env var.

    Args:
        config: Configuration dict with rate_limit section

    Returns:
        Configured ProviderRateLimiterRegistry
    """
    rl_cfg = config.get("rate_limit", {})
    default_rpm = int(os.environ.get("HERMES_REQUESTS_PER_MINUTE", 0)) \
                  or rl_cfg.get("requests_per_minute", 0)
    providers = rl_cfg.get("providers", {})
    return ProviderRateLimiterRegistry(default_rpm, providers)


def make_rate_limiter(rpm: int) -> SlidingWindowRateLimiter:
    """
    Simple factory to create a rate limiter.

    Args:
        rpm: Requests per minute (0 = disabled)

    Returns:
        SlidingWindowRateLimiter instance
    """
    return SlidingWindowRateLimiter(rpm)
