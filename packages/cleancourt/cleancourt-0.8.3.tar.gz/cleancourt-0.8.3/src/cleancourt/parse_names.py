from loguru import logger
import probablepeople as pp
from tqdm import tqdm
import re

from cleancourt.filter_types import filter_people


def format_people_names(df, party_type = "None Specified"):

    """Take in a list or df of one column and return a dictionary with each name in First Last format"""

    if party_type not in ['company', 'person', 'None Specified']:
        logger.error('Company type must equal person, company or None')


    # Group data by exact matches and count the number of values
    logger.info("GROUPING DATA")
    grouped_df = (
        df.value_counts().rename_axis("first_plaintiff").reset_index(name="counts")
    )

    # Grab the names of each plaintiff and place into a list
    # Note: Order of this list does matter.
    # Names are prioritized based on the number of exact matches in the document

    names = grouped_df.first_plaintiff

    names_dict = {}

    # if party_type is company, no need to iterate 
    if party_type == 'company':
        return names_dict
    
    # Iterate over names
    for name in tqdm(names):

        # Check if name is a person

        if party_type == 'person':
            is_person = True

        else:
            # If no label is specified, use built in filter
            is_person = filter_people(name)

        # If is a person, grab name components from parsed names and place in a common format
        if is_person:
            
            # 7/25/2023 - added try catch to account for parsing errors in probable people. In these cases just skip parsing.
            success=False
            try:
                val = pp.tag(name)
                success = True
            except:
                names_dict[name] = name
            
            if success:
                try:
                    firstI = val[0]["FirstInitial"]
                except KeyError:
                    firstI = ""

                try:
                    prefOther = val[0]["PrefixOther"]
                except KeyError:
                    prefOther = ""


                try: # Update 0.7.8 first names are sometimes parsed as SuffixOther in probablepeople. this attempts to correct for that error
                    sufOther = val[0]["SuffixOther"]
                    if sufOther == 'dds' or sufOther == 'md' or sufOther == 'dmd' or sufOther == 'dpn':
                        sufOtherEnd = sufOther
                        sufOther = ""
                    else:
                        sufOtherEnd = ""

                except KeyError:
                    sufOther = ""
                    sufOtherEnd = ""


                try:
                    first = val[0]["GivenName"]
                except KeyError:
                    first = ""

                try:
                    middle = val[0]["MiddleName"]
                except KeyError:
                    middle = ""

                try:
                    middleI = val[0]["MiddleInitial"]
                except KeyError:
                    middleI = ""

                try:
                    last = val[0]["Surname"]
                except KeyError:
                    last = ""

                try:
                    lastI = val[0]["LastInitial"]
                except KeyError:
                    lastI = ""

                try:
                    suffix = val[0]["SuffixGenerational"]
                except KeyError:
                    suffix = ""

                full_name = ( # Add all of the parsed names together in a standard format
                    firstI
                    + " "
                    + prefOther
                    + " "
                    + first
                    + " "
                    + sufOther
                    + " "
                    + middle
                    + " "
                    + middleI
                    + " "
                    + last
                    + " " 
                    + lastI
                    + " "
                    + suffix
                    + " " 
                    + sufOtherEnd
                )

                names_dict[name] = re.sub(" +", " ", full_name.strip()) # Strip any extra white spaces

    return names_dict
