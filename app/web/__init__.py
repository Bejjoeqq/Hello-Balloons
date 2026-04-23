from pathlib import Path

from flask import Flask

from .config import Config
from .routes import bp

_REPO_ROOT = Path(__file__).resolve().parents[2]
_TEMPLATES = _REPO_ROOT / "templates"


def create_app(config: Config | None = None) -> Flask:
    app = Flask("hello_balloons", template_folder=str(_TEMPLATES))
    cfg = config or Config.from_env()
    app.config.from_object(cfg)
    app.secret_key = cfg.SECRET_KEY
    app.register_blueprint(bp)
    return app


__all__ = ["create_app", "Config"]
