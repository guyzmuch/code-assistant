def require_input(lines):
    if not lines:
        raise ValueError("no input provided")


def first_non_empty_line(lines):
    require_input(lines)
    for line in lines:
        if line.strip():
            return line
    raise ValueError("no non-empty line found")


def merge_lines_into_one(lines):
    require_input(lines)
    text = "\n".join(lines).strip()
    if not text:
        raise ValueError("no non-empty input found")
    return text


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


def remove_empty_lines(lines):
    result = []
    for line in lines:
        if not line.strip():
            continue
        result.append(line)
    return result


def flatten_and_remove_empty_lines(output_list):
    flattened_list = []
    for sublist in output_list:
        for item in sublist:
            if item:
                flattened_list.append(item)
    return flattened_list
