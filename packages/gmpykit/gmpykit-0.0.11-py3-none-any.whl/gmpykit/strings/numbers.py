
def percent(nb: float) -> str:
    """Format the number sent into a % number, eg 0.012 into "01.2%" """
    the_number = round(100 * nb, 2)
    the_string = "{: >6.2f}%".format(the_number)
    return the_string


def readable_number(number:float) -> str:
    """Convert the given number into a more readable string"""

    for x in ['', 'k', 'M', 'B']:
        if number < 1000.0: return str(round(number, 1)) + x
        number /= 1000.0
    raise Exception("This Exception should never happen")


def readable_bytes(bytes_nb: float) -> str:
    """Convert bytes to KB, or MB or GB"""

    for x in ["B", "kB", "MB", "GB", "TB"]:
        if size < 1000.0: return "%3.1f %s" % (size, x)
        size /= 1000.0
    raise Exception("This Exception should never happen")
