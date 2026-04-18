"""Core constants for Let's Cook."""

from pathlib import Path
import platform

VERSION     = "2.1"
CONFIG_DIR  = Path.home() / ".letscook"
CONFIG_FILE = CONFIG_DIR / "config.json"
IS_WINDOWS  = platform.system() == "Windows"
OS_KEY      = "windows" if IS_WINDOWS else "linux"
OS_LABEL    = "Windows" if IS_WINDOWS else "Linux"

BANNER = f"""
╔═══════════════════════════════════════════════╗
║        LET'S COOK  v{VERSION}  -  Workspace        ║
║      Fire up your entire stack at once        ║
╚═══════════════════════════════════════════════╝"""

HELP_TEXT = """
  Usage:
    lets_cook            — launch your configured workspace
    lets_cook --setup    — full setup wizard (reconfigure everything)
    lets_cook --add      — add new apps or URLs
    lets_cook --edit     — toggle apps on/off or edit commands
    lets_cook --remove   — remove apps or URLs
    lets_cook --list     — show current configuration
    lets_cook --help     — show this help
"""
