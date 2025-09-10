from abc import ABC, abstractmethod

class Plugin(ABC):
    def __init__(self):
        # These should be set by child classes
        self.name = self.get_name()
        self.description = self.get_description()
        self.options = self.get_options()
    
    @abstractmethod
    def get_name(self):
        """Return the plugin name. Must be implemented by child classes."""
        pass
    
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