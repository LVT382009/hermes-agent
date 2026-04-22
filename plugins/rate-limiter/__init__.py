"""Rate limiter plugin for Hermes Agent.

Provides cross-session rate limit guard for side clients that prevents
retry amplification when rate limits are hit.

Hooks:
  - pre_llm_call: Check if rate-limited before making API calls
  - post_llm_call: Record rate limit if 429 received

Slash commands:
  - /ratelimit status: Check rate limit status
  - /ratelimit clear: Clear rate limit state
  - /ratelimit enable: Enable rate limiter
  - /ratelimit disable: Disable rate limiter
  - /ratelimit set <seconds>: Set default cooldown
"""

from __future__ import annotations

from . import commands
from . import rate_limiter


def register(ctx) -> None:
    """Register the rate limiter plugin with the plugin system."""
    # Register hooks for rate limit enforcement
    ctx.register_hook("pre_llm_call", rate_limiter.check_rate_limit)
    ctx.register_hook("post_llm_call", rate_limiter.record_rate_limit_hook)

    # Register slash commands for runtime control
    ctx.register_command(
        "ratelimit",
        handler=commands.handle,
        description="Runtime controls for the rate limiter.",
    )
