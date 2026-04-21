"""
rate-limiter — built-in Hermes plugin.

Ships disabled. Enable with: hermes plugins enable rate-limiter

Provides /ratelimit slash commands.
The core limiter in run_agent.py is the enforcement layer.
This plugin is a control surface only.
"""

import logging
from .commands import handle

logger = logging.getLogger(__name__)
_registry = None


def _on_session_start(**kwargs) -> None:
    if _registry is None:
        return
    rpm = _registry.resolve(None).rpm
    if rpm > 0:
        logger.info("🐢 rate-limiter active (%d rpm). /ratelimit status for details.", rpm)


def register(ctx) -> None:
    global _registry

    # Prefer the shared registry already on the AIAgent instance
    try:
        _registry = getattr(ctx.agent, "_rl_registry", None)
    except AttributeError:
        pass

    if _registry is None:
        from agent.rate_limiter import make_registry
        _registry = make_registry(getattr(ctx, "config", {}))

    ctx.register_command(
        "ratelimit",
        handler=lambda raw_args: handle(raw_args, _registry),
        description="Control the rate limiter: enable, disable, status, set <rpm>",
    )
    ctx.register_hook("on_session_start", _on_session_start)
