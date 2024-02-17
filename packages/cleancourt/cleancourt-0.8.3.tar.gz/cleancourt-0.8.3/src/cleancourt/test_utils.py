import pandas as pd


def generate_diagnostics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a DataFrame with diagnostics to understand how the standardization process impacts the raw data.

    This function groups the output data by the standardized plaintiff name and aggregates the raw values into a string
    to make it easier to visually inspect the output. This method also adds a count of the number of raw values that were standardized
    to the same value.

    """
    count_raw_names_by_clean_name = (
        df.groupby("first_plaintiff_clean")
        .agg(
            count_first_plaintiff=("first_plaintiff", "nunique"),
            values_first_plaintiff=("first_plaintiff", lambda x: ",".join(x)),
        )
        .reset_index()
    )

    return count_raw_names_by_clean_name
