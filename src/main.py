from app.main_view import create_main_view
from app.window import create_root_window
from database.connection import database_connection


def main():
    root = create_root_window()

    with database_connection() as db_connection:
        create_main_view(root, db_connection)

        root.protocol("WM_DELETE_WINDOW", root.destroy)
        root.mainloop()


if __name__ == "__main__":
    main()
