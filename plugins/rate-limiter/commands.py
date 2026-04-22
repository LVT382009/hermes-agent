"""Slash commands for rate limiter plugin.

Provides runtime control over the cross-session rate limit guard.
"""

import logging
from typing import Optional

from .rate_limiter import (
    clear_rate_limit,
    format_remaining,
    get_default_cooldown,
    get_rate_limit_remaining,
    is_enabled,
    set_default_cooldown,
    set_enabled,
)

logger = logging.getLogger(__name__)


def ratelimit_status(args: Optional[list[str]] = None) -> str:
    """Show current rate limit status.

    Usage: /ratelimit status

    Returns:
        Human-readable status message.
    """
    enabled = is_enabled()
    remaining = get_rate_limit_remaining()
    cooldown = get_default_cooldown()

    status_lines = [
        f"Rate limiter: {'✓ ENABLED' if enabled else '✗ DISABLED'}",
        f"Default cooldown: {format_remaining(cooldown)}",
    ]

    if remaining is not None:
        status_lines.append(f"⚠ Rate limit active. Resets in {format_remaining(remaining)}.")
    else:
        status_lines.append("✓ No active rate limit. Requests will proceed normally.")

    return "\n".join(status_lines)


def ratelimit_clear(args: Optional[list[str]] = None) -> str:
    """Clear the rate limit state.

    Usage: /ratelimit clear

    WARNING: This will allow requests to proceed even if the provider
    is still rate-limited, which may result in additional 429 errors.

    Returns:
        Confirmation message.
    """
    clear_rate_limit()
    return "✓ Rate limit state cleared. Requests will proceed normally."


def ratelimit_enable(args: Optional[list[str]] = None) -> str:
    """Enable the rate limiter.

    Usage: /ratelimit enable

    Returns:
        Confirmation message.
    """
    set_enabled(True)
    return "✓ Rate limiter enabled. Requests will be rate-limited when 429 errors are detected."


def ratelimit_disable(args: Optional[list[str]] = None) -> str:
    """Disable the rate limiter.

    Usage: /ratelimit disable

    WARNING: This will allow requests to proceed even when rate limits
    are hit, which may result in additional 429 errors and retry amplification.

    Returns:
        Confirmation message.
    """
    set_enabled(False)
    return "✓ Rate limiter disabled. Requests will proceed normally even when rate-limited."


def ratelimit_set(args: Optional[list[str]] = None) -> str:
    """Set the default cooldown time.

    Usage: /ratelimit set <seconds>

    Args:
        args: List containing the cooldown time in seconds.

    Returns:
        Confirmation message or error.
    """
    if not args or len(args) < 1:
        return "✗ Usage: /ratelimit set <seconds>\nExample: /ratelimit set 300"

    try:
        cooldown = float(args[0])
        if cooldown < 0:
            return "✗ Cooldown must be non-negative."
        set_default_cooldown(cooldown)
        return f"✓ Default cooldown set to {format_remaining(cooldown)}."
    except ValueError:
        return "✗ Invalid cooldown value. Must be a number (seconds)."


def handle(raw_args: str) -> Optional[str]:
    """Main handler for /ratelimit slash command.

    Dispatches to subcommands: status, clear, enable, disable, set

    Args:
        raw_args: Command arguments as a string.

    Returns:
        Response message, or None if no output.
    """
    argv = raw_args.strip().split()
    if not argv or argv[0] in ("help", "-h", "--help"):
        return """Rate limiter runtime controls.

Usage:
  /ratelimit status    Show current rate limit status
  /ratelimit clear     Clear rate limit state manually
  /ratelimit enable    Enable the rate limiter
  /ratelimit disable   Disable the rate limiter
  /ratelimit set <s>   Set default cooldown time (seconds)

The core rate limiter is always active — this plugin adds runtime controls.
"""

    sub = argv[0]

    if sub == "status":
        return ratelimit_status()

    if sub == "clear":
        return ratelimit_clear()

    if sub == "enable":
        return ratelimit_enable()

    if sub == "disable":
        return ratelimit_disable()

    if sub == "set":
        return ratelimit_set(argv[1:])

    return f"Unknown ratelimit subcommand: {sub}. Use /ratelimit help for usage."
