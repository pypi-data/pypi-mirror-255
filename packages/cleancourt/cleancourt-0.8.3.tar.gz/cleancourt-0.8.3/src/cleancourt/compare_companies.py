from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from loguru import logger
from sklearn.neighbors import NearestNeighbors

from cleancourt.compute_ngrams import ngrams
from cleancourt.filter_types import filter_companies
from cleancourt.clean_data import clean_data


SIMILARITY_DISTANCE = 0.25


def _print_matches(distances, indices, org_name_messy, org_name_clean):
    """Print function to see output of matches"""

    all_matches = [
        (round(distances[i][0], 2), org_name_messy[i], org_name_clean[j[0]])
        for i, j in enumerate(indices)
    ]
    all_matches = pd.DataFrame(all_matches, columns=["score", "original", "matched"])

    all_matches.to_csv("data/ignore_all_matches.csv")


def compare_companies(
    org_name_messy,
    org_name_clean,
    threshold=SIMILARITY_DISTANCE,
    print_all_matches=False,
    clean_org_names=[False, False],
    all_companies = False
):
    """This method implements a K-Nearest Neighbors (KNN) algorithm to
    compare a standard list of *clean* party names to a *messy* list of
    party names.

    With KNN algorithms, individual (new) data points are added to an existing
    dataset, and the "distance" to all other points in the dataset is computed.

    "Distance" is measured using TFIDF and cosine similarities similarly to the link_company_names_function.

    """

    # Remove people from the list of names, unless you are already passing a list of companies
    if not all_companies:
        org_name_messy = [name for name in org_name_messy if filter_companies(name)]

    # Clean data in both lists if optional parameters are set to true
    if clean_org_names[0]:
        logger.info("Cleaning Messy Org Dataset")
        org_name_messy = [clean_data(name) for name in org_name_messy]
    if clean_org_names[1]:
        logger.info("Cleaning Clean Org Dataset")
        org_name_clean = [clean_data(name) for name in org_name_clean]

    logger.info("Vectorizing and Transforming Clean Names")

    # Create a sparse matrix of "ngrams" across the list of clean names.
    # Output of tfidf sparse matrix (and what you would see if you ran print(tfidf)) is below:
    # The tuple represents: (clean_name id, ngram id)
    # The value following the tuple represents the tf-idf score of a given ngram in a given clean_name
    # The tuples that are not there have a tf-idf score of 0
    vectorizer = TfidfVectorizer(analyzer=ngrams, lowercase=True)
    tfidf = vectorizer.fit_transform(org_name_clean)

    logger.info("Computing Nearest Neighbor Algorithm")

    # This model uses the cosine similarity metric and the brute force metric
    # This algorithm was chosen to produce similar output based on other comparitors in this library.
    # However, in cases with extrememly large clean_names, this will be an inefficient method for computing
    # as the brute force method computes the distances between all pairs of points in the dataset.

    # n_neighbors is set to 1 as we are only concerned with pulling the closest company name
    # n_jobs is set to run to allow process to run in parallel using all processors

    nbrs = NearestNeighbors(
        n_neighbors=1, metric="cosine", algorithm="brute", n_jobs=-1
    ).fit(tfidf)

    # Returns the distance to the next closest neighbor in the geographic plain,
    # Also returns the index in the list of the closest neighbor in the clean data set
    distances, indices = nbrs.kneighbors(vectorizer.transform(org_name_messy))

    if print_all_matches:
        _print_matches(distances, indices, org_name_messy, org_name_clean)

    logger.info("Pairing Names")

    # Creates a dict that pairs the messy_name with the closest clean name
    # Only adds the values to a dict if they are below a certain distance as determined by SIMILARITY_DISTANCE
    # Also add the score to a dict and return
    matches = {}
    scores = {}
    for i in range(0, len(indices)):
        if distances[i][0] < threshold:
            matches[org_name_messy[i]] = org_name_clean[indices[i][0]]
            scores[org_name_messy[i]] = str(distances[i][0])

    return matches, scores
