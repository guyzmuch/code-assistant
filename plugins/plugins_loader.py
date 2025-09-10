# load all plugins in the plugins folder
import os
import importlib

def load_plugins():
    excluded_files = ["__init__.py", "plugins_loader.py", "plugin.py"]
    plugins = []
    for root, dirs, files  in os.walk("plugins"):  
        for file in files:      
            if file.endswith(".py") and file not in excluded_files:
                #print(f"loading plugin: {file}")
                # Get the full path and convert to module path
                rel_path = os.path.relpath(os.path.join(root, file), ".")
                module_path = rel_path.replace(os.sep, ".")[:-3]  # Remove .py

                module = importlib.import_module(module_path)
                # Find the plugin class in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        hasattr(attr, '__bases__') and 
                        any(base.__name__ == 'Plugin' for base in attr.__bases__)):
                        #print(f"attr is a plugin: {attr}")
                        plugins.append(attr)
    return plugins