from typing import Dict

import pandas as pd
import numpy as np

import plotly.express as px

from ..strings import percent


def group_by_count(df: pd.DataFrame, column: str, agg_column: str = None) -> pd.DataFrame:
    """
    Make a group by and a count on a column, and return a DataFrame.
    
    :param pandas.DataFrame df: The dataframe to analyze
    :param str column: The dataframe column to analyze
    :param str agg_column: Another dataframe column to keep -> Concatenate the unique values of this columns
    """

    loc_df = df.copy()
    loc_df[column].fillna('NaN', inplace=True)

    # Get counts and put in correct format
    gb = loc_df.groupby(column).count()
    gb.reset_index(inplace=True)
    gb = gb[[gb.columns[0], gb.columns[1]]]
    gb.rename(columns={gb.columns[1]: "count"}, inplace=True)
    gb.sort_values("count", ascending=False, inplace=True)
    gb.reset_index(inplace=True, drop=True)

    # Add percent column
    total = gb["count"].sum()
    gb["percent"] = [percent(c / total) for c in gb["count"]]

    # Types
    gb["count"] = gb["count"].astype(pd.Int64Dtype())
    gb["percent"] = gb["percent"].astype(pd.StringDtype())

    if agg_column:
        agg = loc_df.groupby(column).agg(aggregation=pd.NamedAgg(column=agg_column, aggfunc=lambda x: " - ".join(str(e) for e in np.unique(x))))
        gb = gb.merge(agg, on=column, how="left")
        gb.rename(columns={'aggregation':f'{agg_column}'}, inplace=True)


    return gb.sort_values("count", ascending=False)


def na_analyze(df: pd.DataFrame) -> None:
    """Print out an analyze of NA in the dataframe. Designed to work in Jupyter Notebooks."""

    row_number = df.shape[0]
    col_number = df.shape[1]
    nan_number = df.isna().sum().sum()
    nan_columns = df.isna().sum()
    nan_columns_filtered_dict = {key: value for (key, value) in nan_columns.items()}
    nan_columns_filtered = [{"col_name": key, "na_nb": value, "na_percent": value / row_number} for (key, value) in nan_columns_filtered_dict.items()]

    print("Total NaN number:", nan_number, "(" + percent(nan_number / (row_number * col_number)) + ")")

    if nan_number == 0:
        return

    nan_columns_filtered.sort(key=lambda x: x["na_nb"], reverse=True)

    for obj in nan_columns_filtered:
        if obj["na_nb"] == 0:
            continue

        prcnt = percent(obj["na_percent"])
        col_name = str(obj["col_name"])
        print(f" - {prcnt} of column <{col_name}> is not defined")


def column_analyze(df: pd.DataFrame, column: str, nb: int = 20) -> None:
    """Print out an analyse of values of a column."""

    uniques = df[column].unique()
    sumup = []

    for uniq in uniques:
        if pd.notna(uniq):
            sumup.append({"key": uniq, "count": (df[column] == uniq).sum()})
        else:
            sumup.append({"key": "None", "count": (df[column].isna()).sum()})
    sumup.sort(key=lambda elt: elt["count"], reverse=True)

    print(f"{len(sumup)} unique values:")
    for i in range(min(nb, len(sumup))):
        print(percent(sumup[i]["count"] / len(df)) + f': "{sumup[i]["key"]}" ==> {sumup[i]["count"]}')


def histogram(df: pd.DataFrame, column: str, options: Dict[str, str]) -> None:
    """Print out an horizontal histogram of a DataFrame column. Designed for Jupyter notebooks."""

    title = options['title'] if pd.notna(options['title']) else 'Title missing'
    max_number = options['max_number'] if pd.notna(options['max_number']) else 20
    width = options['width'] if pd.notna(options['width']) else None
    height = options['height'] if pd.notna(options['height']) else None
    style = options['style'] if pd.notna(options['style']) else 'bar'
    colors = ['#322659','#44337A','#553C9A','#6B46C1','#805AD5','#9F7AEA','#B794F4','#D6BCFA','#E9D8FD','#FAF5FF','#E9D8FD','#D6BCFA','#B794F4','#9F7AEA','#805AD5','#6B46C1','#553C9A','#44337A'];

    temp_df = df.copy()
    temp_df[column] = temp_df[column].astype(str)
    counts = temp_df.groupby(column).count()
    counts = counts.reset_index()[[column, counts.columns[0]]].sort_values(counts.columns[0], ascending=True)
    counts.rename(columns={counts.columns[1]: "Count"}, inplace=True)
    total_nb = counts["Count"].sum()
    counts["Percent"] = round((counts["Count"] / total_nb) * 1000) / 10
    counts["Percent"] = counts["Percent"].astype(str) + " %"

    if style == "bar":
        fig = px.bar(counts[-max_number:], x="Count", y=column, orientation="h", text="Percent", title=title, width=width, height=height, color_discrete_sequence=colors)
    else:
        fig = px.pie(counts, values="Count", names=column, title=title, color_discrete_sequence=colors)
        fig.update_traces(textposition="inside", textinfo="percent+label", showlegend=False)

    fig.show()


def discover(df: pd.DataFrame, uniq_ex_nb: int = 5) -> None:
    """Get an rough analysis of the dataframe."""

    print("Columns contain:")

    # Get the size of the longer column name
    col_name_size = 0
    for col in df.columns:
        if len(col) > col_name_size:
            col_name_size = len(col)

    # Unique values str size
    uniq_val_size = len(str(len(df)))

    # How much row is there?
    print(f"Total number of rows: {df.shape[0]}")

    def display_ex(value):
        if len(str(value)) > 10:
            return str(value)[0:10] + "..."
        return str(value)

    # Discover each column (na number, unique values)
    nas = df.isna().sum().sort_values()
    for key, val in nas.items():
        to_print = "  - " + f'"{key}"'.rjust(col_name_size + 2) + ": "
        to_print += f"{percent(val / df.shape[0])} empty - "
        extract = "; ".join([display_ex(v) for v in df[key].unique()[:uniq_ex_nb]])
        uniq_nb = len(df[key].unique())
        uniq_prct = uniq_nb / df.shape[0]
        to_print += f"{uniq_nb}".rjust(uniq_val_size)
        to_print += f" ({percent(uniq_prct)}) uniques (eg: {extract})"
        print(to_print)
