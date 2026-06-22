import ast
import json
from abc import ABC, abstractmethod


class Plugin(ABC):
    DEFAULT_NAME = None
    DEFAULT_OPTIONS = {}

    def __init_subclass__(cls, **kwargs):
        # Runs when a subclass is defined (import time). Every plugin must set
        # DEFAULT_NAME so the loader/UI can identify it; fail early, not at runtime.
        super().__init_subclass__(**kwargs)
        if cls.DEFAULT_NAME is None:
            raise TypeError(f"{cls.__name__} must define DEFAULT_NAME")

    def __init__(
        self,
        custom_name=None,
        options=None,
        shortcut=None,
        id=None,
        config_version=None,
    ):
        cls = type(self)
        self.custom_name = custom_name or ""
        self.shortcut = shortcut or ""
        self.id = id
        self.config_version = config_version
        self.name = self.custom_name if self.custom_name else cls.DEFAULT_NAME
        self.description = self.get_description()
        self.options = {**cls.DEFAULT_OPTIONS, **self._parse_options(options)}

    # parse the options from a string to a dictionary
    def _parse_options(self, options):
        if not options:
            return {}
        if isinstance(options, dict):
            return options
        if isinstance(options, str):
            text = options.strip()
            if not text:
                return {}
            try:
                parsed = json.loads(text)
                return parsed if isinstance(parsed, dict) else {}
            except json.JSONDecodeError:
                try:
                    parsed = ast.literal_eval(text)
                    return parsed if isinstance(parsed, dict) else {}
                except (ValueError, SyntaxError):
                    return {}
        return {}

    def get_name(self):
        return self.name

    def get_default_name(self):
        return type(self).DEFAULT_NAME

    def get_options(self):
        return self.options

    @abstractmethod
    def get_description(self):
        """Return the plugin description. Must be implemented by child classes."""
        pass

    @abstractmethod
    def run(self, user_input_list):
        """Run the plugin with input data. Must be implemented by child classes."""
        pass
