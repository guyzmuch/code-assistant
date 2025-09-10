
# #########
# helper functions
import pyperclip
import tkinter as tk

def get_text_from_clipboard(input_text_area):
    input_text_area.delete("1.0", tk.END)
    input_text_area.insert("1.0", pyperclip.paste())

def split_lines(input_text_area):
    user_input = input_text_area.get("1.0", "end-1c")
    # split user input by linebreak
    user_input_list = user_input.split("\n")
    return user_input_list

def apply_for_all_lines(lines, function): 
    output_list = []
    for line in lines:
        if not line:
            output_list.append(line)
            continue
        try:
            output_list.append(function(line))
        except Exception as e:
            output_list.append(f"Error: {e}")

    return output_list

def plugin_entrance(plugin_function, input_text_area, output_text_area):
    user_input_list = split_lines(input_text_area)
    output_list = plugin_function(user_input_list)
    output_text = "\n".join(output_list)
    output_text_area.delete("1.0", tk.END)
    output_text_area.insert("1.0", output_text)

def flatten_and_remove_empty_lines(output_list):
    flattened_list = []
    for sublist in output_list:
        for item in sublist:
            if item:  # Only add non-empty lines
                flattened_list.append(item)
    return flattened_list 
