from datetime import datetime


def now() -> float:
    """Get current timestamp in seconds (number)."""
    return int(datetime.now().timestamp())


def format_duration(duration: float, fixed_format=False) -> str:
    """Transform a number of second into a human readable string."""

    counted = 0
    years = int(duration / 31556952)
    counted += years * 31556952
    months = int((duration - counted) / 2629746)
    counted += months * 2629746
    days = int((duration - counted) / 86400)
    counted += days * 86400
    hours = int((duration - counted) / 3600)
    counted += hours * 3600
    minutes = int((duration - counted) / 60)
    counted += minutes * 60
    seconds = int(round(duration - counted))

    years_str = "{:0>4.0f}".format(years)
    months_str = "{:0>2.0f}".format(months)
    days_str = "{:0>2.0f}".format(days)
    hours_str = "{:0>2.0f}".format(hours)
    minutes_str = "{:0>2.0f}".format(minutes)
    seconds_str = "{:0>2.0f}".format(seconds)

    return f"{years_str}y{months_str}m{days_str}d-{hours_str}h{minutes_str}m{seconds_str}s"
