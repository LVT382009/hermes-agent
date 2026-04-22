# rate-limiter

Cross-session rate limit guard for side clients (Nous Portal, etc.) that prevents
retry amplification when rate limits are hit.

## Problem

Each 429 (rate limit) error from a provider triggers up to 9 API calls per conversation turn:
- 3 SDK retries × 3 Hermes retries = 9 calls
- Every call counts against RPH (requests per hour)
- This amplification can quickly exhaust rate limits

## Solution

This plugin records rate limit state on the first 429 and checks it before subsequent attempts across all sessions (CLI, gateway, cron, auxiliary).

## How it works

| Hook | Behaviour |
|---|---|
| `pre_llm_call` | Check if provider is currently rate-limited. If so, inject context to inform the user about the rate limit. |
| `post_llm_call` | If a 429 error is received, parse reset time from headers/error context and record to shared state file. |

**IMPORTANT**: The `pre_llm_call` hook cannot block LLM API calls - it can only inject context into the user message. When rate-limited, the plugin injects a warning message to inform the user, but the LLM API call still proceeds. Users should wait for the rate limit to expire before retrying.

State is stored in `$HERMES_HOME/rate_limits/nous.json` and is shared across all sessions.

## Reset time parsing

Priority order (first match wins):

1. `x-ratelimit-reset-requests-1h` - hourly RPH window (most useful)
2. `x-ratelimit-reset-requests` - per-minute RPM window
3. `retry-after` - generic HTTP header
4. Default cooldown: 5 minutes (300 seconds)

## Slash commands

```
/ratelimit status    # Show current rate limit status
/ratelimit clear     # Clear rate limit state manually
/ratelimit enable    # Enable the rate limiter
/ratelimit disable   # Disable the rate limiter
/ratelimit set <s>   # Set default cooldown time (seconds)
```

## Safety

- Atomic writes: temp file + rename for safe concurrent access
- Expired entries are automatically cleaned up on read
- State file is scoped to `$HERMES_HOME/rate_limits/`
- No external dependencies beyond standard library

## Testing

Run the test suite:

```bash
pytest tests/plugins/test_rate_limiter_plugin.py -v
```

Tests cover:
- Header parsing (priority order, invalid values)
- Rate limit recording (headers, error context, default cooldown)
- Rate limit checking (remaining time, expiration)
- Plugin hooks (pre_llm_call, post_llm_call)
- Slash commands (status, clear, enable, disable, set)
- Bundled plugin discovery
