"""Config file loading and saving."""

import json

from .constants import CONFIG_DIR, CONFIG_FILE
from .ui import green, red

def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            print(red("  Warning: config file is corrupted. Starting fresh."))
    return {}


def save_config(config: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print(green(f"\n  Config saved -> {CONFIG_FILE}"))


# ─── Filtered Library ─────────────────────────────────────────────────────────

