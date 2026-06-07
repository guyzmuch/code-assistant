import tkinter as tk

from database.plugin_history import save_plugin_execution
from plugins.commons.diff.diff import Diff
from plugins.plugin import Plugin
from utils.ui import split_lines


def plugin_entrance(
    plugin: Plugin,
    input_text_area,
    output_text_area,
    db_connection=None,
):
    input_text = input_text_area.get("1.0", "end-1c")
    user_input_list = split_lines(input_text_area)

    if isinstance(plugin, Diff):
        output_text = plugin.render_output(output_text_area, user_input_list)
    else:
        output_list = plugin.run(user_input_list)
        output_text = "\n".join(output_list)
        output_text_area.configure(state="normal")
        output_text_area.delete("1.0", tk.END)
        output_text_area.insert("1.0", output_text)

    if db_connection is not None:
        save_plugin_execution(db_connection, plugin, input_text, output_text)
