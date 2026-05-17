import tkinter as tk

from utils.ui import split_lines


def plugin_entrance(plugin_function, input_text_area, output_text_area):
    user_input_list = split_lines(input_text_area)
    output_list = plugin_function(user_input_list)
    output_text = "\n".join(output_list)
    output_text_area.delete("1.0", tk.END)
    output_text_area.insert("1.0", output_text)
