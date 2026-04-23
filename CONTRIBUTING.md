# Contributing

Thanks for wanting to contribute to Hello-Balloons.

## Local setup

```bash
git clone https://github.com/Bejjoeqq/Hello-Balloons.git
cd Hello-Balloons

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements-dev.txt
cp .env.example .env
```

Run the web app:

```bash
python web_app.py
```

Run the CLI:

```bash
python main.py
```

## Workflow

1. Fork the repo and create a feature branch:
   ```bash
   git checkout -b feature/<short-description>
   ```
2. Make your change. Keep PRs focused — one concern per PR.
3. Run the linter before committing:
   ```bash
   ruff check .
   ```
4. Push and open a pull request against `master`. Describe the *why* in the PR body.

## Adding a bot

1. Copy `app/bot/template.py` → `app/bot/<your_bot>.py`
2. Set a unique `NAME` and implement `checkBot(hero)` — it must return `'w'`, `'a'`, `'s'`, or `'d'`
3. Restart the server; the bot is auto-discovered by `app/bot/__init__.py`
4. Verify it shows up at `/bot_demo`

See the *Bot API* section of the README for the available `Hero` methods.

## Code style

- Python 3.8+ compatible
- `ruff check .` must pass (config lives in `pyproject.toml`)
- Prefer small, readable functions over cleverness
- Don't commit `game_scores.db`, `.env`, or `.venv/` — they're in `.gitignore` for a reason

## Reporting bugs / requesting features

Open an issue on GitHub with:
- What you expected
- What actually happened
- Steps to reproduce
- Browser + OS for web issues
