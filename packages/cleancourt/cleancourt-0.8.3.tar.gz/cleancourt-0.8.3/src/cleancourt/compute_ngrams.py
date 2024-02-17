def ngrams(string, n=3):
    """take in string and create ngrams of length 3 for TF-IDF vectorization"""
    ngrams = zip(*[string[i:] for i in range(n)])
    return ["".join(ngram) for ngram in ngrams]
