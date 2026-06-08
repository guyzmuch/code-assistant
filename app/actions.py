import tkinter as tk


def copy_result_to_input(input_text_area, output_text_area):
    output_text = output_text_area.get("1.0", "end-1c")
    paste_text_to_input(input_text_area, output_text)


def paste_text_to_input(input_text_area, text: str):
    input_text_area.delete("1.0", tk.END)
    input_text_area.insert("1.0", text)
