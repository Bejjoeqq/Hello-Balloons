# Hello-Balloons — Balloon Game

A balloon navigation game where you collect dollars while avoiding spikes. Ships with two interfaces: a **Flask web app** (primary) and a **terminal CLI** (legacy). Comes with a plug-in bot system and an in-browser bot builder.

![Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3-green)
![License](https://img.shields.io/badge/License-MIT-blue)

## Overview

Navigate your balloon (`O`) to collect dollars (`$`) while avoiding spikes (`*`). Each dollar you collect spawns a new spike at the old dollar location — the map gets progressively deadlier.

### Features

- **Web UI** — play in the browser, no install on the client side
- **Bot demos** — watch a gallery of pre-built AI algorithms play
- **Bot builder** — write and run your own `checkBot(hero)` in-browser
- **Server-side leaderboard** — scores persisted in SQLite (`game_scores.db`)
- **Admin panel** — PIN-gated view over the raw scores table
- **CLI mode** — terminal version with menu-driven play

## Quick start

### Prerequisites

- Python 3.8+
- Git

### Install

```bash
git clone https://github.com/Bejjoeqq/Hello-Balloons.git
cd Hello-Balloons

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env              # then edit the values you care about
```

### Run (web mode — recommended)

```bash
python web_app.py
```

Open `http://127.0.0.1:5000` in a browser. The SQLite database is created automatically on first launch.

> Default host is `127.0.0.1`. To expose on your LAN, set `FLASK_HOST=0.0.0.0` in `.env`.

### Run (CLI mode)

```bash
python main.py
```

Terminal menu for Play / Leaderboard / Bot demo / Exit. Keyboard input is implemented for Windows (`msvcrt`); on Linux/macOS the arrow-key handler is not wired up — use the web mode instead.

## Configuration

All runtime config is read from environment variables (see `.env.example`):

| Variable            | Default              | Purpose                                                     |
| ------------------- | -------------------- | ----------------------------------------------------------- |
| `FLASK_SECRET_KEY`  | random per boot      | Flask session signing key. Set explicitly in production.    |
| `FLASK_DEBUG`       | `0`                  | `1` enables Flask debug mode (dev only, do not ship).       |
| `FLASK_HOST`        | `127.0.0.1`          | Bind address. `0.0.0.0` exposes on LAN.                     |
| `FLASK_PORT`        | `5000`               | HTTP port.                                                  |
| `ADMIN_PIN`         | `000000`             | PIN required to open the admin panel.                       |
| `DATABASE_PATH`     | `game_scores.db`     | SQLite file location.                                       |

### Admin panel

Navigate to `/admin_panel` and enter `ADMIN_PIN`. The default (`000000`) is suitable for local development only — set a real value via `.env` before exposing the app.

## Gameplay

### Human player

- **W / A / S / D** — move up / left / down / right
- **Goal** — collect `$` while avoiding `*`
- **Catch** — every `$` eaten spawns a new `*` where the dollar was

### Bot demo

Pick a bot from the dropdown and watch it play. Speed is adjustable from *Slow* to *Godspeed*.

### Bot builder

Write a `checkBot(hero)` function in the browser editor, validate, then run. Your bot must return one of `'w' | 'a' | 's' | 'd'`.

## Bot API

```python
NAME = "My Bot"

def checkBot(hero):
    x, y = hero.getLocation()           # balloon position
    ydollar, xdollar = hero.findLocationDollar()   # dollar position
    # ... your logic ...
    return 'w'   # 'w', 'a', 's', or 'd'
```

### Hero methods

| Method                      | Returns                              |
| --------------------------- | ------------------------------------ |
| `hero.getLocation()`        | `[x, y]` balloon position            |
| `hero.findLocationDollar()` | `[y, x]` dollar position             |
| `hero.getMove()`            | current direction                    |
| `hero.getMap()`             | 2D list of map cells                 |

### Built-in bots

All files in `app/bot/` are auto-loaded at start (except `template.py`). Notable ones: `champion_bot`, `perfect_score_bot`, `quantum_neural_bot`, `astar_supreme_bot`, `hybrid_master_bot`.

## Project structure

```
Hello-Balloons/
├── main.py                  # CLI entry shim → app.cli.run()
├── web_app.py               # Web entry shim → app.web.create_app()
├── app/
│   ├── __init__.py          # shared: statePoint(), baseMap()
│   ├── hero.py              # shared: Hero class
│   ├── map.py               # shared: Map class
│   ├── guide.py             # shared: text helpers
│   ├── database.py          # GameDatabase (SQLite) — single DB source
│   ├── bot/                 # bot registry + built-in bot algorithms
│   │   ├── __init__.py      # auto-loader
│   │   ├── template.py      # starter template for new bots
│   │   └── *.py             # built-in bots
│   ├── cli/                 # CLI interface
│   │   ├── __init__.py      # run() — menu loop
│   │   ├── prompt.py        # terminal key reading
│   │   └── start.py         # CLI game loop
│   └── web/                 # Flask interface
│       ├── __init__.py      # create_app() factory
│       ├── config.py        # Config dataclass (env vars)
│       ├── state.py         # in-memory session/custom-bot registries
│       ├── session.py       # GameSession class
│       ├── bot_executor.py  # custom-bot validation + sandboxed exec
│       └── routes.py        # Flask blueprint with all 20 routes
├── templates/               # Flask HTML templates
├── .env.example             # env var reference
├── .gitignore
├── LICENSE                  # MIT
├── CONTRIBUTING.md
├── pyproject.toml           # PEP 621 metadata + ruff config
├── requirements.txt         # runtime deps
└── requirements-dev.txt     # dev deps (ruff, pytest)
```

## Development

```bash
pip install -r requirements-dev.txt
ruff check .                 # lint
```

Run the app locally as described in *Quick start*. The SQLite DB (`game_scores.db`) is created on first import of `app.database`; it is git-ignored.

### Adding a bot

1. Copy `app/bot/template.py` to `app/bot/your_bot.py`
2. Set `NAME = "Your Bot"` and implement `checkBot(hero)`
3. Restart the server — it's auto-registered on import
4. Open `/bot_demo` and pick it from the list

## Data storage

Scores are stored server-side in a local SQLite file (`game_scores.db` by default, overridable via `DATABASE_PATH`). There is **no** browser-local-storage leaderboard. The database file is ignored by git — every checkout starts fresh.

## Roadmap

- Test suite under `tests/` with fixtures for `GameDatabase`
- `.github/workflows/` CI running ruff + pytest
- Type hints / `mypy` pass
- Replace in-memory `game_sessions` dict with Redis (for multi-worker deploys)
- Harden the custom-bot sandbox (restrict imports, add CPU / wall-time limits)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE).

## Acknowledgments

- Project developed with AI-assisted tooling for code generation and documentation
- Game concept inspired by classic navigation puzzles
- Thanks to all contributors and bot authors

## Contact

- **GitHub**: [Bejjoeqq](https://github.com/Bejjoeqq)
- **Repository**: [Hello-Balloons](https://github.com/Bejjoeqq/Hello-Balloons)
