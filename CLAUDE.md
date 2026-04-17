# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Dope Wars — a remake of the classic TI-83 calculator drug dealing game. The player travels between locations, buys and sells goods at fluctuating prices, manages inventory and debt, and tries to maximize profit before time runs out.

## Repository

This is a plaibox sandbox project. The `.plaibox.yaml` file is project metadata for the plaibox system — do not modify it.

## Running

```bash
python3 dopewars.py
```

### PWA (web version)

```bash
cd web && python3 -m http.server 8000
```

Open `http://localhost:8000` on your phone (same network) or desktop browser. On mobile, use "Add to Home Screen" to install as an app.

## Testing

```bash
.venv/bin/python -m pytest test_dopewars.py -v          # all tests
.venv/bin/python -m pytest test_dopewars.py -v -k "buy" # single test by keyword
```

## Architecture

Single-file game (`dopewars.py`). Game logic functions are pure (take `GameState`, return errors or mutate state). Display and input functions handle I/O. The main loop ties them together.

Key pattern: logic functions return `str | None` — `None` means success, a string is an error message to display.
