"""
/ratelimit subcommand handlers.

  /ratelimit help          — show help message
  /ratelimit status        — show state, rpm, per-provider limits
  /ratelimit enable        — re-enable (restores rpm from config default)
  /ratelimit disable       — set rpm=0 for this session
  /ratelimit set <rpm>     — set rpm immediately (0–3600, runtime only)
"""

from __future__ import annotations


def handle(raw_args: str, registry) -> str:
    """
    Handle /ratelimit slash command.

    Args:
        raw_args: Raw command arguments as a string
        registry: ProviderRateLimiterRegistry instance

    Returns:
        Response message
    """
    parts = raw_args.strip().split()
    sub = parts[0].lower() if parts else "status"

    if sub == "help":
        return _help()
    if sub == "status":
        return _status(registry)
    if sub == "enable":
        return _enable(registry)
    if sub == "disable":
        registry.set_default_rpm(0)
        return "🔴 Rate limiter disabled for this session. Edit config.yaml to persist."
    if sub == "set":
        if len(parts) < 2:
            return "Usage: /ratelimit set <rpm>  (e.g. /ratelimit set 40)"
        try:
            rpm = int(parts[1])
        except ValueError:
            return f"❌ '{parts[1]}' is not a valid number."
        if not 0 <= rpm <= 3600:
            return "❌ RPM must be 0–3600."
        registry.set_default_rpm(rpm)
        return f"✅ Rate limiter set to {rpm} rpm (runtime only). Edit config.yaml to persist."
    return f"Unknown subcommand '{sub}'. Try: help, enable, disable, status, set <rpm>"


def _status(registry) -> str:
    """Generate status message."""
    rpm = registry.resolve(None).rpm
    state = f"🟢 enabled ({rpm} rpm)" if rpm > 0 else "🔴 disabled (rpm=0)"
    lines = [f"Rate limiter: {state}"]
    per_provider = [
        f"  {name}: {lim.rpm} rpm"
        for name, lim in registry._providers.items()
        if lim.rpm > 0
    ]
    if per_provider:
        lines.append("Per-provider:")
        lines.extend(per_provider)
    return "\n".join(lines)


def _enable(registry) -> str:
    """Enable rate limiter with safe default."""
    if registry.resolve(None).rpm > 0:
        return f"✅ Already enabled ({registry.resolve(None).rpm} rpm)."
    registry.set_default_rpm(40)
    return "✅ Rate limiter enabled (40 rpm). Use /ratelimit set <rpm> to change."


def _help() -> str:
    """Show help message."""
    return """🐢 Rate Limiter Commands

/ratelimit help          — Show this help message
/ratelimit status        — Show current state and limits
/ratelimit enable        — Enable rate limiting (default: 40 rpm)
/ratelimit disable       — Disable for this session
/ratelimit set <rpm>     — Set RPM immediately (0–3600, runtime only)

💡 Runtime changes (enable/disable/set) only affect the current session.
   To persist changes, edit ~/.hermes/config.yaml:
     rate_limit:
       requests_per_minute: 40
"""
