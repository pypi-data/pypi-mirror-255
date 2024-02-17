import pandas as pd
from loguru import logger


def merge_to_raw_df(raw_df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    """
    append the clean name to the original dataset and return the appended DataFrame.
    """

    dict_for_df = [
        {"first_plaintiff": k, "first_plaintiff_clean": v} for k, v in mapping.items()
    ]
    mapping_df = pd.DataFrame.from_dict(dict_for_df)
    merged_df = raw_df.merge(mapping_df, on=["first_plaintiff"])
    return merged_df


def map_values(aStr: str, aDict: dict) -> str:
    """
    Look up if str in dict otherwise return ""
    """

    try:
        return aDict[aStr]
    except KeyError:
        return ""


def combine_columns(clean, person, company):
    if company == "" and person == "":
        return clean

    if company != "" and person != "":
        logger.warning("NAME HAS BOTH COMPANY AND PERSON NAME: " + clean)
        return clean
    if company != "":
        return company

    if person != "":
        return person


def combine_columns_no_space(all_names, no_space):
    if no_space == "":
        return all_names

    return no_space
