import math


def binomial_nb(n: int, k: int) -> int:
    """Return a binomial number."""
    return round(math.factorial(n) / (k * math.factorial(n - k)))
