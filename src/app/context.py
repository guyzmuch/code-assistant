from views.main_layout import MainLayout

_context = None


class AppContext:
    def __init__(
        self,
        db_connection,
        layout: MainLayout,
        history_panel,
        plugin_classes,
    ):
        self.db_connection = db_connection
        self.layout = layout
        self.history_panel = history_panel
        self.history_visible = False
        self.plugin_classes = list(plugin_classes)
        self.plugins_by_name = {
            plugin_class.__name__: plugin_class
            for plugin_class in self.plugin_classes
        }

    def refresh_history_if_visible(self):
        if self.history_visible:
            self.history_panel.refresh()

    def repopulate_plugins(self):
        from app.menu import repopulate_plugins_menu
        from app.plugin_panel import repopulate_plugin_buttons

        repopulate_plugin_buttons()
        repopulate_plugins_menu()


def init(db_connection, layout: MainLayout, history_panel) -> AppContext:
    global _context
    from app.plugins_loader import discover_plugin_classes

    _context = AppContext(
        db_connection,
        layout,
        history_panel,
        discover_plugin_classes(),
    )
    return _context


def get() -> AppContext:
    if _context is None:
        raise RuntimeError("App context is not initialized")
    return _context


def db_connection():
    return get().db_connection


def plugin_classes():
    return get().plugin_classes


def plugins_by_name():
    return get().plugins_by_name


def refresh_history_if_visible():
    get().refresh_history_if_visible()
