# Let's Cook

Launch your full dev workspace in one command.

`Let's Cook` is a cross-platform (Windows/Linux) workspace launcher that can:
- start selected desktop apps
- open URLs
- save and reuse your setup from config

## Features

- Interactive setup wizard (`--setup`)
- App library with install detection
- Searchable terminal picker (arrow keys + space select)
- App enable/disable editing
- URL management
- Launch delay control
- Modular codebase (`letscook/` package)

## Requirements

- Python 3.10+
- Windows or Linux terminal

## Quick Start

Run directly:

```bash
python lets_cook.py --setup
python lets_cook.py
```

Or module mode:

```bash
python -m letscook --setup
python -m letscook
```

## Commands

```text
lets_cook            launch configured workspace
lets_cook --setup    full setup wizard
lets_cook --add      add apps or URLs
lets_cook --edit     edit/toggle configured apps and URLs
lets_cook --remove   remove apps or URLs
lets_cook --list     show current config
lets_cook --help     show help
```

## Config

Default config path:

```text
~/.letscook/config.json
```

Example:

```json
{
  "apps": [
    {
      "name": "VS Code",
      "cat": "Editors & IDEs",
      "enabled": true,
      "command": "code",
      "args": []
    }
  ],
  "urls": [
    "https://github.com"
  ],
  "delay": 1.5
}
```

## Project Structure

```text
lets_cook.py              # thin entrypoint
letscook/
  cli.py                  # argument flow + command routing
  constants.py            # banner/help/constants
  library.py              # built-in app catalog
  install_detection.py    # installed app checks
  picker.py               # interactive TUI app picker
  setup_wizard.py         # setup flow
  commands.py             # add/edit/remove/list
  launcher.py             # launch apps + open URLs
  config_io.py            # load/save config
  ui.py                   # terminal styling + prompts
  __main__.py             # python -m letscook
```

## One-Script Global Install (All Systems)

Use this if you want `lets_cook` available from anywhere in your system:

```bash
python install_global.py
```

Dry-run preview:

```bash
python install_global.py --dry-run
```

What it does:
- creates launcher commands in `~/.letscook/bin`
- adds that directory to your user PATH
- supports Windows, Linux, and macOS
