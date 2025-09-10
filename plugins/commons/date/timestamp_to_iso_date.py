from plugins.plugin import Plugin
from helpers import apply_for_all_lines
import datetime

class TimestampToIsoDate(Plugin):
    def get_name(self):
        return "Timestamp to ISO date"
    
    def get_description(self):
        return "Convert timestamp to ISO date"
    
    def get_options(self):
        return {}
    
    def run(self, user_input_list):
        """
        12456
        23456321
        123456789
        """
        converted_date = apply_for_all_lines(
            user_input_list,
            lambda x: datetime.datetime.fromtimestamp(int(x)).isoformat()
        )

        return converted_date