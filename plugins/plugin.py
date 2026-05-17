from abc import ABC, abstractmethod


class Plugin(ABC):
    DEFAULT_NAME = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.DEFAULT_NAME is None:
            raise TypeError(f"{cls.__name__} must define DEFAULT_NAME")

    def __init__(self, custom_name=None, options=None, shortcut=None):
        cls = type(self)
        self.custom_name = custom_name or ""
        self.options = options if isinstance(options, str) and options else "{}"
        self.shortcut = shortcut or ""
        self.name = self.custom_name if self.custom_name else cls.DEFAULT_NAME
        self.description = self.get_description()
        self.available_options = self.get_options()

    def get_name(self):
        return self.name

    @abstractmethod
    def get_description(self):
        """Return the plugin description. Must be implemented by child classes."""
        pass

    @abstractmethod
    def get_options(self):
        """Return the plugin options. Must be implemented by child classes."""
        pass

    @abstractmethod
    def run(self, user_input_list):
        """Run the plugin with input data. Must be implemented by child classes."""
        pass
