import re


def get_n_grams(inputString: str, n: int = 3) -> set:
    """Get a set of all ngrams in the given string"""

    # Reformat
    inputString = inputString.replace("-", "").replace("'", "")

    # Get all words out of the input string
    words = [f"  {word} " for word in re.split(r"\W+", str(inputString).lower()) if word.strip()]

    # Generate all ngrams
    ngrams = set()
    for word in words:
        for x in range(0, len(word) - n + 1):
            ngrams.add(word[x : x + n])

    return ngrams

def compare_n_grams(n_grams1: set, n_grams2: set):
    """Function to be able to optimize computations"""
    return len(n_grams1 & n_grams2) / len(n_grams1 | n_grams2)


def trigram_similarity(string1: str, string2: str) -> float:
    """Calculate the similarity score of 2 strings, using they trigrams."""

    ngrams1 = get_n_grams(string1, 3)
    ngrams2 = get_n_grams(string2, 3)

    # number of trigram found in both string divided by the number of all unique trigrams
    return len(ngrams1 & ngrams2) / len(ngrams1 | ngrams2)