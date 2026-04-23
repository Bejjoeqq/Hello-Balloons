from app.bot import getBot

game_sessions: dict = {}
custom_bots: dict = {}


def get_all_bots() -> dict:
    all_bots = getBot().copy()
    all_bots.update(custom_bots)
    return all_bots
