import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from scipy.sparse import csr_matrix
import sparse_dot_topn.sparse_dot_topn as sdt
from loguru import logger
from tqdm import tqdm
from rapidfuzz import process

from cleancourt.compute_ngrams import ngrams
from cleancourt.filter_types import filter_companies

MAX_NAME_LEVENSHTEIN = 500
SIMILARITY_SCORE_WEIGHT = 1.16
MAX_NAMES_TO_LINK = 1000

# HELPER FUNCTIONS

# Associate the indexes returned from the sparse matrix with actual names
def _get_matches_df(sparse_matrix, name_vector, top=-1):

    """take in sparse matrix, set of names, and max number of indexes to read (for testing)
    return a dataframe of names associated with each index in the sparse matrix, along with the
    similarity score between each function"""

    non_zeros = sparse_matrix.nonzero()
    sparserows = non_zeros[0]
    sparsecols = non_zeros[1]

    # Computationally intensive method.
    # For testing purposes, pass value to top to limit the search
    if top != -1:
        nr_matches = top
    else:
        nr_matches = sparsecols.size

    # establish numpy arrays for each of the columns in the returned dataset
    left_side = np.empty([nr_matches], dtype=object)
    right_side = np.empty([nr_matches], dtype=object)
    similarity = np.zeros(nr_matches)

    # grab the name at each index and place into the array for each value
    for index in range(0, nr_matches):
        left_side[index] = name_vector[sparserows[index]]
        right_side[index] = name_vector[sparsecols[index]]
        similarity[index] = sparse_matrix.data[index]

    # return a dataframe of the numpy arrays
    return pd.DataFrame(
        {"left_side": left_side, "right_side": right_side, "similarity": similarity}
    )


def _conduct_cos_sim(A, B, ntop, lower_bound=0):

    """'Cosine similarity function similar to that provided by sklearn
    Two crucial differences:
    1. This version does not do type checking or error handling, which is computationally intensive
    2. This version does not store values below a certain threshold (saving on memory)
    ntop is the max number of similar values to return, and the lower_bound is the minimum threshold of similarity between values to include
    Method taken from example in sparse_dot_topn library (linked below)

    returns a matrix in CSR format
    where the sorted results with similariteis are greater than the lower bound

    """

    A = A.tocsr()
    B = B.tocsr()
    M, _ = A.shape
    _, N = B.shape

    # Set dtype for np arrays
    idx_dtype = np.int32

    # determine size of matrix
    nnz_max = M * ntop

    # Populate matrix values with zeros
    indptr = np.zeros(M + 1, dtype=idx_dtype)
    indices = np.zeros(nnz_max, dtype=idx_dtype)
    data = np.zeros(nnz_max, dtype=A.dtype)

    # create sparse matrix resulting from the matrices passed
    # https://github.com/ing-bank/sparse_dot_topn
    sdt.sparse_dot_topn(
        M,
        N,
        np.asarray(A.indptr, dtype=idx_dtype),
        np.asarray(A.indices, dtype=idx_dtype),
        A.data,
        np.asarray(B.indptr, dtype=idx_dtype),
        np.asarray(B.indices, dtype=idx_dtype),
        B.data,
        ntop,
        lower_bound,
        indptr,
        indices,
        data,
    )

    return csr_matrix((data, indices, indptr), shape=(M, N))


## MAIN CODE
def link_company_names(df, min_similarity_score=0.80, party_type = 'None Specified'):

    """Take in a df of 1 column or a list and a minimum similarity score cutoff and return a dictionary with each of the doc"""

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

    # create list of only company names

    # if party label is person, just return an empty dict
    if party_type == 'person':
        return {}
    elif party_type != 'company':
        names = [name for name in names if filter_companies(name)]

    # If there are fewer than 500 unique names in the list, compute similarity between strings using levenshtein distance
    if len(names) < MAX_NAME_LEVENSHTEIN:
        # To allow users to submit a similarity threshold that will return similar cutoffs for both methods, we multiply 1.16 as
        # a slightly higher threshold is required for levenshtein.
        min_similarity_score = min_similarity_score * SIMILARITY_SCORE_WEIGHT

        # must assert that the similarity score is never more than 100
        min_similarity_score = min(100, (min_similarity_score * 100))

        return _link_company_names_levenshtein(names, min_similarity_score)

    else:
        return _link_company_names_tfidf_cos(names, min_similarity_score)


def _link_company_names_levenshtein(names, min_similarity_score):

    """helper function for computing similarity using the levenshtein distance"""

    duplicates_dict = {}

    # Iterate over company names
    for name in names:

        # employ rapid fuzz to grab a list of names that are more than 80% similar to the name in question
        matches = process.extract(
            name, names, processor=None, score_cutoff=min_similarity_score
        )

        if matches:

            match_names = [match[0] for match in matches if match[0] != name]

            # If the name being iterated on is already in the dataset, grab the value and use that as the new value for the duplicates dictionary
            try:
                linked_name = duplicates_dict[name]
            except KeyError:
                linked_name = name

            for aName in match_names:
                duplicates_dict[aName] = linked_name

    return duplicates_dict


def _link_company_names_tfidf_cos(names, min_similarity_score):

    """helper function for computing similarity using the TFIDF and cosine similarity"""

    # Vectorize and transform the data into a series of ngrams
    logger.info("VECTORIZING")
    vectorizer = TfidfVectorizer(min_df=1, analyzer=ngrams)
    logger.info("TRANSFORMING")
    tf_idf_matrix = vectorizer.fit_transform(names)

    # Pass to cosine function, take top 10 pairs and only pairs with a similarity above 80%
    logger.info("CONDUCTING COSINE SIMILARITY... This may take a second")
    matches = _conduct_cos_sim(
        tf_idf_matrix,
        tf_idf_matrix.transpose(),
        MAX_NAMES_TO_LINK,
        min_similarity_score,
    )

    # Get the values returned from the indices of the sparse matrix and return as a data frame of word1, word2, similarity
    logger.info("GRABBING VALUES FROM SPARSE MATRIX INDICES")
    matches_df = _get_matches_df(matches, names, top=-1)

    # Pairs with themselves will be included in the df with a similarity of .9999999999.
    # These will need to be removed
    logger.info("REMOVING EXACT MATCHES")
    matches_df = matches_df[
        matches_df["similarity"] < 0.99999
    ]  # Remove all exact matches

    # Add this information into a dict to be returned to the user where
    # the key is the original word and the value is the word that that value should be mapped to
    logger.info("MERGING TO DICT")
    duplicates_dict = {}
    added_names = []

    # Sort values for binary search using string match
    logger.info("ITERATING OVER NAMES")
    matches_df = matches_df.sort_values(by=["left_side"])

    # Begin looping over the ordered names in the dataset and placing into dict
    for name in tqdm(names):

        # Search the existing dataset and see if the name already exists in dictionary.
        try:
            # If so, change linked_name to output that value, which grabs the root value
            linked_name = duplicates_dict[name]
        except KeyError:
            # Otherwise you have a root value, assign that to linked_name
            linked_name = name

        # Conduct a binary search across the dataset
        # Basically this is a really really fast way to filter a dataset based off of exact string matches.
        # The slower equivalent of these three lines is temp_df = matches_df[matches_df.left_side == name]
        indLeft = matches_df["left_side"].searchsorted(name, "left")
        indRight = matches_df["left_side"].searchsorted(name, "right")
        temp_df = matches_df[indLeft:indRight]

        # create a temporary dictionary of all key/value pairs for `name` if name is the root name or names value in the dictionary if it exists
        temp_dict = dict(
            zip(temp_df.right_side, [linked_name] * len(temp_df.right_side))
        )

        # Merge the temporary dectionary with the larger dictionary.
        # Note the `|` (merge) operator requires python 3.9 or above
        duplicates_dict = temp_dict | duplicates_dict

    return duplicates_dict
