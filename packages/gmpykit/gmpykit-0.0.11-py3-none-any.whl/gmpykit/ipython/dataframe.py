from IPython.display import display

import pandas as pd


def infos(df: pd.DataFrame, nb: int = 5, random: bool = False) -> None:
    """Get shape and extract of a dataframe."""

    print("Shape: ", df.shape, "- extract:")
    if random: display(df.sample(nb))
    else: display(df.head(nb))
