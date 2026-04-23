"""Web entry point. The real Flask app lives in `app.web`."""
from app.web import create_app

app = create_app()


if __name__ == "__main__":
    app.run(
        debug=app.config["DEBUG"],
        host=app.config["HOST"],
        port=app.config["PORT"],
    )
