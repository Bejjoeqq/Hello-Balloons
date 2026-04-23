import os
import secrets
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class Config:
    SECRET_KEY: str
    DEBUG: bool
    HOST: str
    PORT: int
    ADMIN_PIN: str
    DATABASE_PATH: str

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            SECRET_KEY=os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32),
            DEBUG=os.getenv("FLASK_DEBUG", "0") == "1",
            HOST=os.getenv("FLASK_HOST", "127.0.0.1"),
            PORT=int(os.getenv("FLASK_PORT", "5000")),
            ADMIN_PIN=os.getenv("ADMIN_PIN", "000000"),
            DATABASE_PATH=os.getenv("DATABASE_PATH", "game_scores.db"),
        )
