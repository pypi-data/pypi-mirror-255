from loguru import logger
import pandas as pd


from cleancourt.check_spaces import *
from cleancourt.clean_data import *
from cleancourt.cosine_similarity import *
from cleancourt.integrate_output import *
from cleancourt.parse_names import *
from cleancourt.separate_parent_company import separate_company_names


def full_clean_names(messy_names, separate_management=False, min_similarity_score=0.80, party_type = "None Specified"):
    
    '''This is an abstracted function that calls the clean names function in CC in the order that they are intended to be called.'''

    if party_type not in ['company', 'person', 'None Specified']:
        logger.error('Company type must equal person, company or None')



    if not separate_management:
        df = pd.DataFrame()

        df["clean_names_1"] = [clean_data(x) for x in tqdm(messy_names)]

        # Parse the people names and format
        logger.info("PARSING PEOPLE NAMES")
        duplicates_dict_people = format_people_names(df["clean_names_1"], party_type)

        # Merge names into df
        logger.info("MERGING PEOPLE NAMES")
        df["formatted_people_names"] = df.apply(
            lambda x: map_values(x.clean_names_1, duplicates_dict_people), axis=1
        )

        # Parse company names
        logger.info("PARSING COMPANY NAMES")
        duplicates_dict_company = link_company_names(
            df["clean_names_1"], min_similarity_score, party_type
        )

        # Merge company names into df
        logger.info("MERGING COMPANY NAMES")
        df["formatted_company_names"] = df.apply(
            lambda x: map_values(x.clean_names_1, duplicates_dict_company), axis=1
        )

        # Create column of all company and people names
        logger.info("ADDING ALL NAMES TO DF")
        df["clean_names_2"] = df.apply(
            lambda x: combine_columns(
                x.clean_names_1, x.formatted_people_names, x.formatted_company_names
            ),
            axis=1,
        )

        # Check for erroneous spaces that may prevent names from being matched
        logger.info("CHECKING SPACES")
        duplicates_dict_spaces = check_spaces(df["clean_names_2"])

        # add values returned from no spaces to df
        logger.info("ADDING NO SPACES NAMES TO DF")
        df["clean_names_3"] = df.apply(
            lambda x: map_values(x.clean_names_2, duplicates_dict_spaces), axis=1
        )

        # Combine all cleaned names columns into one column for use
        df["clean_name_final"] = df.apply(
            lambda x: combine_columns_no_space(x.clean_names_2, x.clean_names_3), axis=1
        )

        return df["clean_name_final"]
    else:
        df = pd.DataFrame()

        df["clean_names_1"] = [clean_data(x) for x in tqdm(messy_names)]

        logger.info("SEPARATING MANAGING NAMES")
        df["nameA"], df["nameB"] = separate_company_names(df["clean_names_1"])

        # Parse the people names and format
        logger.info("PARSING PEOPLE NAMES")
        duplicates_dict_peopleA = format_people_names(df["nameA"], party_type)
        duplicates_dict_peopleB = format_people_names(df["nameB"], party_type)

        # Merge names into df
        logger.info("MERGING PEOPLE NAMES")
        df["formatted_people_namesA"] = df.apply(
            lambda x: map_values(x.nameA, duplicates_dict_peopleA), axis=1
        )
        df["formatted_people_namesB"] = df.apply(
            lambda x: map_values(x.nameB, duplicates_dict_peopleB), axis=1
        )

        # Parse company names
        logger.info("PARSING COMPANY NAMES")
        duplicates_dict_companyA = link_company_names(df["nameA"], min_similarity_score, party_type)
        duplicates_dict_companyB = link_company_names(df["nameB"], min_similarity_score, party_type)

        # Merge company names into df
        logger.info("MERGING COMPANY NAMES")
        df["formatted_company_namesA"] = df.apply(
            lambda x: map_values(x.nameA, duplicates_dict_companyA), axis=1
        )
        df["formatted_company_namesB"] = df.apply(
            lambda x: map_values(x.nameB, duplicates_dict_companyB), axis=1
        )

        # Create column of all company and people names
        logger.info("ADDING ALL NAMES TO DF")
        df["clean_names_2a"] = df.apply(
            lambda x: combine_columns(
                x.nameA, x.formatted_people_namesA, x.formatted_company_namesA
            ),
            axis=1,
        )
        df["clean_names_2b"] = df.apply(
            lambda x: combine_columns(
                x.nameB, x.formatted_people_namesB, x.formatted_company_namesB
            ),
            axis=1,
        )

        # Check for erroneous spaces that may prevent names from being matched
        logger.info("CHECKING SPACES")
        duplicates_dict_spacesA = check_spaces(df["clean_names_2a"])
        duplicates_dict_spacesB = check_spaces(df["clean_names_2b"])

        # add values returned from no spaces to df
        logger.info("ADDING NO SPACES NAMES TO DF")
        df["clean_names_3a"] = df.apply(
            lambda x: map_values(x.clean_names_2a, duplicates_dict_spacesA), axis=1
        )
        df["clean_names_3b"] = df.apply(
            lambda x: map_values(x.clean_names_2b, duplicates_dict_spacesB), axis=1
        )

        # Combine all cleaned names columns into one column for use
        df["clean_name_finalA"] = df.apply(
            lambda x: combine_columns_no_space(x.clean_names_2a, x.clean_names_3a),
            axis=1,
        )
        df["clean_name_finalB"] = df.apply(
            lambda x: combine_columns_no_space(x.clean_names_2b, x.clean_names_3b),
            axis=1,
        )

        return (df["clean_name_finalA"], df["clean_name_finalB"])


# Same as the full clean names function, only this function separates the company names by DBA/TA names
# In future iterations, this method will replace full_clean_names
def full_clean_names1(messy_names):
    logger.error(
        "full_clean_names1 deprecated in cleancourt 0.6.0 use full_clean_names with separate_management=True"
    )
    quit()
