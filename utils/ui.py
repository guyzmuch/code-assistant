import pyperclip
import tkinter as tk


def get_text_from_clipboard(input_text_area):
    input_text_area.delete("1.0", tk.END)
    input_text_area.insert("1.0", pyperclip.paste())


def split_lines(input_text_area):
    user_input = input_text_area.get("1.0", "end-1c")
    return user_input.split("\n")
