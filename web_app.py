from flask import Flask, render_template, request, jsonify, session
import uuid
import json
from app.hero import Hero
from app.guide import header
from app import statePoint, baseMap
from app.bot import getBot
import threading
import time

app = Flask(__name__)
app.secret_key = 'balloon_game_secret_key'

# Global game sessions storage
game_sessions = {}

# Global custom bots storage
custom_bots = {}

def get_all_bots():
    """Get all bots including custom ones"""
    # Get built-in bots
    built_in_bots = getBot()
    
    # Combine with custom bots
    all_bots = built_in_bots.copy()
    all_bots.update(custom_bots)
    
    return all_bots

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
        
        # Leaderboard data
        self.all_scores = [10000, 6000, 3000, 1000]
        self.all_names = ["Pro(Computer)", "Advance(Computer)", "Intermediate(Computer)", "Novice(Computer)"]
    
    def start_new_game(self):
        rage, point, eated, sp = statePoint()
        map_data = baseMap()
        hero = Hero(map_data)
        
        speed_values = [0.1, 0.05, 0.01, 0.005, 0.002, 0.001]  # Slow, Normal, Fast, Insane, Lightning, Godspeed
        speed = speed_values[min(self.speed_level, len(speed_values) - 1)]
        
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
        if not self.is_active or not self.current_game or self.current_game['game_over']:
            return {'success': False, 'message': 'No active game'}
        
        game = self.current_game
        hero = game['hero']
        
        # Set new direction if a valid move is provided
        if move and move in ['w', 'a', 's', 'd']:
            hero.setMove(move)
        
        # Always try to move (will use current direction or no movement)
        safety, is_eat = hero.moveWithAutoDirection()
        
        # Update game state only if there was actual movement
        if hero.hasMove():
            if game['rage'] != 0:
                game['rage'] -= 1
            
            if game['sp'] != 0:
                game['sp'] -= 1
        
        if not safety or game['sp'] <= 0:
            # Game over
            game['game_over'] = True
            self.is_active = False
            final_score = game['point']
            
            if final_score > self.best_score:
                self.best_score = final_score
            
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
        return [{'score': score, 'name': name, 'rank': i+1} 
                for i, (score, name) in enumerate(sorted_scores)]
    
    def start_bot_demo(self, bot_name, bot_function):
        """Start a bot demo game"""
        rage, point, eated, sp = statePoint()
        map_data = baseMap()
        hero = Hero(map_data)
        
        speed_values = [0.1, 0.05, 0.01]
        speed = speed_values[1]  # Use normal speed for demo
        
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
        return self.current_game
    
    def make_bot_move(self):
        """Make automatic bot move"""
        if not self.is_active or not self.current_game or self.current_game['game_over'] or not self.is_bot_demo:
            return {'success': False, 'message': 'No active bot demo'}
        
        game = self.current_game
        hero = game['hero']
        
        try:
            # Get bot move
            move = self.bot_function(hero)
            if move and move in ['w', 'a', 's', 'd']:
                hero.setMove(move)
            
            # Always try to move
            safety, is_eat = hero.moveWithAutoDirection()
            
            # Update game state only if there was actual movement
            if hero.hasMove():
                if game['rage'] != 0:
                    game['rage'] -= 1
                
                if game['sp'] != 0:
                    game['sp'] -= 1
            
            if not safety or game['sp'] <= 0:
                # Game over
                game['game_over'] = True
                self.is_active = False
                final_score = game['point']
                
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game')
def game():
    return render_template('game.html')

@app.route('/bot_demo')
def bot_demo():
    return render_template('bot_demo.html')

@app.route('/bot_builder')
def bot_builder():
    return render_template('bot_builder.html')

@app.route('/get_bots', methods=['GET'])
def get_bots():
    """Get list of available bots"""
    try:
        bot_menu = get_all_bots()
        bot_list = []
        
        for bot_key, bot_data in bot_menu.items():
            if 'name' in bot_data and 'func' in bot_data:
                bot_list.append({
                    'key': bot_key,
                    'name': bot_data['name'],
                    'display_name': f"{bot_data['name']} ({bot_key})",
                    'type': 'builtin'
                })
        
        # Get custom bots
        custom_list = []
        for bot_key, bot_data in custom_bots.items():
            if 'name' in bot_data and 'func' in bot_data:
                custom_list.append({
                    'key': bot_key,
                    'name': bot_data['name'],
                    'display_name': f"{bot_data['name']} (Custom)",
                    'type': 'custom'
                })
        
        return jsonify({
            'success': True, 
            'builtin_bots': bot_list,
            'custom_bots': custom_list,
            'bots': bot_list + custom_list  # For backward compatibility
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting bots: {str(e)}'})

@app.route('/start_game', methods=['POST'])
def start_game():
    data = request.json
    player_name = data.get('player_name', 'Anonymous')
    speed_level = data.get('speed_level', 1)  # 0=slow, 1=normal, 2=fast
    
    # Create new game session
    game_session = GameSession(player_name, speed_level)
    session_id = game_session.id
    game_sessions[session_id] = game_session
    
    # Store session ID in Flask session
    session['game_session_id'] = session_id
    
    # Start the game
    game_data = game_session.start_new_game()
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'map': game_session.get_map_as_string(game_data['hero'].getMap()),
        'game_state': game_session.get_game_state()
    })

@app.route('/make_move', methods=['POST'])
def make_move():
    session_id = session.get('game_session_id')
    if not session_id or session_id not in game_sessions:
        return jsonify({'success': False, 'message': 'No active game session'})
    
    data = request.json
    move = data.get('move')
    
    if move and move not in ['w', 'a', 's', 'd']:
        return jsonify({'success': False, 'message': 'Invalid move'})
    
    game_session = game_sessions[session_id]
    result = game_session.make_move(move)
    
    return jsonify(result)

@app.route('/auto_move', methods=['POST'])
def auto_move():
    """Continue movement in current direction without new input"""
    session_id = session.get('game_session_id')
    if not session_id or session_id not in game_sessions:
        return jsonify({'success': False, 'message': 'No active game session'})
    
    game_session = game_sessions[session_id]
    # Call make_move with None to continue in current direction
    result = game_session.make_move(None)
    
    return jsonify(result)

@app.route('/get_game_state', methods=['GET'])
def get_game_state():
    session_id = session.get('game_session_id')
    if not session_id or session_id not in game_sessions:
        return jsonify({'success': False, 'message': 'No active game session'})
    
    game_session = game_sessions[session_id]
    game_state = game_session.get_game_state()
    
    if game_state and game_session.current_game:
        # Also return current map and speed
        hero = game_session.current_game['hero']
        speed = game_session.current_game['speed']
        return jsonify({
            'success': True, 
            'game_state': game_state,
            'map': game_session.get_map_as_string(hero.getMap()),
            'speed': speed,
            'player_name': game_session.player_name,
            'session_id': session_id
        })
    else:
        return jsonify({'success': False, 'message': 'No active game'})

@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    session_id = session.get('game_session_id')
    if not session_id or session_id not in game_sessions:
        # Return default leaderboard
        default_scores = [10000, 6000, 3000, 1000]
        default_names = ["Pro(Computer)", "Advance(Computer)", "Intermediate(Computer)", "Novice(Computer)"]
        combined = list(zip(default_scores, default_names))
        sorted_scores = sorted(combined, key=lambda x: x[0], reverse=True)
        leaderboard_data = [{'score': score, 'name': name, 'rank': i+1} 
                           for i, (score, name) in enumerate(sorted_scores)]
    else:
        game_session = game_sessions[session_id]
        leaderboard_data = game_session.get_leaderboard()
    
    return jsonify({'success': True, 'leaderboard': leaderboard_data})

@app.route('/recent_scores', methods=['GET'])
def recent_scores():
    session_id = session.get('game_session_id')
    if not session_id or session_id not in game_sessions:
        return jsonify({'success': False, 'message': 'No active game session'})
    
    game_session = game_sessions[session_id]
    return jsonify({
        'success': True, 
        'scores': game_session.scores,
        'player_name': game_session.player_name
    })

@app.route('/start_bot_demo', methods=['POST'])
def start_bot_demo():
    """Start a new bot demo session"""
    try:
        data = request.json
        selected_bot_key = data.get('bot_key') if data else None
        speed_level = data.get('speed_level', 3)  # Default to Insane (index 3)
        
        # Get available bots
        bot_menu = get_all_bots()
        bot_list = list(bot_menu)
        
        if not bot_list:
            return jsonify({'success': False, 'message': 'No bots available'})
        
        # Use selected bot or first available bot
        if selected_bot_key and selected_bot_key in bot_menu:
            selected_bot = bot_menu[selected_bot_key]
            bot_key = selected_bot_key
        else:
            bot_key = bot_list[0]
            selected_bot = bot_menu[bot_key]
            
        bot_name = selected_bot["name"]
        bot_func = selected_bot["func"]
        
        # Create new bot demo session with selected speed
        game_session = GameSession(bot_name, speed_level)
        session_id = game_session.id
        game_sessions[session_id] = game_session
        
        # Store session ID in Flask session
        session['game_session_id'] = session_id
        
        # Start the bot demo
        game_data = game_session.start_bot_demo(bot_name, bot_func)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'bot_name': bot_name,
            'bot_key': bot_key,
            'map': game_session.get_map_as_string(game_data['hero'].getMap()),
            'game_state': game_session.get_game_state()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Bot demo start error: {str(e)}'})

@app.route('/bot_move', methods=['POST'])
def bot_move():
    """Make a bot move in the current demo"""
    session_id = session.get('game_session_id')
    if not session_id or session_id not in game_sessions:
        return jsonify({'success': False, 'message': 'No active bot demo session'})
    
    game_session = game_sessions[session_id]
    if not game_session.is_bot_demo:
        return jsonify({'success': False, 'message': 'Not a bot demo session'})
    
    result = game_session.make_bot_move()
    return jsonify(result)

@app.route('/validate_custom_bot', methods=['POST'])
def validate_custom_bot():
    """Validate user's custom bot code"""
    try:
        data = request.json
        code = data.get('code', '')
        bot_name = data.get('bot_name', 'CustomBot')
        
        if not code.strip():
            return jsonify({'success': False, 'message': 'Code cannot be empty'})
        
        # Basic validation
        if 'def checkBot(' not in code:
            return jsonify({'success': False, 'message': 'Missing required function: def checkBot(hero)'})
        
        if 'return ' not in code:
            return jsonify({'success': False, 'message': 'Function must return a move (w, a, s, d)'})
        
        # Try to compile the code
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            return jsonify({'success': False, 'message': f'Syntax Error: {str(e)}'})
        
        return jsonify({'success': True, 'message': 'Code validation passed'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Validation error: {str(e)}'})

@app.route('/save_custom_bot', methods=['POST'])
def save_custom_bot():
    """Save custom bot to global storage"""
    try:
        data = request.json
        bot_name = data.get('bot_name', 'CustomBot').strip()
        code = data.get('code', '')
        
        if not bot_name:
            return jsonify({'success': False, 'message': 'Bot name is required'})
        
        if not code.strip():
            return jsonify({'success': False, 'message': 'Bot code is required'})
        
        # Validate code first
        if 'def checkBot(' not in code:
            return jsonify({'success': False, 'message': 'Missing required function: def checkBot(hero)'})
        
        try:
            # Create bot function
            custom_globals = {}
            exec(code, custom_globals)
            
            if 'checkBot' not in custom_globals:
                return jsonify({'success': False, 'message': 'Function checkBot not found after execution'})
            
            custom_bot_func = custom_globals['checkBot']
            
            # Use fixed key for custom bot (only allow one custom bot)
            bot_key = "custom_bot_builder"
            
            # Save to global custom_bots storage (overwrite if exists)
            custom_bots[bot_key] = {
                'name': bot_name,
                'func': custom_bot_func,
                'code': code,
                'type': 'custom'
            }
            
            return jsonify({
                'success': True, 
                'message': f'Bot "{bot_name}" saved successfully! ',
                'bot_key': bot_key
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Bot execution error: {str(e)}'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Save error: {str(e)}'})

@app.route('/start_custom_bot_demo', methods=['POST'])
def start_custom_bot_demo():
    """Start demo with user's custom bot"""
    try:
        data = request.json
        code = data.get('code', '')
        bot_name = data.get('bot_name', 'CustomBot')
        speed_level = data.get('speed_level', 3)  # Default to Insane
        
        if not code.strip():
            return jsonify({'success': False, 'message': 'Code cannot be empty'})
        
        # Create custom bot function
        try:
            # Create a safe execution environment
            custom_globals = {
                '__builtins__': {
                    'abs': abs,
                    'max': max,
                    'min': min,
                    'len': len,
                    'range': range,
                    'int': int,
                    'float': float,
                    'str': str,
                    'bool': bool,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'sum': sum,
                    'sorted': sorted,
                    'enumerate': enumerate,
                    'zip': zip,
                },
                'random': __import__('random')
            }
            
            # Execute the code
            exec(code, custom_globals)
            
            # Get the checkBot function
            if 'checkBot' not in custom_globals:
                return jsonify({'success': False, 'message': 'Function checkBot not found'})
            
            custom_bot_func = custom_globals['checkBot']
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Code execution error: {str(e)}'})
        
        # Create new custom bot demo session with selected speed
        game_session = GameSession(bot_name, speed_level)
        session_id = game_session.id
        game_sessions[session_id] = game_session
        
        # Store session ID in Flask session
        session['game_session_id'] = session_id
        
        # Start the custom bot demo
        game_data = game_session.start_bot_demo(bot_name, custom_bot_func)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'bot_name': bot_name,
            'map': game_session.get_map_as_string(game_data['hero'].getMap()),
            'game_state': game_session.get_game_state()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Custom bot demo error: {str(e)}'})

@app.route('/custom_bot_move', methods=['POST'])
def custom_bot_move():
    """Make a move with custom bot"""
    session_id = session.get('game_session_id')
    if not session_id or session_id not in game_sessions:
        return jsonify({'success': False, 'message': 'No active custom bot session'})
    
    game_session = game_sessions[session_id]
    if not game_session.is_bot_demo:
        return jsonify({'success': False, 'message': 'Not a bot demo session'})
    
    result = game_session.make_bot_move()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)