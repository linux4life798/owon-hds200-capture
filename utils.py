
def split_int_units(value: str) -> tuple[int, str]:
    """Parse a number with units from string as an int."""

    for i, c in enumerate(value):
        if not c.isdigit():
            return int(value[:i]), value[i:]
    return int(value), ""


def split_float_units(value: str) -> tuple[float, str]:
    """Parse a number with units from string as a float."""

    for i, c in enumerate(value):
        if not c.isdigit() and c != ".":
            return float(value[:i]), value[i:]
    return float(value), ""
