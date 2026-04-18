"""Interactive app picker TUI."""

import re
import shutil
import sys

from .constants import IS_WINDOWS, OS_KEY
from .install_detection import check_installed
from .ui import bold, cyan, dim, green, yellow

_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")


def _render_rows(lines: list[str], cols: int) -> int:
    """Count terminal rows occupied by rendered lines (accounting for wraps)."""
    cols = max(cols, 1)
    rows = 0
    for line in lines:
        plain = _ANSI_RE.sub("", line)
        rows += max(1, (len(plain) + cols - 1) // cols)
    return rows


def _read_key() -> str | None:
    """Return a key name: 'up','down','space','enter','backspace', or a character."""
    if IS_WINDOWS:
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ('\x00', '\xe0'):          # special key prefix
            ch2 = msvcrt.getwch()
            return {'H': 'up', 'P': 'down'}.get(ch2)
        if ch == '\r':   return 'enter'
        if ch == ' ':    return 'space'
        if ch == '\x08': return 'backspace'
        if ch == '\x03': raise KeyboardInterrupt
        return ch if ch.isprintable() else None
    else:
        import tty, termios
        fd  = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                nxt = sys.stdin.read(2)
                return {'[A': 'up', '[B': 'down'}.get(nxt)
            if ch in ('\r', '\n'): return 'enter'
            if ch == ' ':          return 'space'
            if ch in ('\x7f', '\x08'): return 'backspace'
            if ch == '\x03': raise KeyboardInterrupt
            return ch if ch.isprintable() else None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


# ─── TUI App Picker ───────────────────────────────────────────────────────────

MAX_VISIBLE = 16   # max rows shown at once


def pick_apps(available: list, pre_selected: set = None) -> list:
    """
    Arrow keys navigate, Space toggles, type to filter, Enter confirms.
    No external libraries — pure stdlib raw terminal input.
    """
    selected = set(pre_selected or set())
    cursor   = 0
    search   = ""
    offset   = 0    # first visible index into filtered list
    prev_rows = 0   # rendered terminal rows in last frame (includes wrapped lines)

    # Pre-warm install cache before entering raw mode
    sys.stdout.write(f"\n  {bold('Checking installation status...')} ")
    sys.stdout.flush()
    for app in available:
        check_installed(app)
    sys.stdout.write(green("done\n\n"))
    sys.stdout.flush()

    while True:
        # ── Filter list ──
        q        = search.lower()
        filtered = [a for a in available
                    if q in a["name"].lower() or q in a["cat"].lower()] if q else list(available)
        total_f  = len(filtered)

        # ── Clamp cursor + adjust scroll window ──
        cursor = max(0, min(cursor, total_f - 1)) if total_f else 0
        if cursor < offset:
            offset = cursor
        elif cursor >= offset + MAX_VISIBLE:
            offset = cursor - MAX_VISIBLE + 1

        # ── Build frame ──
        SEP = "─" * 54
        term_cols = shutil.get_terminal_size((80, 24)).columns
        # Keep row width inside terminal to prevent wrapping, which can desync redraw on Windows.
        name_w = 22
        cat_w = 20
        if term_cols < 72:
            shrink = 72 - term_cols
            cat_cut = min(shrink, cat_w - 8)
            cat_w -= cat_cut
            shrink -= cat_cut
            if shrink > 0:
                name_cut = min(shrink, name_w - 8)
                name_w -= name_cut

        frame = []
        frame.append(f"  {bold(SEP)}")
        search_display = cyan(search) if search else dim("type to filter…")
        frame.append(f"  Search : {search_display}   {dim('|')}   "
                     f"{cyan(str(len(selected)))} selected / {total_f} shown")
        frame.append(f"  {dim('↑↓ navigate   Space select   Enter confirm   Bksp erase')}")
        frame.append(f"  {bold(SEP)}")

        if not filtered:
            frame.append(yellow("  No apps match."))
        else:
            vis_end = min(offset + MAX_VISIBLE, total_f)
            if offset > 0:
                frame.append(dim(f"  ↑  {offset} more above"))

            for i in range(offset, vis_end):
                app    = filtered[i]
                ticked = app["name"] in selected
                inst   = check_installed(app)

                # Build plain strings first (no ANSI) for correct width calculation
                tick  = "[x]" if ticked else "[ ]"
                name  = app["name"][:name_w].ljust(name_w)
                badge = "installed" if inst else "not found"
                cat   = app["cat"][:cat_w]
                arrow = "> " if i == cursor else "  "

                if i == cursor:
                    # Reverse-video highlight — keep the whole row plain text
                    row = f"\033[7m  {arrow}{tick}  {name}  {badge:<10}  {cat}\033[0m"
                else:
                    # Colour only individual tokens (no ljust on ANSI strings)
                    tick_c  = f"\033[36m{tick}\033[0m" if ticked else tick
                    badge_c = f"\033[32m{badge}\033[0m" if inst else f"\033[33m{badge}\033[0m"
                    cat_c   = f"\033[2m{cat}\033[0m"
                    row = f"    {tick_c}  {name}  {badge_c:<10}  {cat_c}"

                frame.append(row)

            if vis_end < total_f:
                frame.append(dim(f"  ↓  {total_f - vis_end} more below"))

        frame.append(f"  {bold(SEP)}")

        # ── Erase last frame, draw new one ──
        if prev_rows:
            # Move to previous frame start and clear downward.
            sys.stdout.write(f"\033[{prev_rows}F\033[J")
        sys.stdout.write("\n".join(frame) + "\n")
        sys.stdout.flush()
        prev_rows = _render_rows(frame, term_cols)

        # ── Handle keypress ──
        try:
            key = _read_key()
        except KeyboardInterrupt:
            sys.stdout.write("\n")
            print(yellow("\n  Cancelled."))
            sys.exit(0)

        if key == 'up':
            cursor = max(0, cursor - 1)
        elif key == 'down':
            cursor = min(total_f - 1, cursor + 1) if total_f else 0
        elif key == 'space':
            if filtered:
                name = filtered[cursor]["name"]
                if name in selected:
                    selected.discard(name)
                else:
                    selected.add(name)
                    if not check_installed(filtered[cursor]):
                        # Shown in badge column — no extra print needed
                        pass
        elif key == 'enter':
            sys.stdout.write("\n")
            for nm in list(selected):
                app = next((a for a in available if a["name"] == nm), None)
                if app and not check_installed(app):
                    print(yellow(f"  Warning: {nm} not detected — verify its command after setup."))
            break
        elif key == 'backspace':
            search = search[:-1]
            cursor = 0
            offset = 0
        elif key and len(key) == 1:
            search += key
            cursor = 0
            offset = 0

    return [a for a in available if a["name"] in selected]



def toggle_apps(apps: list, pre_enabled: set = None) -> set:
    """Same TUI for toggling already-configured apps ON/OFF."""
    pseudo = [
        {"name": a["name"], "cat": a.get("cat", "Custom"),
         "platform": "both",
         OS_KEY: {"cmd": a.get("command", ""), "check": None, "args": []}}
        for a in apps
    ]
    chosen = pick_apps(pseudo, pre_enabled)
    return {a["name"] for a in chosen}


# ─── URL Editor ───────────────────────────────────────────────────────────────
