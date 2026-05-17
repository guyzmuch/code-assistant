from plugins.plugin import Plugin
from utils.text import apply_for_all_lines, flatten_and_remove_empty_lines


class SplitByComma(Plugin):
    DEFAULT_NAME = "Split by comma"

    def get_description(self):
        return "Split text by comma and flatten the result"

    def run(self, user_input_list):
        """
        apple , banana , cherry
        orange  ,  grape  ,  kiwi
        citron,mango,pear,pineapple,
        """
        output_list = apply_for_all_lines(user_input_list, lambda x: [item.strip() for item in x.split(",")])

        flattened_list = flatten_and_remove_empty_lines(output_list)

        return flattened_list