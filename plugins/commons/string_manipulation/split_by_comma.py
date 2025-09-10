from plugins.plugin import Plugin
from helpers import apply_for_all_lines, flatten_and_remove_empty_lines


class SplitByComma(Plugin):
    def get_name(self):
        return "Split by comma"
    
    def get_description(self):
        return "Split text by comma and flatten the result"
    
    def get_options(self):
        return {}  # No options for this plugin
    
    def run(self, user_input_list):
        """
        apple , banana , cherry
        orange  ,  grape  ,  kiwi
        citron,mango,pear,pineapple,
        """
        output_list = apply_for_all_lines(user_input_list, lambda x: [item.strip() for item in x.split(",")])

        flattened_list = flatten_and_remove_empty_lines(output_list)

        return flattened_list