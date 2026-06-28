---
name: grok-usage
description: >
  Display your current Grok subscription tier, credit usage, billing period,
  on-demand and prepaid balances directly in the terminal. Use when the user
  types /grok-usage, /grok-usage --json, or asks about "grok usage", "my credits",
  "subscription status", "how much have I used", "grok subscription", or
  "billing info".
argument-hint: "[--json]"
user-invocable: true
---

# /grok-usage — Grok Subscription Usage

Show the user's current Grok (xAI) subscription and credit usage information
pulled from the CLI's internal billing data (the same data the official client
already fetches on startup).

## Invocation

- `/grok-usage` — human readable summary
- `/grok-usage --json` — machine readable JSON (useful for scripting or further processing)
- `/grok-usage --refresh` — force a fresh fetch of credits data (runs `grok models` briefly) then show summary
- `/grok-usage --refresh --json` — refresh + JSON output

**Note:** There is a built-in `/usage` command. This skill provides the detailed
terminal view using the name `/grok-usage` to avoid conflict. You can also use
the qualified form `/user:grok-usage` if needed.

## Steps to fulfill a request

1. Determine the desired output format from the user's slash command:
   - If they typed `/grok-usage --json` (or similar), use JSON mode.
   - Otherwise use the default human-readable mode.

2. For the common case (human readable or --json, without refresh) use this **fast native command** (avoids Python startup):

   ```
   tail -n 200 ~/.grok/logs/unified.jsonl | grep -F 'billing: fetched credits config' | tail -1
   ```

   Parse the single resulting JSON line (it contains the .ctx), then format exactly as described below.

   For --refresh (or direct script use) you may still run the helper:
   ```
   python ~/.grok/skills/grok-usage/scripts/usage.py [--json] [--refresh]
   ```

   The script handles the grok models side-effect for --refresh.

3. Capture the (very small) tool result.

4. **Output ONLY the usage information.** Do not add any introductory text ("Here's your usage..."), explanations, or extra newlines. Just the block or JSON.

   - Normal mode: the nicely formatted summary (see "What the data means").
   - --json mode: a clean JSON object with subscriptionTier, creditUsagePercent, currentPeriod, onDemand*, prepaidBalance.

5. If no data line is present:
   - Tell the user to run any `grok` command (e.g. `grok models` or just start a session)
     to trigger a fresh billing/credits fetch.
   - Then they can run `/grok-usage` again.

## What the data means

The script surfaces:
- `subscriptionTier` (e.g. "SuperGrok Heavy")
- `creditUsagePercent` for the current period
- Billing period start/end and type (usually WEEKLY)
- On-demand and prepaid balances

This gives the user a quick terminal view of where they stand with their Grok subscription
without leaving the TUI or opening a browser.

## Implementation notes (for you)

- The *fast path* (normal /grok-usage and --json) uses only `tail | grep | tail` + your formatting. No Python.
- The Python script is kept for `--refresh`, direct shell use (`python usage.py`), and as a reference.
- The script (and the tail command) read `~/.grok/logs/unified.jsonl`.
- The actual fresh data is populated by the grok binary itself on startup / `grok models`.
- Never call external APIs. Only use locally logged data.
- Always output *only* the usage block/JSON (the model instruction above enforces this for low latency + clean UX).

## Future improvements (optional)

Later we can enhance the script to accept `--refresh` (which would run `grok models`
in the background first to force a new fetch). For now the current behavior is
reliable and matches how the rest of the CLI works.
