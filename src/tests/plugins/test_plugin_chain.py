from plugins.plugin import IoMode, Plugin
from plugins.plugin_chain import PluginChain


class _FakePlugin(Plugin):
    DEFAULT_NAME = "Fake"
    IO_MODE = IoMode.SAME_COUNT

    def __init__(self, transform, **kwargs):
        super().__init__(**kwargs)
        self._transform = transform
        self.executed = False

    def get_description(self):
        return "fake"

    def run(self, user_input_list):
        return [self._transform(line) for line in user_input_list]

    def execute(self, user_input_list, history_recorder):
        self.executed = True
        return super().execute(user_input_list, history_recorder)


class _FakeExecution:
    def __init__(self):
        self.steps = []
        self.finished = None

    def record_step(self, position, plugin, input_text, output_text):
        self.steps.append((position, plugin, input_text, output_text))

    def finish(self, input_text, output_text):
        self.finished = (input_text, output_text)


class _FakeRecorder:
    def __init__(self):
        self.plugin_executions = []
        self.execution = _FakeExecution()

    def record_plugin_execution(self, plugin, input_text, output_text):
        self.plugin_executions.append((plugin, input_text, output_text))

    def start_chain_execution(self, chain):
        return self.execution


def test_chain_pipes_output_into_next_step():
    upper = _FakePlugin(str.upper)
    exclaim = _FakePlugin(lambda line: line + "!")
    chain = PluginChain(custom_name="Loud", steps=[upper, exclaim])

    result = chain.execute(["ab", "cd"], _FakeRecorder())

    assert result == ["AB!", "CD!"]


def test_chain_runs_steps_without_calling_child_execute():
    upper = _FakePlugin(str.upper)
    chain = PluginChain(custom_name="Loud", steps=[upper])

    chain.execute(["ab"], _FakeRecorder())

    # Steps must use run(), not execute(), to avoid standalone history entries.
    assert upper.executed is False


def test_chain_records_summary_and_each_step():
    upper = _FakePlugin(str.upper)
    exclaim = _FakePlugin(lambda line: line + "!")
    chain = PluginChain(custom_name="Loud", steps=[upper, exclaim])
    recorder = _FakeRecorder()

    chain.execute(["ab"], recorder)

    # Runnables hand the recorder raw line lists; the recorder joins to text.
    assert recorder.execution.finished == (["ab"], ["AB!"])
    positions = [step[0] for step in recorder.execution.steps]
    assert positions == [1, 2]
    # step 1 input is the original, step 2 input is step 1 output
    assert recorder.execution.steps[0][2] == ["ab"]
    assert recorder.execution.steps[0][3] == ["AB"]
    assert recorder.execution.steps[1][2] == ["AB"]
    assert recorder.execution.steps[1][3] == ["AB!"]
    # A chain does not record a standalone plugin execution.
    assert recorder.plugin_executions == []


def test_plugin_execute_records_single_standalone_execution():
    plugin = _FakePlugin(str.upper)
    recorder = _FakeRecorder()

    result = plugin.execute(["ab", "cd"], recorder)

    assert result == ["AB", "CD"]
    assert len(recorder.plugin_executions) == 1
    recorded_plugin, input_data, output_data = recorder.plugin_executions[0]
    assert recorded_plugin is plugin
    # Raw line lists are passed to the recorder (it joins to text on write).
    assert input_data == ["ab", "cd"]
    assert output_data == ["AB", "CD"]


def test_chain_io_mode_is_any_to_any():
    chain = PluginChain(custom_name="Any")
    assert chain.IO_MODE is IoMode.ANY_TO_ANY
    assert chain.get_io_mode() is IoMode.ANY_TO_ANY
