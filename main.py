import tkinter as tk

from app.main_view import create_main_view
from database.connection import database_connection


def main():
    root = tk.Tk()
    root.title("Dev assistant")
    screen_width = root.winfo_screenwidth()
    window_width = 700
    root.geometry("{}x650+{}+0".format(window_width, screen_width - window_width))

    with database_connection() as db_connection:
        create_main_view(root, db_connection)

        root.protocol("WM_DELETE_WINDOW", root.destroy)
        root.mainloop()


if __name__ == "__main__":
    main()
