"""
Takes headlines from specified csv files and generates new headlines using n-grams model.
"""

import numpy as np
import pandas as pd
import re
from collections import Counter
from collections import defaultdict

# specify training directory here
directory = "training_data/"

# specify csv file name here
filenames = ["local10_headlines.csv", "floridaman_com_headlines.csv"]

# specify what value of n to use here
n = 2

def load_files(filenames):
    """Takes a list of file names for .csv files and returns a DataFrame.

    Parameters
    ----------
    filenames: list of strings
        A list of strings containing the names of .csv files for headline data.
    """
    df = pd.DataFrame(columns=["title", "link"])
    for filename in filenames:
        df = df.append(pd.read_csv(directory + filename), ignore_index=True)
    df = df.drop_duplicates()
    df["title"] = [clean_headline(headline) for headline in df["title"]]
    return df

def clean_headline(headline):
    """Cleans the headline.

    For now, all this function does is change headline to lowercase.

    Parameters
    ----------
    headline: str
        A headline to clean.
    """
    return headline.lower()

def single_headline_grams(headline):
    """Generates grams for a single headline.

    Returns a dictionary that maps histories (phrase of words) to a list of
    tuples that describe how likely it is for another phrase to follow.

    Also makes the headline all lowercase and removes special characters.

    Parameters
    ----------
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

def generate_grams(entries):
    """Aggregates grams for every headline.

    Normalizes the counts for each phrase afterwards.

    Parameters
    ----------
    entries: pandas DataFrame
        A pandas Dataframe containing the Florida man headlines.
    """
    # Getting counts for each headline
    headline_counts = []
    for headline in entries["title"]:
        headline_count = single_headline_grams(headline)
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

def generate_headline(headline_aggregate):
    """Generates a headline using the language model.

    Parameters
    ----------
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

def is_valid_headline(headline):
    """Checks that headline is valid.

    Checks that headline is not identical to any headline in the training data,
    that the headline is longer than 4 words, and that 'florida man' is in the
    headline.

    Parameters
    ----------
    headline: str
        Language model generated headlines
    """
    return headline not in list(entries["title"])\
        and len(headline.split()) > 4\
        and "florida man" in headline

def print_headlines(headline_aggregate):
    """Prints headlines based on user's prompt.

    Parameters
    ----------
    headline_aggregate: dictionary
        A dictionary of histories and corresponding frequencies for following words.
    """
    # Greeting prompt
    print(
    """
    Hello! This program uses a n-grams language model to generate 'Florida Man'
    headlines. Currently, we are using the following .csv files as training
    data for our model: {0}

    Additionally, the value of n is currently {1}. This can be modified in
    n_grams_lm.py.

    """.format(filenames, n)
    )

    # Getting counts and generating headlines
    headline_count = input("How many headlines would you like to generate? ")
    while type(headline_count) != int:
        try:
            headline_count = int(headline_count)
        except:
            print("\nPlease enter a postive integer.")
            headline_count = input("How many headlines would you like to generate? ")
    print()
    successfully_generated_count = 0
    already_generated = set()
    while (successfully_generated_count < headline_count):
        headline = generate_headline(headline_aggregate)
        if is_valid_headline(headline) and headline not in already_generated:
            already_generated.add(headline)
            successfully_generated_count += 1
            print(headline)

if __name__ == "__main__":
    entries = load_files(filenames)
    headline_aggregate = generate_grams(entries)
    print_headlines(headline_aggregate)