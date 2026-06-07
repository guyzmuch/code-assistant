import difflib
import tkinter as tk

import pyperclip

from plugins.plugin import Plugin
from utils.format import format_error
from utils.text import require_input

_DIFF_HEADER_PREFIXES = ("---", "+++", "@@")


def _unified_diff_lines(left: list[str], right: list[str]) -> list[str]:
    return list(
        difflib.unified_diff(
            left,
            right,
            fromfile="input",
            tofile="clipboard",
            lineterm="",
        )
    )


def _content_lines(diff_lines: list[str]) -> list[str]:
    return [
        line
        for line in diff_lines
        if not line.startswith(_DIFF_HEADER_PREFIXES)
    ]


def _line_tag(line: str) -> str | None:
    if line.startswith("+"):
        return "diff_added"
    if line.startswith("-"):
        return "diff_removed"
    if line.startswith(" "):
        return "diff_context"
    return None


def build_diff_segments(left: list[str], right: list[str]) -> list[tuple[str, str | None]]:
    segments = []
    raw_difflib_result = _unified_diff_lines(left, right)
    for line in _content_lines(raw_difflib_result):
        segments.append((f"{line}\n", _line_tag(line)))
    return segments


def write_diff_to_text_widget(
    text_widget: tk.Text, segments: list[tuple[str, str | None]]
) -> None:
    text_widget.configure(state="normal")
    text_widget.delete("1.0", tk.END)
    for text, tag in segments:
        if tag:
            text_widget.insert(tk.END, text, tag)
        else:
            text_widget.insert(tk.END, text)


class Diff(Plugin):
    DEFAULT_NAME = "Diff"

    def get_description(self):
        return "Diff input against the clipboard (unified diff)"

    def run(self, user_input_list):
        try:
            require_input(user_input_list)
            clipboard_lines = pyperclip.paste().splitlines()
            segments = build_diff_segments(user_input_list, clipboard_lines)
            return [text.rstrip("\n") for text, _ in segments]
        except ValueError as e:
            return [format_error(str(e))]

    def render_output(self, output_text_area, user_input_list) -> str:
        try:
            require_input(user_input_list)
            clipboard_lines = pyperclip.paste().splitlines()
            segments = build_diff_segments(user_input_list, clipboard_lines)
            write_diff_to_text_widget(output_text_area, segments)
            return "".join(text for text, _ in segments)
        except ValueError as e:
            message = format_error(str(e))
            output_text_area.configure(state="normal")
            output_text_area.delete("1.0", tk.END)
            output_text_area.insert("1.0", message)
            return message
