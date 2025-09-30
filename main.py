import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext as scrolledtext
import pyperclip
import sqlite3

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
    root.title("Dev assistant")
    screen_width = root.winfo_screenwidth()
    window_width = 700

    # Position in top-right corner
    root.geometry("{}x650+{}+0".format(window_width, screen_width - window_width))

    # Use context manager for database connection
    with sqlite3.connect("plugins.db") as db_connection:
        db_connection.row_factory = sqlite3.Row
        cursor = db_connection.cursor()
        # create a table to store the plugins
        try:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS plugins (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name TEXT, 
                activated INTEGER,
                new_plugin INTEGER,
                option INTEGER,
                shortcut TEXT,
                custom_name TEXT
            )""")
        
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS plugin_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                input TEXT, 
                output TEXT,
                plugin_name TEXT,
                timestamp TEXT
            )""")
            db_connection.commit()  # Save on success
        except Exception as e:
            db_connection.rollback()  # Undo on error
            print(f"Error: {e}")

        create_widgets(root, db_connection)
        
        # Bind the close event
        def on_closing():
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the application
        root.mainloop()
    # Database automatically closes when exiting the 'with' block

def create_widgets(root, db_connection):
    # Create a frame to hold the grid
    main_container = ttk.Frame(root)
    main_container['padding'] = 10
    main_container.pack(side="top", fill="both", expand=True)
    
    main_container.columnconfigure(0, weight=3)
    main_container.columnconfigure(1, weight=2)
    main_container.columnconfigure(2, weight=3)

    main_container.rowconfigure(0, weight=10)
    main_container.rowconfigure(1, weight=1)
    main_container.rowconfigure(2, weight=1)

    # Create a frame to hold the buttons using grid with 2 columns
    frame_buttons = ttk.Frame(main_container)
    frame_buttons.columnconfigure(0, weight=1)
    frame_buttons.columnconfigure(1, weight=10)

    frame_output_buttons = ttk.Frame(main_container)
    frame_output_buttons['padding'] = 5

    # create an input text area
    user_input_text_area = scrolledtext.ScrolledText(
        main_container, 
        height=35, 
        width=30,
        wrap=tk.NONE
    )

    # create an output text area
    user_output_text_area = scrolledtext.ScrolledText(
        main_container, 
        height=35, 
        width=30,
        wrap=tk.NONE
    )

    plugins = load_plugins(db_connection)
    print("***** End of loading plugins: loaded ", len(plugins), " plugins")
    
    # Create a dictionary mapping plugin names to plugin classes
    plugins_dict = {}
    for plugin_class in plugins:
        plugin_name = plugin_class.__name__
        plugins_dict[plugin_name] = plugin_class
    
    # get the plugins from the database
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM plugins WHERE activated = 1")
    plugins_from_database = cursor.fetchall()
    
    i = 0 # counter for the grid

    for plugin_from_database in plugins_from_database:
        if plugin_from_database['name'] not in plugins_dict:
            print("Plugin from database not found in plugins: ", plugin_from_database['name'])
            continue
        
        # instantiate the plugin
        plugin_instance = plugins_dict[plugin_from_database['name']]()
        plugin_instance.option = plugin_from_database['option']
        plugin_instance.shortcut = plugin_from_database['shortcut']
        plugin_instance.custom_name = plugin_from_database['custom_name']
  

        print("Instanciated plugin: ", plugin_instance.get_name())
        # create a button to directly run the plugin from the clipboard
        plugin_from_clipboard_button = ttk.Button(
            frame_buttons,
            text=f"{copy_symbol}",
            command=lambda p=plugin_instance: [
                get_text_from_clipboard(user_input_text_area),
                plugin_entrance(p.run, user_input_text_area, user_output_text_area)
            ]
        )
        plugin_from_clipboard_button.grid(row=i, column=0, sticky="ew", padx=(5, 5))
        
        # create a button to run the plugin from the input
        plugin_button = ttk.Button(
            frame_buttons,
            text=plugin_instance.get_name(),
            command=lambda p=plugin_instance: plugin_entrance(p.run, user_input_text_area, user_output_text_area)
        )
        plugin_button.grid(row=i, column=1, sticky="ew", padx=(0, 5))
        i += 1
        
        # Force buttons to expand to fill available space
        plugin_from_clipboard_button.configure(width=2)
        plugin_button.configure(width=15)
        
    copy_result_to_input_button = ttk.Button(
        frame_output_buttons, 
        text="⤾ result to input", 
        command=lambda: copy_result_to_input(user_input_text_area, user_output_text_area)
    )
    copy_result_to_clipboard_button = ttk.Button(
        frame_output_buttons, 
        text=f"{copy_symbol} clipboard", 
        command=lambda: pyperclip.copy(user_output_text_area.get("1.0", "end-1c"))
    )
    copy_result_to_input_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
    copy_result_to_clipboard_button.pack(side=tk.LEFT, fill=tk.X, expand=True)


    # grid the widgets
    user_input_text_area.grid(row=0, column=0, sticky="nsew")
    frame_buttons.grid(row=0, column=1, sticky="nsew")
    user_output_text_area.grid(row=0, column=2, sticky="nsew")
    frame_output_buttons.grid(row=1, column=2, sticky="nsew")

# #########
# app functions
def copy_result_to_input(input_text_area, output_text_area):
    output_text = output_text_area.get("1.0", "end-1c")
    input_text_area.delete("1.0", tk.END)
    input_text_area.insert("1.0", output_text)


if __name__ == "__main__":
    main()
