import os
import importlib
import inspect

def getBot():
    current_directory = os.path.dirname(os.path.abspath(__file__))

    all_vars_funcs = {}

    for filename in os.listdir(current_directory):
        if filename.endswith(".py") and filename != "__init__.py" and filename != "template.py":
            module_name = filename[:-3]  # Remove .py extension
            module = importlib.import_module(f".{module_name}", package=__name__)
            all_vars_funcs[module_name] = {}

            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj) or (not name.startswith("__") and not inspect.isroutine(obj)):
                    if name == "NAME":
                        all_vars_funcs[module_name]["name"] = obj
                    if name == "checkBot":
                        all_vars_funcs[module_name]["func"] = obj

    return all_vars_funcs

