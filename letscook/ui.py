"""Terminal UI helpers and prompts."""

import sys

from .constants import IS_WINDOWS


def _enable_ansi():
    if IS_WINDOWS:
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            mode = ctypes.c_uint()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                # Preserve existing console flags; only add virtual terminal processing.
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        except Exception:
            pass


_enable_ansi()


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def green(t):  return _c(str(t), "32")
def yellow(t): return _c(str(t), "33")
def cyan(t):   return _c(str(t), "36")
def red(t):    return _c(str(t), "31")
def bold(t):   return _c(str(t), "1")
def dim(t):    return _c(str(t), "2")


def section(title: str):
    print(f"\n{bold('─' * 50)}")
    print(f"  {bold(title)}")
    print(bold("─" * 50))


def ask(prompt: str, default: str = "") -> str:
    hint = f" {dim('[' + default + ']')}" if default else ""
    try:
        val = input(f"  {cyan('>')} {prompt}{hint}: ").strip()
    except (KeyboardInterrupt, EOFError):
        print(f"\n{yellow('  Aborted.')}")
        sys.exit(0)
    return val if val else default


def ask_yn(prompt: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    raw = ask(f"{prompt} ({hint})", "").lower()
    if not raw:
        return default
    return raw in ("y", "yes")


def ensure_utf8_output():
    """Avoid Unicode banner crashes in legacy Windows console encodings."""
    if not IS_WINDOWS:
        return

    for stream in (sys.stdout, sys.stderr):
        try:
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
