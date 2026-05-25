from app.plugin_panel import populate_plugin_buttons
from views.main_layout import create_main_layout


def create_main_view(root, db_connection):
    layout = create_main_layout(root)
    populate_plugin_buttons(layout, db_connection)
