#!/usr/bin/env python3
"""Install Let's Cook as a global user command on Windows/Linux/macOS.

Creates launcher scripts in ~/.letscook/bin and ensures that directory
is present in the user's PATH.
"""

from __future__ import annotations

import argparse
import os
import platform
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parent


def _bin_dir() -> Path:
    return Path.home() / ".letscook" / "bin"


def _entrypoint() -> Path:
    return _repo_root() / "lets_cook.py"


def _write_text(path: Path, content: str, dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _install_launchers(bin_dir: Path, entry: Path, python_exe: Path, dry_run: bool) -> list[Path]:
    created: list[Path] = []

    if os.name == "nt":
        for name in ("lets_cook.cmd", "letscook.cmd"):
            launcher = bin_dir / name
            content = (
                "@echo off\n"
                "setlocal\n"
                f"\"{python_exe}\" \"{entry}\" %*\n"
            )
            _write_text(launcher, content, dry_run)
            created.append(launcher)
    else:
        for name in ("lets_cook", "letscook"):
            launcher = bin_dir / name
            content = (
                "#!/usr/bin/env sh\n"
                f"\"{python_exe}\" \"{entry}\" \"$@\"\n"
            )
            _write_text(launcher, content, dry_run)
            if not dry_run:
                launcher.chmod(0o755)
            created.append(launcher)

    return created


def _normalize_path_parts(value: str, sep: str) -> list[str]:
    return [p.strip() for p in value.split(sep) if p.strip()]


def _contains_path(path_value: str, target: Path, sep: str, casefold: bool) -> bool:
    target_str = str(target)
    target_cmp = target_str.casefold() if casefold else target_str
    for part in _normalize_path_parts(path_value, sep):
        part_cmp = part.casefold() if casefold else part
        if part_cmp == target_cmp:
            return True
    return False


def _update_windows_user_path(bin_dir: Path, dry_run: bool) -> tuple[bool, str]:
    import winreg

    key_path = r"Environment"
    read_access = winreg.KEY_READ
    write_access = winreg.KEY_READ | winreg.KEY_SET_VALUE
    access = read_access if dry_run else write_access

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            key_path,
            0,
            access,
        ) as key:
            try:
                current, reg_type = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                current, reg_type = "", winreg.REG_EXPAND_SZ

            current = current or ""
            if _contains_path(current, bin_dir, ";", casefold=True):
                return False, "PATH already contains install directory."

            new_value = f"{current};{bin_dir}" if current else str(bin_dir)
            if not dry_run:
                winreg.SetValueEx(key, "Path", 0, reg_type, new_value)
    except PermissionError:
        return False, "Could not update user PATH automatically (permission denied)."

    # Broadcast environment change so new terminals pick it up.
    if not dry_run:
        try:
            import ctypes

            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x001A
            SMTO_ABORTIFHUNG = 0x0002
            ctypes.windll.user32.SendMessageTimeoutW(
                HWND_BROADCAST,
                WM_SETTINGCHANGE,
                0,
                "Environment",
                SMTO_ABORTIFHUNG,
                5000,
                0,
            )
        except Exception:
            pass

    return True, "Added install directory to user PATH."


def _pick_shell_rc() -> Path:
    home = Path.home()
    shell = Path(os.environ.get("SHELL", "")).name

    if shell == "zsh":
        candidates = [home / ".zshrc", home / ".profile"]
    elif shell == "bash":
        candidates = [home / ".bashrc", home / ".profile"]
    else:
        candidates = [home / ".profile", home / ".bashrc", home / ".zshrc"]

    for rc in candidates:
        if rc.exists():
            return rc
    return candidates[0]


def _update_posix_path(bin_dir: Path, dry_run: bool) -> tuple[bool, str]:
    export_line = 'export PATH="$HOME/.letscook/bin:$PATH"'
    rc_file = _pick_shell_rc()

    if rc_file.exists():
        content = rc_file.read_text(encoding="utf-8")
        if export_line in content:
            return False, f"PATH export already exists in {rc_file}."
    else:
        content = ""

    if not dry_run:
        rc_file.parent.mkdir(parents=True, exist_ok=True)
        if content and not content.endswith("\n"):
            content += "\n"
        content += f"\n# Let's Cook\n{export_line}\n"
        rc_file.write_text(content, encoding="utf-8", newline="\n")

    return True, f"Added PATH export to {rc_file}."


def _update_path(bin_dir: Path, dry_run: bool) -> tuple[bool, str]:
    if os.name == "nt":
        return _update_windows_user_path(bin_dir, dry_run)
    return _update_posix_path(bin_dir, dry_run)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Let's Cook global command.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without changing files or PATH.",
    )
    args = parser.parse_args()

    system = platform.system()
    root = _repo_root()
    bin_dir = _bin_dir()
    entry = _entrypoint()
    python_exe = Path(sys.executable).resolve()

    if not entry.exists():
        print(f"[ERROR] Entry point not found: {entry}")
        return 1

    print(f"[INFO] OS: {system}")
    print(f"[INFO] Repo: {root}")
    print(f"[INFO] Python: {python_exe}")
    print(f"[INFO] Install dir: {bin_dir}")
    if args.dry_run:
        print("[INFO] Dry run mode enabled.")

    created = _install_launchers(bin_dir, entry, python_exe, args.dry_run)
    changed, msg = _update_path(bin_dir, args.dry_run)

    print("\n[OK] Launchers:")
    for item in created:
        print(f"  - {item}")

    print(f"[OK] PATH: {msg}")

    print("\nNext step:")
    if os.name == "nt":
        print("  - Open a NEW terminal and run: lets_cook --help")
    else:
        print("  - Open a NEW terminal (or run: source ~/.profile) and run: lets_cook --help")

    if args.dry_run and changed:
        print("  - Re-run without --dry-run to apply changes.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
