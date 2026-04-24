import threading
import uuid

from app import baseMap, statePoint
from app.database import db
from app.hero import Hero


class GameSession:
    def __init__(self, player_name, speed_level):
        self.id = str(uuid.uuid4())
        self.player_name = player_name
        self.speed_level = speed_level
        self.best_score = 0
        self.scores = []
        self.current_game = None
        self.is_active = False
        self.is_bot_demo = False
        self.bot_function = None
        self.move_count = 0
        # Flask runs requests in parallel threads by default. The client's
        # setInterval polling on /bot_move can fire a second request before
        # the previous one returns, letting two threads mutate the same
        # hero/grid concurrently — which causes the bot to step onto a
        # spike whose trail was laid by a sibling request. Serialize all
        # state-mutating operations on this session.
        self._move_lock = threading.Lock()

        if not hasattr(self, 'is_test_bot'):
            self.is_test_bot = False

        self.all_scores = [10000, 6000, 3000, 1000]
        self.all_names = ["Pro(Computer)", "Advance(Computer)", "Intermediate(Computer)", "Novice(Computer)"]

    def start_new_game(self):
        rage, point, eated, sp = statePoint()
        map_data = baseMap()
        hero = Hero(map_data)

        speed_values = [0.1, 0.05, 0.01, 0.005, 0.002, 0.001]
        speed = speed_values[min(self.speed_level, len(speed_values) - 1)]

        self.move_count = 0

        self.current_game = {
            'hero': hero,
            'rage': rage,
            'point': point,
            'eated': eated,
            'sp': sp,
            'speed': speed,
            'game_over': False,
            'map_data': map_data
        }
        self.is_active = True
        return self.current_game

    def make_move(self, move):
        with self._move_lock:
            return self._make_move_locked(move)

    def _make_move_locked(self, move):
        if not self.is_active or not self.current_game or self.current_game['game_over']:
            return {'success': False, 'message': 'No active game'}

        game = self.current_game
        hero = game['hero']

        if move and move in ['w', 'a', 's', 'd']:
            hero.setMove(move)

        safety, is_eat = hero.moveWithAutoDirection()

        if hero.hasMove():
            self.move_count += 1

        if hero.hasMove():
            if game['rage'] != 0:
                game['rage'] -= 1

            if game['sp'] != 0:
                game['sp'] -= 1

        if not safety or game['sp'] <= 0:
            game['game_over'] = True
            self.is_active = False
            final_score = game['point']

            if final_score > self.best_score:
                self.best_score = final_score

            moves = getattr(self, 'move_count', 0)
            score_type = 'bot' if self.is_bot_demo else 'normal'

            print(f"DEBUG: Game over - Player: {self.player_name}, Score: {final_score}, Type: {score_type}")
            print(f"DEBUG: Is bot demo: {self.is_bot_demo}, Is test bot: {self.is_test_bot}")

            if not self.is_test_bot:
                print("DEBUG: Saving to database...")
                result = db.save_score(
                    points=final_score,
                    rages=game['rage'],
                    spikes=len([cell for row in hero.getMap() for cell in row if cell == '*']),
                    eaten=game['eated'],
                    moves=moves,
                    time=game['sp'],
                    name=self.player_name,
                    score_type=score_type
                )
                print(f"DEBUG: Database save result: {result}")
            else:
                print("DEBUG: Skipping database save for test bot from bot builder")

            self.scores.append(final_score)
            self.all_scores.append(final_score)
            self.all_names.append(self.player_name)

            return {
                'success': True,
                'game_over': True,
                'final_score': final_score,
                'map': self.get_map_as_string(hero.getMap()),
                'game_state': self.get_game_state()
            }

        if is_eat:
            game['point'] += 20
            game['point'] += game['rage'] + game['sp']
            game['rage'] = 50
            if game['eated'] % 9 == 0:
                game['sp'] += 200
            if (sum(game['map_data'], []).count('*') - 116) % 4 == 0:
                game['sp'] += 50
            game['eated'] += 1
            hero.dropRandomDollar()

        return {
            'success': True,
            'game_over': False,
            'map': self.get_map_as_string(hero.getMap()),
            'game_state': self.get_game_state()
        }

    def get_game_state(self):
        if not self.current_game:
            return None

        game = self.current_game
        hero = game['hero']
        y_dollar, x_dollar = hero.getLocationDollar()

        return {
            'point': game['point'],
            'rage': game['rage'],
            'sp': game['sp'],
            'eated': game['eated'],
            'spike_count': sum(game['map_data'], []).count('*') - 116,
            'dollar_location': {'x': x_dollar, 'y': y_dollar},
            'best_score': self.best_score,
            'game_over': game['game_over']
        }

    def get_map_as_string(self, map_data):
        result = []
        for row in map_data:
            result.append(''.join(row))
        return result

    def get_leaderboard(self):
        combined = list(zip(self.all_scores, self.all_names))
        sorted_scores = sorted(combined, key=lambda x: x[0], reverse=True)
        return [{'score': score, 'name': name, 'rank': i + 1}
                for i, (score, name) in enumerate(sorted_scores)]

    def start_bot_demo(self, bot_name, bot_function):
        rage, point, eated, sp = statePoint()
        map_data = baseMap()
        hero = Hero(map_data)

        self.move_count = 0

        speed_values = [0.1, 0.05, 0.01]
        speed = speed_values[1]

        self.current_game = {
            'hero': hero,
            'rage': rage,
            'point': point,
            'eated': eated,
            'sp': sp,
            'speed': speed,
            'game_over': False,
            'map_data': map_data
        }
        self.is_active = True
        self.is_bot_demo = True
        self.bot_function = bot_function
        self.player_name = bot_name
        print(f"DEBUG: start_bot_demo - is_test_bot preserved: {getattr(self, 'is_test_bot', 'NOT_SET')}")
        return self.current_game

    def make_bot_move(self):
        with self._move_lock:
            return self._make_bot_move_locked()

    def _make_bot_move_locked(self):
        if not self.is_active or not self.current_game or self.current_game['game_over'] or not self.is_bot_demo:
            return {'success': False, 'message': 'No active bot demo'}

        game = self.current_game
        hero = game['hero']

        try:
            move = self.bot_function(hero)
            if move and move in ['w', 'a', 's', 'd']:
                hero.setMove(move)

            safety, is_eat = hero.moveWithAutoDirection()

            if hero.hasMove():
                self.move_count += 1

                if game['rage'] != 0:
                    game['rage'] -= 1

                if game['sp'] != 0:
                    game['sp'] -= 1

            if not safety or game['sp'] <= 0:
                game['game_over'] = True
                self.is_active = False
                final_score = game['point']

                moves = getattr(self, 'move_count', 0)
                print(f"DEBUG: Bot demo finished - {self.player_name} scored {final_score}")
                print(f"DEBUG: Is test bot: {self.is_test_bot}")

                if not self.is_test_bot:
                    print(f"DEBUG: Saving score for {self.player_name} (bot) with {final_score} points")
                    result = db.save_score(
                        points=final_score,
                        rages=game['rage'],
                        spikes=len([cell for row in hero.getMap() for cell in row if cell == '*']),
                        eaten=game['eated'],
                        moves=moves,
                        time=game['sp'],
                        name=self.player_name,
                        score_type='bot'
                    )
                    print(f"DEBUG: Bot demo database save result: {result}")
                else:
                    print(f"DEBUG: Skipping database save for test bot: {self.player_name}")

                return {
                    'success': True,
                    'game_over': True,
                    'final_score': final_score,
                    'map': self.get_map_as_string(hero.getMap()),
                    'game_state': self.get_game_state()
                }

            if is_eat:
                game['point'] += 20
                game['point'] += game['rage'] + game['sp']
                game['rage'] = 50
                if game['eated'] % 9 == 0:
                    game['sp'] += 200
                if (sum(game['map_data'], []).count('*') - 116) % 4 == 0:
                    game['sp'] += 50
                game['eated'] += 1
                hero.dropRandomDollar()

            return {
                'success': True,
                'game_over': False,
                'map': self.get_map_as_string(hero.getMap()),
                'game_state': self.get_game_state(),
                'last_move': move
            }

        except Exception as e:
            return {'success': False, 'message': f'Bot move error: {str(e)}'}
