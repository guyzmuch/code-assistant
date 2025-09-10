import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import pyperclip

from helpers import get_text_from_clipboard, plugin_entrance
from plugins.plugins_loader import load_plugins


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

    plugins = load_plugins()
    print("***** End of loading plugins: loaded ", len(plugins), " plugins")
    for plugin in plugins:
        # instantiate the plugin
        plugin_instance = plugin()
        # create a frame for the plugin
        plugin_frame = tk.Frame(frame_buttons)
        plugin_frame.pack()
        print("Instanciated plugin: ", plugin_instance.get_name())
        # create a button to directly run the plugin from the clipboard
        plugin_from_clipboard_button = tk.Button(
            plugin_frame,
            text=f"{copy_symbol}",
            command=lambda p=plugin_instance: [
                get_text_from_clipboard(user_input_text_area),
                plugin_entrance(p.run, user_input_text_area, user_output_text_area)
            ]
        )
        plugin_from_clipboard_button.pack(side=tk.LEFT)
        # create a button to run the plugin from the input
        plugin_button = tk.Button(
            plugin_frame,
            text=plugin_instance.get_name(),
            command=lambda p=plugin_instance: plugin_entrance(p.run, user_input_text_area, user_output_text_area)
        )
        plugin_button.pack(side=tk.LEFT)
    
    copy_result_to_input_button = tk.Button(
        frame_output_buttons, 
        text="⤾ result to input", 
        command=lambda: copy_result_to_input(user_input_text_area, user_output_text_area)
    )
    copy_result_to_clipboard_button = tk.Button(
        frame_output_buttons, 
        text=f"{copy_symbol} clipboard", 
        command=lambda: pyperclip.copy(user_output_text_area.get("1.0", "end-1c"))
    )

    frame_input.pack(side=tk.LEFT)
    frame_buttons.pack(side=tk.LEFT) 
    frame_output.pack(side=tk.LEFT)

    user_input_text_area.pack(fill=tk.BOTH, expand=True)
   
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


if __name__ == "__main__":
    main()
