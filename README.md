# Grok Build Usage

**`/grok-usage`** — See your Grok subscription usage, credits, and billing period right inside the terminal.

A tiny, installable skill for the [Grok Build TUI](https://x.ai) (the official `grok` CLI from xAI).

## Why?

The Grok CLI already tracks your usage internally (SuperGrok, credit usage, weekly periods, etc.), but there's no built-in terminal command to view the numbers easily. This skill adds `/grok-usage` using only data the CLI already writes to its logs.

## Install (30 seconds)

```bash
git clone https://github.com/yourname/grok-usage.git
cd grok-usage
./install.sh
```

Or manually:

```bash
cp -r grok-usage ~/.grok/skills/
```

Then open (or restart) `grok`. The command appears in the `/` menu automatically.

## Usage

```bash
/grok-usage
/grok-usage --json
/grok-usage --refresh          # force a fresh data fetch (slower)
/grok-usage --refresh --json
```

The normal path is deliberately lightweight (`tail | grep`) for minimal latency and output.

## Example Output

```
Grok Subscription

  Tier:               SuperGrok Heavy
  Credit usage:       4.0%

  Period:             2026-06-26 → 2026-07-03   (WEEKLY)
  On-demand balance:  0 / 0
  Prepaid balance:    0

Data as of last grok CLI credits fetch.
Run any grok command (or /grok-usage --refresh) to update.
```

(JSON output also available for scripting.)

JSON mode returns clean structured data you can pipe to `jq`.

## How it works

- The official `grok` binary logs billing info on every start (`~/.grok/logs/unified.jsonl`)
- This skill just reads the last entry
- No external API calls, no secrets, no modifications to the closed-source binary
- Implemented as a standard Grok user skill (see [Grok skills docs](https://grok.x.ai))

## Privacy & Data

This project only ever reads your local `~/.grok/logs/unified.jsonl` file. It never touches `auth.json`, never makes network calls, and never leaks tokens or other credentials.

- In normal mode it prints a human summary.
- `--json` returns only the extracted usage fields (subscriptionTier, creditUsagePercent, periods, balances). The full internal ctx ("raw") is intentionally omitted.

The data surfaced is *your* subscription usage — that's the whole point of the tool.

## Requirements

- The official Grok CLI/TUI
- `tail` + `grep` (for the fast low-latency path used by `/grok-usage`)
- Python 3 (only needed for `--refresh`, direct `python usage.py`, or the legacy script)

Works on macOS and Linux. Windows users can use WSL / Git Bash.

## Project layout

```
.
├── README.md
├── install.sh
└── grok-usage/           # <-- this folder goes to ~/.grok/skills/
    ├── SKILL.md
    └── scripts/
        └── usage.py
```

## Notes

- The built-in `/usage` command exists but this gives you the actual numbers in the terminal.
- Because the core `grok` binary is closed source, skills are the official supported way to extend the TUI.
- Skill auto-reloads when files change.

## For xAI / Grok users

If you find this useful, a native `grok usage` subcommand would be even better. In the meantime — this works today.

---

**Quick X post suggestion:**

"Added /grok-usage to my Grok terminal so I can finally see my subscription credits without leaving the TUI.

Super simple skill (no binary hacks):
git clone ... && ./install.sh
Then just type /grok-usage

Fast native path (tail+grep) = almost zero added latency.

Repo: [link]

Works with the official grok CLI from x.ai"
