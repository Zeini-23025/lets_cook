"""CLI entrypoint wiring."""

import sys

from .commands import cmd_add, cmd_edit, cmd_list, cmd_remove
from .config_io import load_config
from .constants import BANNER, HELP_TEXT
from .launcher import cook
from .setup_wizard import run_setup
from .ui import ensure_utf8_output, yellow

def main():
    ensure_utf8_output()
    argv = sys.argv[1:]

    if "--help" in argv or "-h" in argv:
        print(BANNER)
        print(HELP_TEXT)
        return

    if "--setup" in argv or "-s" in argv:
        config = run_setup(load_config() or None)
        return

    config = load_config()

    if "--add" in argv:
        config = cmd_add(config) if config else run_setup()
        return

    if "--edit" in argv:
        config = cmd_edit(config) if config else run_setup()
        return

    if "--remove" in argv:
        if not config:
            print(yellow("  Nothing to remove — no config found."))
        else:
            cmd_remove(config)
        return

    if "--list" in argv:
        if not config:
            print(yellow("  No config found. Run  lets_cook --setup  to get started."))
        else:
            cmd_list(config)
        return

    if not config:
        print(yellow("  No config found — let's set things up!\n"))
        config = run_setup()

    cook(config)
