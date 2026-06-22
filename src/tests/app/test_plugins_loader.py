from app.constants import DEFAULT_PLUGIN_CLASS_NAMES
from app.plugins_loader import discover_plugin_classes


def test_discover_plugin_classes_finds_default_plugins():
    plugin_classes = discover_plugin_classes()
    class_names = {cls.__name__ for cls in plugin_classes}

    assert len(plugin_classes) >= len(DEFAULT_PLUGIN_CLASS_NAMES)
    for name in DEFAULT_PLUGIN_CLASS_NAMES:
        assert name in class_names
