"""Pandas utility functions."""

from typing import List, Dict, Any

import pandas as pd


def combine_collumns(
    df: pd.DataFrame,
    column_names: List[str],
    catergory_col_name: str,
    value_col_name: str,
) -> pd.DataFrame:
    """
    Combine multiple columns into two columns, one for the category and one for the value.

    Args:
        df: The dataframe to combine the columns from.
        column_names: The columns to combine.
        catergory_col_name: The name of the column for the category.
        value_col_name: The name of the column for the value.

    Returns:
        A new dataframe with the combined columns.
    """
    for col in column_names:
        assert col in df.columns, f"Column {col} not found in dataframe!"

    df_column_names = df.columns

    other_column_names = list(filter(lambda x: x not in column_names, df_column_names))

    df_new_column_names = other_column_names.copy()

    df_new_column_names.append(catergory_col_name)
    df_new_column_names.append(value_col_name)

    data: Dict[str, Any] = {col_name: [] for col_name in df_new_column_names}

    for index in df.index:
        row = df.loc[index]
        column_values = [row[col_name] for col_name in column_names]

        for col_name, col_value in zip(column_names, column_values):
            data[catergory_col_name].append(col_name)
            data[value_col_name].append(col_value)

            for col_name in other_column_names:
                data[col_name].append(row[col_name])

    return pd.DataFrame(data)
