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


def flatten_and_remove_empty_lines(output_list):
    flattened_list = []
    for sublist in output_list:
        for item in sublist:
            if item:
                flattened_list.append(item)
    return flattened_list
