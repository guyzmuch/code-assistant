import tkinter as tk

from app.context import get, refresh_history_if_visible
from database.plugin_history import save_plugin_execution
from plugins.plugin import Plugin
from utils.ui import split_lines


def plugin_entrance(plugin: Plugin):
    ctx = get()
    input_text_area = ctx.layout.user_input_text_area
    output_text_area = ctx.layout.user_output_text_area

    input_text = input_text_area.get("1.0", "end-1c")
    user_input_list = split_lines(input_text_area)
    output_list = plugin.run(user_input_list)
    output_text = "\n".join(output_list)
    output_text_area.delete("1.0", tk.END)
    output_text_area.insert("1.0", output_text)

    save_plugin_execution(ctx.db_connection, plugin, input_text, output_text)
    refresh_history_if_visible()
