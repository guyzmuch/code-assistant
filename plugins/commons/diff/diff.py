import difflib
import tkinter as tk

import pyperclip

from plugins.plugin import Plugin
from utils.format import format_error
from utils.text import require_input

_DIFF_CONTEXT = 3
# Single-digit line numbers only: aligns " 1:1  ", "-2    ", "+2    ".
_LINE_PREFIX_WIDTH = 6


def _format_prefix(
    left_num: int | None, right_num: int | None, tag: str
) -> str:
    if tag == "diff_context":
        prefix = f" {left_num}:{right_num}  "
    elif tag == "diff_removed":
        prefix = f"-{left_num}  "
    else:
        prefix = f"+{right_num}  "
    return prefix.ljust(_LINE_PREFIX_WIDTH)


def _format_segment(
    left_num: int | None,
    right_num: int | None,
    line: str,
    tag: str,
) -> tuple[str, str]:
    return (f"{_format_prefix(left_num, right_num, tag)}{line}\n", tag)


def _collect_segments(left: list[str], right: list[str]) -> list[tuple[int | None, int | None, str, str]]:
    matcher = difflib.SequenceMatcher(a=left, b=right)
    segments: list[tuple[int | None, int | None, str, str]] = []
    left_num = 1
    right_num = 1

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for line in left[i1:i2]:
                segments.append((left_num, right_num, line, "diff_context"))
                left_num += 1
                right_num += 1
        elif tag == "delete":
            for line in left[i1:i2]:
                segments.append((left_num, None, line, "diff_removed"))
                left_num += 1
        elif tag == "insert":
            for line in right[j1:j2]:
                segments.append((None, right_num, line, "diff_added"))
                right_num += 1
        elif tag == "replace":
            for line in left[i1:i2]:
                segments.append((left_num, None, line, "diff_removed"))
                left_num += 1
            for line in right[j1:j2]:
                segments.append((None, right_num, line, "diff_added"))
                right_num += 1

    return segments


def _apply_context(
    segments: list[tuple[int | None, int | None, str, str]], context: int = _DIFF_CONTEXT
) -> list[tuple[int | None, int | None, str, str]]:
    change_indices = [
        index for index, segment in enumerate(segments) if segment[3] != "diff_context"
    ]
    if not change_indices:
        return []

    visible = set()
    for change_index in change_indices:
        start = max(0, change_index - context)
        end = min(len(segments), change_index + context + 1)
        visible.update(range(start, end))

    return [segments[index] for index in sorted(visible)]


def build_diff_segments(left: list[str], right: list[str]) -> list[tuple[str, str | None]]:
    visible = _apply_context(_collect_segments(left, right))
    return [
        _format_segment(left_num, right_num, line, tag)
        for left_num, right_num, line, tag in visible
    ]


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
        return "Diff input against the clipboard with line numbers (input:clipboard)"

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
