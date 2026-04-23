from typing import Optional, Tuple

from .state import custom_bots

SAFE_BUILTINS = {
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
}


def validate_code(code: str) -> Tuple[bool, str]:
    if not code.strip():
        return False, 'Code cannot be empty'
    if 'def checkBot(' not in code:
        return False, 'Missing required function: def checkBot(hero)'
    if 'return ' not in code:
        return False, 'Function must return a move (w, a, s, d)'
    try:
        compile(code, '<string>', 'exec')
    except SyntaxError as e:
        return False, f'Syntax Error: {str(e)}'
    return True, 'Code validation passed'


def register_custom_bot(bot_name: str, code: str) -> Tuple[bool, str, Optional[str]]:
    if not bot_name:
        return False, 'Bot name is required', None
    if not code.strip():
        return False, 'Bot code is required', None
    if 'def checkBot(' not in code:
        return False, 'Missing required function: def checkBot(hero)', None

    try:
        custom_globals: dict = {}
        exec(code, custom_globals)

        if 'checkBot' not in custom_globals:
            return False, 'Function checkBot not found after execution', None

        custom_bot_func = custom_globals['checkBot']
        bot_key = "custom_bot_builder"
        custom_bots[bot_key] = {
            'name': bot_name,
            'func': custom_bot_func,
            'code': code,
            'type': 'custom'
        }
        return True, f'Bot "{bot_name}" saved successfully! ', bot_key
    except Exception as e:
        return False, f'Bot execution error: {str(e)}', None


def compile_sandboxed_bot(code: str):
    custom_globals = {
        '__builtins__': dict(SAFE_BUILTINS),
        'random': __import__('random'),
    }
    exec(code, custom_globals)
    if 'checkBot' not in custom_globals:
        raise ValueError('Function checkBot not found')
    return custom_globals['checkBot']
