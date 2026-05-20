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

    def __init__(self, custom_name=None, options=None, shortcut=None):
        cls = type(self)
        self.custom_name = custom_name or ""
        self.shortcut = shortcut or ""
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
            try:
                parsed = json.loads(options)
                return parsed if isinstance(parsed, dict) else {}
            except json.JSONDecodeError:
                return {}
        return {}

    def get_name(self):
        return self.name

    @abstractmethod
    def get_description(self):
        """Return the plugin description. Must be implemented by child classes."""
        pass

    @abstractmethod
    def run(self, user_input_list):
        """Run the plugin with input data. Must be implemented by child classes."""
        pass
