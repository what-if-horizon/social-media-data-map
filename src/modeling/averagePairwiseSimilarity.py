from itertools import combinations

import re
import unicodedata
import json

def standardize_strings(id_list):
    """
    Standardize a string by:
    - converting to lowercase
    - removing accents
    - stripping leading/trailing whitespace
    - replacing multiple whitespace with a single space
    - removing punctuation (except letters, numbers, and spaces)
    """
    for text in id_list:

        if text is None:
            return ""

        text = str(text)

        # Lowercase
        text = text.lower()

        # Remove accents
        text = unicodedata.normalize("NFKD", text)
        text = "".join(c for c in text if not unicodedata.combining(c))

        # Remove punctuation
        text = re.sub(r"[^\w\s]", "", text)

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()

    return id_list

def jaccard_similarity(a, b):
    set_a = set(a)
    set_b = set(b)
    # intersection of two sets
    intersection = len(set_a.intersection(set_b))
    # Unions of two sets
    union = len(set_a.union(set_b))
    
    return intersection / union

def dice_coefficient(a, b):
    """
    Compute the Dice coefficient between two collections.

    Parameters
    ----------
    a, b : iterable
        Lists, sets, tuples, etc.

    Returns
    -------
    float
        Dice coefficient in [0, 1].
    """
    set_a = set(a)
    set_b = set(b)

    if not set_a and not set_b:
        return 1.0

    intersection = len(set_a & set_b)

    return (2 * intersection) / (len(set_a) + len(set_b))



def avg_pair_sim(df, compare_column):

    js_total = 0
    total = len(df)-1
    for (i1, row1), (i2, row2) in combinations(df.iterrows(), 2):
        value1 = standardize_strings(json.loads(row1[compare_column]))
        value2 = standardize_strings(json.loads(row2[compare_column]))

        js = jaccard_similarity(value1, value2)
        js_total = js_total + js

    avg_js = js_total/total
    return avg_js
    

    




