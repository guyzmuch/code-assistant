import datetime
import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import pyperclip


boxed_letters = [
    "🅰",  # A in box
    "🅱",  # B in box
    "🅲",  # C in box
    "🅳",  # D in box
    "🅴",  # E in box
    "🅵",  # F in box
    "🅶",  # G in box
    "🅷",  # H in box
    "🅸",  # I in box
    "🅹",  # J in box
    "🅺",  # K in box
    "🅻",  # L in box
    "🅼",  # M in box
    "🅽",  # N in box
    "🅾",  # O in box
    "🅿",  # P in box
    "🆀",  # Q in box
    "🆁",  # R in box
    "🆂",  # S in box
    "🆃",  # T in box
    "🆄",  # U in box
    "🆅",  # V in box
    "🆆",  # W in box
    "🆇",  # X in box
    "🆈",  # Y in box
    "🆉",  # Z in box
]

copy_symbol = "📋"

def main():
    # Create the main window
    root = tk.Tk()
    root.title("code assistant")
    screen_width = root.winfo_screenwidth()
    window_width = 700

    # Position in top-right corner
    root.geometry("{}x650+{}+0".format(window_width, screen_width - window_width))
    #root.geometry("700x650")

    create_widgets(root)
    
    # Start the application
    root.mainloop()

def create_widgets(root):
    # Create a frame to hold horizontal widgets
    frame = tk.Frame(root)
    frame.pack() 

    # Create a frame to hold the buttons
    frame_buttons = tk.Frame(frame)
    frame_input = tk.Frame(frame)
    frame_output = tk.Frame(frame)
    frame_output_buttons = tk.Frame(frame_output)

    # create an input text area
    user_input_text_area = scrolledtext.ScrolledText(
        frame_input, 
        height=35, 
        width=30,
        wrap=tk.NONE
    )

    # create an output text area
    user_output_text_area = scrolledtext.ScrolledText(
        frame_output, 
        height=35, 
        width=30,
        wrap=tk.NONE
    )

    # create the actionable buttons
    timestamp_to_iso_date_convertion_button = tk.Button(frame_buttons, text="ISO date convertion", command=lambda: plugin_entrance(timestamp_to_iso_date_convertion, user_input_text_area, user_output_text_area))
    split_by_comma_button = tk.Button(frame_buttons, text="Split by comma", command=lambda: plugin_entrance(split_by_comma, user_input_text_area, user_output_text_area))
    copy_result_to_input_button = tk.Button(frame_output_buttons, text="⤾ result to input", command=lambda: copy_result_to_input(user_input_text_area, user_output_text_area))
    copy_result_to_clipboard_button = tk.Button(frame_output_buttons, text=f"{copy_symbol} clipboard", command=lambda: pyperclip.copy(user_output_text_area.get("1.0", "end-1c")))

    frame_input.pack(side=tk.LEFT)
    frame_buttons.pack(side=tk.LEFT) 
    frame_output.pack(side=tk.LEFT)

    user_input_text_area.pack(fill=tk.BOTH, expand=True)
   
    timestamp_to_iso_date_convertion_button.pack()
    split_by_comma_button.pack()

    user_output_text_area.pack(fill=tk.BOTH, expand=True)
    frame_output_buttons.pack()
    copy_result_to_input_button.pack(side=tk.LEFT)
    copy_result_to_clipboard_button.pack(side=tk.LEFT)

# #########
# app functions
def copy_result_to_input(input_text_area, output_text_area):
    output_text = output_text_area.get("1.0", "end-1c")
    input_text_area.delete("1.0", tk.END)
    input_text_area.insert("1.0", output_text)

# #########
# helper functions
def split_lines(input_text_area):
    user_input = input_text_area.get("1.0", "end-1c")
    # split user input by linebreak
    user_input_list = user_input.split("\n")
    return user_input_list

def apply_for_all_items(lines, function): 
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

def plugin_entrance(plugin_function, input_text_area, output_text_area):
    user_input_list = split_lines(input_text_area)
    output_list = plugin_function(user_input_list)
    output_text = "\n".join(output_list)
    output_text_area.delete("1.0", tk.END)
    output_text_area.insert("1.0", output_text)

def flatten_and_remove_empty_items(output_list):
    flattened_list = []
    for sublist in output_list:
        for item in sublist:
            if item:  # Only add non-empty items
                flattened_list.append(item)
    return flattened_list 

# #########
# actions for buttons
def timestamp_to_iso_date_convertion(user_input_list):
    """
12456
23456321
123456789
    """
    converted_date = apply_for_all_items(user_input_list, lambda x: datetime.datetime.fromtimestamp(int(x)).isoformat())
    
    return converted_date

def split_by_comma(user_input_list):
    """
apple , banana , cherry
orange  ,  grape  ,  kiwi
citron,mango,pear,pineapple,
    """
    output_list = apply_for_all_items(user_input_list, lambda x: [item.strip() for item in x.split(",")])

    flattened_list = flatten_and_remove_empty_items(output_list)

    return flattened_list


if __name__ == "__main__":
    main()
