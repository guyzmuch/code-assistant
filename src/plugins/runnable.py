from typing import Protocol, runtime_checkable


@runtime_checkable
class Runnable(Protocol):
    """Common interface shared by a single Plugin and a PluginChain.

    Callers (panel, menu, plugin_entrance) treat both the same way: read
    metadata via get_name()/get_io_mode() and run via execute(). The history
    recorder is injected so runnables never import the database layer directly.
    """

    id: object
    config_version: object

    def get_name(self) -> str: ...

    def get_io_mode(self): ...

    def execute(self, user_input_list, history_recorder) -> list: ...
