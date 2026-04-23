from flask import Blueprint, current_app, jsonify, render_template, request, session

from app.database import db

from .bot_executor import (
    compile_sandboxed_bot,
    register_custom_bot,
    validate_code,
)
from .session import GameSession
from .state import custom_bots, game_sessions, get_all_bots

bp = Blueprint("game", __name__)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/game')
def game():
    return render_template('game.html')


@bp.route('/bot_demo')
def bot_demo():
    return render_template('bot_demo.html')


@bp.route('/bot_builder')
def bot_builder():
    return render_template('bot_builder.html')


@bp.route('/get_bots', methods=['GET'])
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
            'bots': bot_list + custom_list
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting bots: {str(e)}'})


@bp.route('/start_game', methods=['POST'])
def start_game():
    data = request.json
    player_name = data.get('player_name', 'Anonymous')
    speed_level = data.get('speed_level', 1)

    game_session = GameSession(player_name, speed_level)
    session_id = game_session.id
    game_sessions[session_id] = game_session

    session['game_session_id'] = session_id

    game_data = game_session.start_new_game()

    return jsonify({
        'success': True,
        'session_id': session_id,
        'map': game_session.get_map_as_string(game_data['hero'].getMap()),
        'game_state': game_session.get_game_state()
    })


@bp.route('/make_move', methods=['POST'])
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


@bp.route('/auto_move', methods=['POST'])
def auto_move():
    """Continue movement in current direction without new input"""
    session_id = session.get('game_session_id')
    if not session_id or session_id not in game_sessions:
        return jsonify({'success': False, 'message': 'No active game session'})

    game_session = game_sessions[session_id]
    result = game_session.make_move(None)

    return jsonify(result)


@bp.route('/get_game_state', methods=['GET'])
def get_game_state():
    session_id = session.get('game_session_id')
    if not session_id or session_id not in game_sessions:
        return jsonify({'success': False, 'message': 'No active game session'})

    game_session = game_sessions[session_id]
    game_state = game_session.get_game_state()

    if game_state and game_session.current_game:
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


@bp.route('/leaderboard', methods=['GET'])
def leaderboard():
    try:
        leaderboard_data = db.get_leaderboard(limit=10)

        formatted_leaderboard = []
        for entry in leaderboard_data:
            formatted_leaderboard.append({
                'score': entry['points'],
                'name': entry['name'],
                'rank': entry['rank'],
                'type': entry['type'],
                'time': entry['time'],
                'moves': entry['moves']
            })

        return jsonify({'success': True, 'leaderboard': formatted_leaderboard})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error loading leaderboard: {str(e)}'})


@bp.route('/recent_scores', methods=['GET'])
def recent_scores():
    try:
        recent_scores_data = db.get_recent_scores(limit=10)

        formatted_scores = []
        for score in recent_scores_data:
            formatted_scores.append({
                'score': score['points'],
                'name': score['name'],
                'type': score['type'],
                'time': score['time'],
                'moves': score['moves'],
                'created_at': score['created_at']
            })

        return jsonify({
            'success': True,
            'scores': formatted_scores
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error loading recent scores: {str(e)}'})


@bp.route('/start_bot_demo', methods=['POST'])
def start_bot_demo():
    """Start a new bot demo session"""
    try:
        data = request.json
        selected_bot_key = data.get('bot_key') if data else None
        speed_level = data.get('speed_level', 3)

        bot_menu = get_all_bots()
        bot_list = list(bot_menu)

        if not bot_list:
            return jsonify({'success': False, 'message': 'No bots available'})

        if selected_bot_key and selected_bot_key in bot_menu:
            selected_bot = bot_menu[selected_bot_key]
            bot_key = selected_bot_key
        else:
            bot_key = bot_list[0]
            selected_bot = bot_menu[bot_key]

        bot_name = selected_bot["name"]
        bot_func = selected_bot["func"]

        game_session = GameSession(bot_name, speed_level)
        session_id = game_session.id
        game_sessions[session_id] = game_session

        session['game_session_id'] = session_id

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


@bp.route('/bot_move', methods=['POST'])
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


@bp.route('/validate_custom_bot', methods=['POST'])
def validate_custom_bot():
    """Validate user's custom bot code"""
    try:
        data = request.json
        code = data.get('code', '')
        ok, message = validate_code(code)
        return jsonify({'success': ok, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Validation error: {str(e)}'})


@bp.route('/save_custom_bot', methods=['POST'])
def save_custom_bot():
    """Save custom bot to global storage"""
    try:
        data = request.json
        bot_name = data.get('bot_name', 'CustomBot').strip()
        code = data.get('code', '')

        ok, message, bot_key = register_custom_bot(bot_name, code)
        if not ok:
            return jsonify({'success': False, 'message': message})
        return jsonify({'success': True, 'message': message, 'bot_key': bot_key})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Save error: {str(e)}'})


@bp.route('/start_custom_bot_demo', methods=['POST'])
def start_custom_bot_demo():
    """Start demo with user's custom bot"""
    try:
        data = request.json
        code = data.get('code', '')
        bot_name = data.get('bot_name', 'CustomBot')
        speed_level = data.get('speed_level', 3)

        if not code.strip():
            return jsonify({'success': False, 'message': 'Code cannot be empty'})

        try:
            custom_bot_func = compile_sandboxed_bot(code)
        except Exception as e:
            return jsonify({'success': False, 'message': f'Code execution error: {str(e)}'})

        game_session = GameSession(bot_name, speed_level)
        game_session.is_test_bot = True
        print(f"DEBUG: Created test bot session - is_test_bot: {game_session.is_test_bot}")
        session_id = game_session.id
        game_sessions[session_id] = game_session

        session['game_session_id'] = session_id

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


@bp.route('/custom_bot_move', methods=['POST'])
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


@bp.route('/admin_panel')
def admin_panel():
    """Admin panel page for database viewing"""
    return render_template('admin.html')


@bp.route('/admin_data', methods=['POST'])
def admin_data():
    """Get admin data with PIN verification"""
    try:
        data = request.json
        pin = data.get('pin', '')

        if pin != current_app.config['ADMIN_PIN']:
            return jsonify({'success': False, 'message': 'Invalid PIN'})

        all_scores = db.get_all_scores_admin()

        return jsonify({
            'success': True,
            'data': all_scores,
            'total_records': len(all_scores)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})
