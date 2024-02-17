from loguru import logger
import re
from tqdm import tqdm


def check_spaces(df):
    """takes in a list or df of one column and
    returns a dictionary of all names in the
    dataset that are found to be identical to at
    least one other name when all spaces are removed"""

    # Group data by exact matches and count the number of values
    logger.info("GROUPING DATA")
    grouped_df = (
        df.value_counts().rename_axis("first_plaintiff").reset_index(name="counts")
    )

    # Remove spaces and create new column
    grouped_df["no_space"] = grouped_df.apply(
        lambda x: re.sub(" +", "", x.first_plaintiff), axis=1
    )

    # See if no-space value is duplicate
    grouped_df["is_dup"] = grouped_df.duplicated(subset="no_space", keep=False)
    grouped_df = grouped_df[grouped_df.is_dup].reset_index()

    # sort dataframe for binary searching
    sorted_grouped_df = grouped_df.sort_values(by=["no_space"])
    duplicates_dict = {}

    # Get list of unique no_space names
    names = list(dict.fromkeys(grouped_df.no_space))

    # Iterate over unique no space names
    for name in tqdm(names):

        # binary search based on unique no space name
        indLeft = sorted_grouped_df["no_space"].searchsorted(name, "left")
        indRight = sorted_grouped_df["no_space"].searchsorted(name, "right")
        temp_df = sorted_grouped_df[indLeft:indRight]

        # Sort temp df created by counts, most frequently appearing term will come first
        temp_df = temp_df.sort_values(by=["counts"], ascending=False).reset_index()

        # Add the names into a dict, with the value that appears the most in the dataset as the version others are linked to
        for x in temp_df.first_plaintiff:

            duplicates_dict[x] = temp_df.first_plaintiff[0]

    return duplicates_dict
