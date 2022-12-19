"""Parses a human time specification to float seconds."""

UNITS = "ns, s, min, h, d, a (for year)"

def parse_time(val: float, unit: str) -> float:
    """Converts a number and a unit to time in seconds.

    Args:
      val: A number, representing time.
      unit: A time unit string. See UNITS for available options.

    Returns:
      A float number of seconds.
    """
    if unit == "ns":
        return val / 1e9
    elif unit == "s":
        return val
    if unit == "min":
        return val * 60
    elif unit == "h":
        return val * 3600
    elif unit == "d":
        return val * 3600 * 24
    elif unit == "a":
        return val * 3600 * 24 * 365
    raise ValueError("Unknown unit: {}".format(unit))


def parse_time_str(s: str) -> float:
    """Parses a string to seconds.

    Args:
      s: A single string, representing time, in the form of `<number> <unit>`. See the
        documentation of the parse function for the available units.

    Returns:
      A float, representing the given time in seconds.
    """
    
    parts = s.split()
    return parse_time(float(parts[0]), parts[1])