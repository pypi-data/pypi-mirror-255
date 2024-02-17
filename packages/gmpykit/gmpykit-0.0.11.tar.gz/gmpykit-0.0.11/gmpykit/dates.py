from typing import Literal
import pandas as pd
from pandas._libs.missing import NAType
import jdcal


def to_julian_day(tuple: tuple[int, int, int], calendar: Literal["gregorian", "julian"] = "gregorian") -> float:
    """Calculate the julian_day of the given tuple date."""
    if pd.isna(tuple):
        return pd.NA

    year = tuple[0]
    month = tuple[1] if pd.notna(tuple[1]) else 1
    day = tuple[2] if pd.notna(tuple[2]) else 1

    if calendar == "gregorian":
        tuple2 = jdcal.gcal2jd(year, month, day)
    if calendar == "julian":
        tuple2 = jdcal.jcal2jd(year, month, day)  # To be verified

    return tuple2[0] + tuple2[1]


def from_julian_day(julian_day: int, calendar: Literal["gregorian", "julian"] = "gregorian") -> tuple[int, int, int]:
    """Return a date tuple corresponding to the provided julian day."""
    if pd.isna(julian_day):
        return pd.NA
    n1 = 2400000.5
    n2 = julian_day - n1
    if calendar == "gregorian":
        year, month, day, _ = jdcal.jd2gcal(n1, n2)
    if calendar == "julian":
        year, month, day, _ = jdcal.jd2jcal(n1, n2)
    return (year, month, day)


def parse_date_str_formated(str: str | NAType) -> tuple[int, int, int] | NAType:
    """Parse a string into a date. Handles errors. Has to be YYYY{sep}MM{sep}DD format. Supported separators are '-' and '/'."""
    if pd.isna(str):
        return pd.NA

    try:
        str = str.replace("-", "")
        str = str.replace("/", "")
        str = str[0:8]

        year = int(str[0:4])
        month = int(str[4:6])
        day = int(str[6:8])

        return (year, month, day)
    except:
        return pd.NA


def parse_date_tuple_formated(str: str | NAType) -> tuple[int, int, int] | NAType:
    """Return a tupled date from a tupled string. Input format should be '(9999,99,99)'."""
    if pd.isna(str): return pd.NA
    return tuple([int(s) if "<NA>" not in s else pd.NA for s in str[1:-1].split(",")])


def days_between(d1: tuple[int, int, int], d2: tuple[int, int, int]) -> float:
    """Return the number of days between the 2 provided dates."""
    d1_jd = to_julian_day((d1[0], d1[1], d1[2]))
    d2_jd = to_julian_day((d2[0], d2[1], d2[2]))
    return abs(d1_jd - d2_jd)
