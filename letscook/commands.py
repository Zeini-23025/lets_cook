"""Management commands for add/edit/remove/list flows."""

from .config_io import save_config
from .constants import BANNER, CONFIG_FILE
from .library import lib_to_config, os_apps
from .picker import pick_apps, toggle_apps
from .setup_wizard import build_custom_app, edit_urls
from .ui import ask, cyan, dim, green, red, section, yellow

def _simple_menu(title: str, options: list[tuple]) -> str:
    """Print a numbered menu, return the chosen value."""
    print(f"\n  {bold(title)}\n")
    for i, (label, _) in enumerate(options, 1):
        print(f"  {i}.  {label}")
    print()
    while True:
        raw = ask("  Choice", "")
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return options[idx][1]
        print(yellow(f"  Enter a number between 1 and {len(options)}."))



def cmd_add(config: dict) -> dict:
    section("ADD")
    action = _simple_menu("What would you like to add?", [
        ("Pick from the app library",  "lib"),
        ("Add a custom app or script", "custom"),
        ("Add URLs",                   "url"),
        ("Cancel",                     "cancel"),
    ])

    configured_names = {a["name"] for a in config.get("apps", [])}

    if action == "lib":
        available = [a for a in os_apps() if a["name"] not in configured_names]
        if not available:
            print(yellow("  All library apps are already in your config."))
        else:
            chosen = pick_apps(available)
            new_entries = [lib_to_config(a) for a in chosen]
            config.setdefault("apps", []).extend(new_entries)
            print(green(f"\n  Added {len(new_entries)} app(s)."))
            save_config(config)

    elif action == "custom":
        entry = build_custom_app()
        if entry:
            config.setdefault("apps", []).append(entry)
            print(green(f"\n  Added: {entry['name']}"))
            save_config(config)

    elif action == "url":
        new_urls = edit_urls(None)
        config.setdefault("urls", []).extend(new_urls)
        print(green(f"\n  Added {len(new_urls)} URL(s)."))
        save_config(config)

    return config



def cmd_edit(config: dict) -> dict:
    section("EDIT")
    action = _simple_menu("What would you like to edit?", [
        ("Toggle apps ON/OFF or change a command", "apps"),
        ("Edit URLs",                              "urls"),
        ("Change launch delay",                    "delay"),
        ("Cancel",                                 "cancel"),
    ])

    if action == "apps":
        apps = config.get("apps", [])
        if not apps:
            print(yellow("  No apps configured yet."))
            return config

        currently_on = {a["name"] for a in apps if a.get("enabled", True)}
        enabled_now  = toggle_apps(apps, currently_on)

        for app in apps:
            app["enabled"] = app["name"] in enabled_now

        # Allow command edits
        print(f"\n  {dim('To change a command, type its number. Blank = done.')}")
        for i, app in enumerate(apps, 1):
            print(f"  {i:3}.  {app['name']:<24}  {dim(app.get('command',''))}")
        print()
        while True:
            raw = ask("  Edit command # (blank = done)", "")
            if not raw or not raw.isdigit():
                break
            idx = int(raw) - 1
            if 0 <= idx < len(apps):
                new_cmd = ask(f"  New command for {apps[idx]['name']}", apps[idx].get("command", ""))
                apps[idx]["command"] = new_cmd
                print(green(f"  Updated."))

        config["apps"] = apps
        save_config(config)

    elif action == "urls":
        config["urls"] = edit_urls(config.get("urls", []))
        save_config(config)

    elif action == "delay":
        try:
            config["delay"] = float(ask("  New delay (seconds)", str(config.get("delay", 1.5))))
            save_config(config)
        except ValueError:
            print(yellow("  Invalid number — unchanged."))

    return config



def cmd_remove(config: dict) -> dict:
    section("REMOVE")
    apps = config.get("apps", [])
    urls = config.get("urls", [])

    if not apps and not urls:
        print(yellow("  Nothing configured to remove."))
        return config

    print("\n  ── Apps ──")
    for i, app in enumerate(apps, 1):
        print(f"  {i:3}.  {app['name']}")
    offset = len(apps)
    print("\n  ── URLs ──")
    for j, url in enumerate(urls, offset + 1):
        print(f"  {j:3}.  {url}")
    print()
    raw = ask("  Numbers to remove (comma-separated, blank = cancel)", "")
    if not raw:
        return config

    picks = {int(t.strip()) for t in raw.split(",") if t.strip().isdigit()}
    app_idx_remove = {i - 1 for i in picks if 1 <= i <= offset}
    url_idx_remove = {i - offset - 1 for i in picks if offset < i <= offset + len(urls)}

    config["apps"] = [a for i, a in enumerate(apps) if i not in app_idx_remove]
    config["urls"] = [u for i, u in enumerate(urls) if i not in url_idx_remove]

    print(green(f"\n  Removed {len(app_idx_remove)} app(s) and {len(url_idx_remove)} URL(s)."))
    save_config(config)
    return config



def cmd_list(config: dict):
    print(BANNER)
    apps  = config.get("apps", [])
    urls  = config.get("urls", [])
    delay = config.get("delay", 1.5)

    section(f"APPS  ({len(apps)} configured)")
    if not apps:
        print(yellow("  None."))
    else:
        current_cat = None
        for app in apps:
            cat = app.get("cat", "Custom")
            if cat != current_cat:
                current_cat = cat
                print(f"\n  {dim('── ' + cat)}")
            state = green("ON ") if app.get("enabled", True) else red("OFF")
            print(f"    [{state}]  {app['name']:<24}  {dim(app.get('command',''))}")

    section(f"URLS  ({len(urls)})")
    for u in urls:
        print(f"    {cyan(u)}")
    if not urls:
        print(yellow("  None."))

    section("SETTINGS")
    print(f"    Delay between apps : {delay}s")
    print(f"    Config file        : {CONFIG_FILE}\n")


# ─── Launcher ─────────────────────────────────────────────────────────────────
