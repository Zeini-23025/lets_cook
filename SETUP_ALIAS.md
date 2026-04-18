# Let's Cook — Alias Setup Guide

## 1. Prerequisites

- Python 3.7+ installed and on your PATH (`python --version` to check)
- The script lives at a stable path — move it somewhere permanent first, e.g.:
  - **Windows:** `C:\tools\lets_cook.py`
  - **Linux/macOS:** `~/tools/lets_cook.py`

---

## 2. Windows — PowerShell alias

Open your PowerShell profile file:

```powershell
notepad $PROFILE
```

> If the file doesn't exist yet, run:
> `New-Item -ItemType File -Path $PROFILE -Force`

Add this line (adjust the path to wherever you put the script):

```powershell
function lets_cook { python "C:\tools\lets_cook.py" @args }
```

Save, then reload your profile:

```powershell
. $PROFILE
```

Now just type:

```powershell
lets_cook           # launch workspace
lets_cook --setup   # re-run wizard
```

---

## 3. Linux / macOS — Bash or Zsh alias

Open your shell config:

```bash
# Bash
nano ~/.bashrc

# Zsh
nano ~/.zshrc
```

Add this line (adjust the path):

```bash
alias lets_cook='python3 ~/tools/lets_cook.py'
```

Reload:

```bash
source ~/.bashrc   # or ~/.zshrc
```

Now just type:

```bash
lets_cook           # launch workspace
lets_cook --setup   # re-run wizard
```

---

## 4. Bonus — make it executable on Linux (skip `python3` prefix)

```bash
chmod +x ~/tools/lets_cook.py
```

Make sure the first line of the script is:
```
#!/usr/bin/env python3
```
(it already is)

Then update your alias:

```bash
alias lets_cook='~/tools/lets_cook.py'
```

Or add `~/tools` to your PATH instead of using an alias:

```bash
export PATH="$HOME/tools:$PATH"
```

---

## 5. First-run flow

```
$ lets_cook
╔═══════════════════════════════════════════╗
║          LET'S COOK  - v1.0               ║
╚═══════════════════════════════════════════╝

  No config found. Let's set things up first!

  Welcome to the Let's Cook setup wizard!
  ...
```

Config is saved to `~/.letscook/config.json` — edit it by hand anytime,
or re-run `lets_cook --setup` to go through the wizard again.
