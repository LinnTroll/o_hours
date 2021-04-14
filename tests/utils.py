"""Utils for tests."""


def s_time(hours: int, minutes: int = 0) -> int:
    """Convert hours and minutes to seconds."""
    return hours * 60 * 60 + minutes * 60
