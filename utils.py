from os import listdir 
from os.path import isfile, join
import pandas as pd
import traceback
from pprint import pprint
import re

MIN_WORDS = 5
MAX_WORDS = 20

def get_files(training_directory, path):
    """Returns list of file names in directory specified by path. 

    Parameters
    ----------
    training_directory: string
        Directory with training data inside.
    path: string
        Directory path to get files from. 
    """
    return [f for f in listdir(path) if isfile(join(training_directory, f))]

def handle_exception(exception, msg=None): 
    """Handles exceptions and logs error message. For now, just prints error to stdout. 

    Parameters
    ----------
    exception: Exception
        Exception to be logged.
    """
    print("\nIncurred the following error:\n" if msg is None else msg)
    if exception is None:
        print(traceback.format_exc())
    else:
        print(exception)

def load_files(training_directory, filenames):
    """Takes a list of file names for .csv files and returns a DataFrame with all entries combined.

    Parameters
    ----------
    training_directory: string
        Directory with training data inside.
    filenames: list of strings
        A list of strings containing the names of .csv files for headline data.
    """
    clean_headline = lambda headline: headline.strip().lower()
    df = pd.DataFrame(columns=["title", "link"])
    for filename in filenames:
        df = df.append(pd.read_csv(training_directory + filename), ignore_index=True, sort=False)
    df = df.drop_duplicates()
    df["title"] = [clean_headline(headline) for headline in df["title"]]
    return df

def option_mux(message, options):
    """Prompts user with message, compares user input with options to decide which function to execute.

    Parameters
    ----------
    message: string
        Message prompt shown to user before input is taken. 
    options: dictionary (string, function)
        Maps strings (compared to user's input) to functions with no args. 
    """
    user_choice = None
    while user_choice not in options:
        user_choice = input(message).lower().strip()
        if user_choice in options:
            return options[user_choice]
        else:
            print("Not a valid option; please enter a valid keyword.\n")

def print_soup(soup, log_file = None):
    """Pretty prints soup to log_file. Used for debugging only. 

    Parameters
    ----------
    soup: Soup
        Soup to be pretty printed.
    log_file: file
        File for soup to be printed to. Default None indicates printed to stdout.
    """
    soup = soup.prettify().encode("utf-8")
    if log_file is None:
        pprint(soup)
    else:
        pprint(soup, log_file)

def validate_headline(headline, entries):
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
        and len(headline.split()) >= MIN_WORDS\
        and len(headline.split()) <= MAX_WORDS\
        and "florida man" in headline

def write_to_text(content, filename):
    """Saves content to a .txt file specified by filename.

    Parameters
    ----------
    content: list
        A list of strings, where each item will be written to a separate line.
    filename: string
        Name of the file the content is being written to. 
    """
    f = open(filename, "w")
    f.writelines([line + "\n" for line in content])
    f.close()

def write_to_csv(content, filename):
    """Writes list to a .csv file specified by filename.

    Parameters
    ----------
    content: pandas DataFrame
        A DataFrame containing titles and links for all headlines.
    filename: string
        The name of the file the content is being written into.
    """
    content = content.drop_duplicates()
    content.to_csv(filename, index=False)
    print("Scraped {} sources.".format(len(content.index)))
    print("Saving currently scraped results in '{}'.".format(filename))
