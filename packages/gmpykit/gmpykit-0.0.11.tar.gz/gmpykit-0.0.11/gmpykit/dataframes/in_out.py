import pandas as pd

from ..strings import remove_bin_chars


def write_df(df: pd.DataFrame, path: str) -> None:
    """Save a DataFrame to CSV format."""
    df.to_csv(path, index=False, sep=";", quoting=2)


def read_df(path: str, skip_info: bool = True, sep: str = ";", quoting=2):
    """Read a DataFrame from CSV format."""

    df = pd.read_csv(path, sep=sep, quoting=quoting, low_memory=False)
    df = df.infer_objects(df)
    cleanse_binaries(df)

    return df


def cleanse_binaries(df: pd.DataFrame) -> None:
    """In each columns, remove all binary chars found."""

    for col in df.columns:
        if df[col].dtype in ['object', 'string']:
            df[col] = [remove_bin_chars(text) for text in df]
