import numpy as np
import pandas as pd
from collections import Counter
from collections import defaultdict

def single_headline_grams(n, headline):
    """Generates grams for a single headline.

    Returns a dictionary that maps histories (phrase of words) to a list of
    tuples that describe how likely it is for another phrase to follow.

    Also makes the headline all lowercase and removes special characters.

    Parameters
    ----------
    n: int
        Value of n for language model.
    headlines: str
        A single Florida man headline.
    """
    counts = defaultdict(Counter)
    history = ("~ " * n).strip()
    headline = headline.split()
    for word in headline:
        counts[history][word] += 1
        history = history.split()[1:] + [word]
        history = " ".join(history)
    return counts

def combine_two_headlines(headline_1, headline_2):
    """Combines two headline dictionaries into one dictionary.

    Destructively mutates headline_1.

    Parameters
    ----------
    headline_1: dictionary
        Key-value pair is string, Counter
    headline_2: dictionary
        Key-value pair is string, Counter
    """
    for phrase, next_words in headline_2.items():
        if phrase in headline_1:
            headline_1[phrase] = next_words + headline_1[phrase]
        else:
            headline_1[phrase] = next_words
    return headline_1

def normalize_counts(counter):
    """Normalizes the counts of a counter.

    Parameters
    ----------
    counter: Counter
        The aggregate counts of how often each following word shows up.
    """
    total = sum(counter.values())
    return [(word, count / total) for word, count in counter.most_common()]

def generate_grams(n, entries):
    """Aggregates grams for every headline.

    Normalizes the counts for each phrase afterwards.

    Parameters
    ----------
    n: int
        Value of n for language model.
    entries: pandas DataFrame
        A pandas Dataframe containing the Florida man headlines.
    """
    # Getting counts for each headline
    headline_counts = []
    for headline in entries["title"]:
        headline_count = single_headline_grams(n, headline)
        headline_counts.append(headline_count)

    # Aggregating headlines into one language model
    headline_aggregate = headline_counts[0]
    headline_counts = headline_counts[1:]
    for headline in headline_counts:
        combine_two_headlines(headline_aggregate, headline)

    # Normalizing counts
    for phrase, counter in headline_aggregate.items():
        headline_aggregate[phrase] = normalize_counts(counter)

    return headline_aggregate

def generate_headline(n, headline_aggregate):
    """Generates a headline using the language model.

    Parameters
    ----------
    n: int
        Value of n for language model.
    headline_aggregate: dictionary
        A dictionary of histories and corresponding frequencies for following words.
    """
    history = ("~ " * n).strip()
    headline = ""

    next_word = generate_word(headline_aggregate, history)
    history = (history[1:] + " " + next_word).strip()
    headline += next_word + " "
    while next_word != "":
        next_word = generate_word(headline_aggregate, history)
        history = history.split()[1:]
        history.append(next_word)
        history = " ".join(history).strip()
        headline += next_word + " "
    return headline.strip()

def generate_word(headline_aggregate, history):
    """Generates a word using the language model and preceding history.

    Parameters
    ----------
    headline_aggregate: dictionary
        A dictionary of histories and corresponding frequencies for following words.
    history: str
        A history of the last observed words.
    """
    if history not in headline_aggregate:
        return ""
    next = headline_aggregate[history]
    words = []
    p = []
    for frequency in next:
        words.append(frequency[0])
        p.append(frequency[1])
    return np.random.choice(words, p=p)

def is_valid_headline(headline, entries):
    """Checks that headline is valid.

    Checks that headline is not identical to any headline in the training data,
    that the headline is between 5 and 20 words, and that 'florida man' is in
    the headline.

    Parameters
    ----------
    headline: str
        Language model generated headlines
    entries: DataFrame
        A DataFrame containing all headline entries.
    """
    return headline not in list(entries["title"])\
        and len(headline.split()) > 5\
        and len(headline.split()) < 20\
        and "florida man" in headline
