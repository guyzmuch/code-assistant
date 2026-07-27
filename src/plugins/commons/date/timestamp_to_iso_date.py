import datetime
from zoneinfo import ZoneInfo

from plugins.plugin import IoMode, Plugin
from utils.text import apply_for_all_lines


class TimestampToIsoDate(Plugin):
    DEFAULT_NAME = "Timestamp to ISO date"
    IO_MODE = IoMode.SAME_COUNT
    DEFAULT_OPTIONS = {"timezone": "local", "hide_offset": True}

    def get_description(self):
        return "Convert timestamp to ISO date"

    def _format_datetime(self, dt):
        if self.options["hide_offset"] and dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
        return dt.isoformat()

    def _timestamp_to_iso(self, value):
        timestamp = int(value)
        timezone = self.options["timezone"]

        if timezone in (None, "", "local"):
            return datetime.datetime.fromtimestamp(timestamp).isoformat()

        dt = datetime.datetime.fromtimestamp(timestamp, tz=ZoneInfo(timezone))
        return self._format_datetime(dt)

    def run(self, user_input_list):
        """
        12456
        23456321
        123456789
        """
        return apply_for_all_lines(user_input_list, self._timestamp_to_iso)
