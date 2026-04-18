"""Setup wizard and setup-related inputs."""

from .config_io import save_config
from .constants import BANNER, OS_LABEL
from .library import lib_to_config, os_apps
from .picker import pick_apps
from .ui import ask, ask_yn, bold, dim, green, section

def edit_urls(existing: list = None) -> list:
    section("URLS")
    print("  Enter the URLs to open in your browser.")
    print(dim("  Type one URL per line. Leave blank and press Enter when done.\n"))

    urls = []
    if existing:
        for i, u in enumerate(existing, 1):
            print(f"    {i}. {u}")
        print()
        if ask_yn("  Keep these URLs?", True):
            urls = list(existing)

    while True:
        raw = ask("  Add URL (blank = done)", "")
        if not raw:
            break
        for u in raw.split(","):
            u = u.strip()
            if not u:
                continue
            if not u.startswith(("http://", "https://")):
                u = "https://" + u
            urls.append(u)
            print(green(f"    + {u}"))

    return urls


# ─── Custom App Builder ───────────────────────────────────────────────────────


def build_custom_app() -> dict | None:
    name = ask("  App display name (blank = cancel)", "")
    if not name:
        return None
    cmd      = ask(f"  Command or full path to launch {name}", "")
    args_raw = ask("  Extra args (space-separated, or blank)", "")
    return {
        "name":    name,
        "cat":     "Custom",
        "enabled": True,
        "command": cmd,
        "args":    args_raw.split() if args_raw else [],
    }


# ─── Library → Config Converter ───────────────────────────────────────────────


def run_setup(existing: dict = None) -> dict:
    print(BANNER)
    print(bold(f"\n  Welcome to Let's Cook setup!  OS: {OS_LABEL}\n"))

    # Step 1 — Pick apps
    section("STEP 1 / 3  —  SELECT YOUR APPS")
    pre_selected = {a["name"] for a in existing.get("apps", [])} if existing else set()
    chosen = pick_apps(os_apps(), pre_selected)

    # Step 1b — Custom apps
    section("STEP 1b  —  CUSTOM APPS  (optional)")
    custom = []
    while ask_yn("  Add a custom app not in the list?", False):
        entry = build_custom_app()
        if entry:
            custom.append(entry)

    apps = [lib_to_config(a) for a in chosen] + custom

    # Step 2 — URLs
    has_browser = any(a.get("cat") == "Browsers" for a in chosen)
    if has_browser:
        urls = edit_urls(existing.get("urls") if existing else None)
    else:
        urls = list(existing.get("urls", [])) if existing else []

    # Step 3 — Delay
    section("STEP 3 / 3  —  TIMING")
    delay_default = str(existing.get("delay", 1.5) if existing else 1.5)
    try:
        delay = float(ask("  Seconds between app launches", delay_default))
    except ValueError:
        delay = 1.5

    config = {"apps": apps, "urls": urls, "delay": delay}
    save_config(config)
    print(green("\n  All set! Run  lets_cook  anytime to fire everything up.\n"))
    return config


# ─── Management Commands ──────────────────────────────────────────────────────
