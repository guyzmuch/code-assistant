from plugins.plugin import IoMode
from plugins.runnable import Runnable

DEFAULT_CHAIN_NAME = "Chain"


class PluginChain(Runnable):
    """An ordered pipeline of plugins run one after another.

    A chain contains Plugin instances (composition, not inheritance from
    Plugin): it is not itself a transformation plugin, but it implements the
    shared Runnable interface (get_name/execute) so the panel, menu and
    plugin_entrance treat it like any single plugin.

    IO_MODE is always ANY_TO_ANY: the overall cardinality depends on the steps
    and is not practical to derive.
    """

    IO_MODE = IoMode.ANY_TO_ANY

    def __init__(
        self,
        custom_name=None,
        steps=None,
        id=None,
        config_version=None,
        shortcut=None,
    ):
        self.custom_name = custom_name or ""
        self.plugins = list(steps or [])
        self.id = id
        self.config_version = config_version
        self.shortcut = shortcut or ""
        self.name = self.custom_name or DEFAULT_CHAIN_NAME

    def get_name(self):
        return self.name

    def get_io_mode(self):
        return type(self).IO_MODE

    def execute(self, user_input_list, history_recorder):
        """Pipe the input through every step and record the whole run.

        Each step's pure run() output becomes the next step's input. Steps are
        run via run() (never execute()) so they are not saved as independent
        executions; the chain records one grouped execution instead. The
        recorder turns the line lists into stored text, so no joining here.
        """
        execution = history_recorder.start_chain_execution(self)

        current_list = user_input_list
        for position, plugin in enumerate(self.plugins, start=1):
            step_input_list = current_list
            output_list = plugin.run(current_list)
            execution.record_step(
                position, plugin, step_input_list, output_list
            )
            current_list = output_list

        execution.finish(user_input_list, current_list)
        return current_list
