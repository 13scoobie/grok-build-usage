#!/usr/bin/env python3
"""
grok-usage helper script for the grok-usage skill.

Parses the last "billing: fetched credits config" entry from the grok unified log
and prints subscription / credit usage information.

This is how Grok (via the skill) surfaces usage without modifying the closed-source binary.

Usage:
  python scripts/usage.py
  python scripts/usage.py --json
  python scripts/usage.py --refresh
  python scripts/usage.py -h
"""

import json
import os
import sys

GROK_HOME = os.environ.get("GROK_HOME") or os.path.expanduser("~/.grok")
LOG_FILE = os.path.join(GROK_HOME, "logs", "unified.jsonl")
SCRIPT_NAME = "grok-usage"


def usage():
    print(f"""{SCRIPT_NAME} - Show your Grok subscription / credit usage

USAGE:
  {SCRIPT_NAME}
  {SCRIPT_NAME} --json
  {SCRIPT_NAME} --refresh
  {SCRIPT_NAME} -h | --help

The data is taken from the most recent billing fetch performed by the grok CLI
(appears in the log whenever you run grok). Use --refresh to force a new fetch
before displaying.

This script is invoked by the /grok-usage slash command skill.
""")


def main():
    args = sys.argv[1:]

    if "-h" in args or "--help" in args:
        usage()
        return 0

    want_json = "--json" in args
    do_refresh = "--refresh" in args

    if do_refresh:
        grok_bin = os.environ.get("GROK_BIN") or os.path.join(GROK_HOME, "bin", "grok")
        if os.path.isfile(grok_bin) and os.access(grok_bin, os.X_OK):
            print("Refreshing credits data (running 'grok models' briefly)...", file=sys.stderr)
            # This subcommand triggers auth + model catalog fetch, which also fetches billing/credits.
            import subprocess
            try:
                subprocess.run([grok_bin, "models"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=8)
            except Exception:
                pass
            # Give the log a moment to flush
            import time
            time.sleep(0.4)
        else:
            print(f"Warning: could not locate grok binary at {grok_bin} for refresh", file=sys.stderr)

    last_ctx = None

    if "--stdin" in args or (not sys.stdin.isatty()):
        # Support: tail ... | grep ... | python usage.py [--json]
        try:
            data = sys.stdin.read()
            line = data.strip().splitlines()[-1] if data.strip() else ""
            if line:
                obj = json.loads(line)
                last_ctx = obj.get("ctx") or obj
        except Exception:
            pass

    if last_ctx is None:
        if not os.path.isfile(LOG_FILE):
            msg = f"No grok log found at: {LOG_FILE}\nRun 'grok' or 'grok models' at least once."
            if want_json:
                print(json.dumps({"error": msg}))
            else:
                print(msg)
            return 1

        # Stream to find the *last* matching entry (memory efficient + faster on large logs)
        last_line = None
        try:
            with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if "billing: fetched credits config" in line:
                        last_line = line
        except Exception as e:
            err = f"Failed to read log: {e}"
            if want_json:
                print(json.dumps({"error": err}))
            else:
                print(err)
            return 1

        if last_line:
            try:
                obj = json.loads(last_line.strip())
                last_ctx = obj.get("ctx") or {}
            except Exception:
                pass

    if not last_ctx:
        msg = ("No billing/credits data found in the log yet.\n"
               "Start a grok session (or run 'grok models') to populate it, then try again.")
        if want_json:
            print(json.dumps({"error": msg}))
        else:
            print(msg)
        return 1

    config = last_ctx.get("config") or {}
    tier = last_ctx.get("subscriptionTier") or config.get("subscriptionTier") or "Unknown"
    usage_pct = config.get("creditUsagePercent", 0)
    period = config.get("currentPeriod") or {}
    period_type = period.get("type", "unknown").replace("USAGE_PERIOD_TYPE_", "")
    start = (period.get("start") or config.get("billingPeriodStart") or "")[:10]
    end = (period.get("end") or config.get("billingPeriodEnd") or "")[:10]
    on_demand_cap = (config.get("onDemandCap") or {}).get("val", 0)
    on_demand_used = (config.get("onDemandUsed") or {}).get("val", 0)
    prepaid = (config.get("prepaidBalance") or {}).get("val", 0)

    if want_json:
        # Return only the safe, documented fields (no raw internal ctx for privacy + smaller output)
        out = {
            "subscriptionTier": tier,
            "creditUsagePercent": usage_pct,
            "currentPeriod": {
                "type": period.get("type"),
                "start": period.get("start") or config.get("billingPeriodStart"),
                "end": period.get("end") or config.get("billingPeriodEnd"),
            },
            "onDemandCap": on_demand_cap,
            "onDemandUsed": on_demand_used,
            "prepaidBalance": prepaid,
        }
        print(json.dumps(out, indent=2))
        return 0

    # Human readable
    print("Grok Subscription\n")
    print(f"  Tier:               {tier}")
    print(f"  Credit usage:       {usage_pct}%\n")
    print(f"  Period:             {start} → {end}   ({period_type})")
    print(f"  On-demand balance:  {on_demand_used} / {on_demand_cap}")
    print(f"  Prepaid balance:    {prepaid}\n")
    print("Data as of last grok CLI credits fetch.")
    print("Run any grok command (or /grok-usage --refresh) to update.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
