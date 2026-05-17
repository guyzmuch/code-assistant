_ERROR_DIVIDER = "--------------------"


def format_section(title: str) -> str:
    return f"--- {title}"


def format_error(message: str) -> str:
    return (
        f"{_ERROR_DIVIDER}\n"
        f"--- ERROR\n"
        f"\n"
        f"{message}\n"
        f"{_ERROR_DIVIDER}"
    )
