BS = "\\"
must_escape = (BS, "'", "`")


def format_str(value: str):
    return f"'{escape_str(value)}'"


def escape_str(value: str):
    return "".join(f"{BS}{c}" if c in must_escape else c for c in value)
