import datetime
import tkinter as tk

def main():
    # Create the main window
    root = tk.Tk()
    root.title("code assistant")
    root.geometry("700x650")

    create_widgets(root)
    
    # Start the application
    root.mainloop()

def create_widgets(root):
    # Create a frame to hold horizontal widgets
    frame = tk.Frame(root)
    frame.pack() 

    # Create a frame to hold the buttons
    frame_buttons = tk.Frame(frame)

    # create an input text area
    user_input_text_area = tk.Text(frame, height=35, width=30)

    # create an output text area
    user_output_text_area = tk.Text(frame, height=35, width=30)

    # create a button
    timestamp_to_iso_date_convertion_button = tk.Button(frame_buttons, text="ISO date convertion", command=lambda: plugin_entrance(timestamp_to_iso_date_convertion, user_input_text_area, user_output_text_area))
    split_by_comma_button = tk.Button(frame_buttons, text="Split by comma", command=lambda: plugin_entrance(split_by_comma, user_input_text_area, user_output_text_area))

    user_input_text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    frame_buttons.pack(side=tk.LEFT) 
    user_output_text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
   
    timestamp_to_iso_date_convertion_button.pack()
    split_by_comma_button.pack()
    
# helper functions
def split_lines(input_text_area):
    user_input = input_text_area.get("1.0", "end-1c")
    # split user input by linebreak
    user_input_list = user_input.split("\n")
    return user_input_list

def apply_for_all_items(lines, function): 
    output_list = []
    for line in lines:
        output_list.append(function(line))
    return output_list

def plugin_entrance(plugin_function, input_text_area, output_text_area):
    user_input_list = split_lines(input_text_area)
    output_list = plugin_function(user_input_list)
    output_text = "\n".join(output_list)
    output_text_area.delete("1.0", tk.END)
    output_text_area.insert("1.0", output_text)


# actions for buttons

def timestamp_to_iso_date_convertion_outdated(input_text_area, output_text_area):
    user_input = input_text_area.get("1.0", "end-1c")
    # split user input by linebreak 
    user_input_list = user_input.split("\n")
    converted_date = []
    # convert each line to a timestamp
    for line in user_input_list:
        line = line.strip()  # Remove whitespace
        if line:  # Skip empty lines
            try:
                timestamp = int(line)
                # convert timestamp to iso date
                iso_date = datetime.datetime.fromtimestamp(timestamp).isoformat()
                converted_date.append(iso_date)
            except ValueError:
                converted_date.append(f"Invalid timestamp: {line}")
    # join converted dates by linebreak
    converted_date = "\n".join(converted_date)
    # Clear the output area first, then insert the result
    output_text_area.delete("1.0", tk.END)
    output_text_area.insert("1.0", converted_date)
    
def timestamp_to_iso_date_convertion(input_text_area, output_text_area):
    # split user input by linebreak 
    user_input_list = split_lines(input_text_area)

    converted_date = apply_for_all_items(user_input_list, lambda x: datetime.datetime.fromtimestamp(int(x)).isoformat())
    
    # join converted dates by linebreak
    converted_date = "\n".join(converted_date)
    # Clear the output area first, then insert the result
    output_text_area.delete("1.0", tk.END)
    output_text_area.insert("1.0", converted_date)

def split_by_comma(input_text_area, output_text_area):
    # split user input by comma
    user_input_list = split_lines(input_text_area)
    output_list = apply_for_all_items(user_input_list, lambda x: [item.strip() for item in x.split(",")])

    print("output_list:", output_list)

    # Flatten the nested array and remove empty entries
    flattened_list = []
    for sublist in output_list:
        for item in sublist:
            if item:  # Only add non-empty items
                flattened_list.append(item)

    print("flattened_list:", flattened_list)
    # join output list by linebreak
    output_text = "\n".join(flattened_list)
    # Clear the output area first, then insert the result
    #output_text_area.delete("1.0", tk.END)
    output_text_area.insert("1.0", output_text)

"""
12456
23456321
123456789
"""

"""
apple , banana , cherry
  orange  ,  grape  ,  kiwi
  citron,mango,pear,pineapple,
"""

if __name__ == "__main__":
    main()
