import pandas as pd
import traceback
from pprint import pprint

def write_to_csv(content, filename):
    """Writes list to a .csv file specified by filename.

    Parameters
    ----------
    content: pandas DataFrame
        A DataFrame containing titles and links for all headlines.
    filename:
        The name of the file the string is being written into.
    """
    content = content.drop_duplicates()
    content.to_csv(filename, index=False)

    print("Scraped {} sources.".format(len(content.index)))
    print("Saving currently scraped results in '{}'.".format(filename))

def load_files(filenames):
    """Takes a list of file names for .csv files and returns a DataFrame with all entries combined.

    Parameters
    ----------
    filenames: list of strings
        A list of strings containing the names of .csv files for headline data.
    """
    df = pd.DataFrame(columns=["title", "link"])
    for filename in filenames:
        df = df.append(pd.read_csv(training_directory + filename), ignore_index=True, sort=False)
    df = df.drop_duplicates()
    df["title"] = [clean_headline(headline) for headline in df["title"]]
    return df

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

def print_soup(soup, log_file = None):
    """Pretty prints soup to log_file. Used for debugging only. 

    Parameters
    ----------
    soup: Soup
        Soup to be pprinted.  
    log_file: file
        File for soup to be printed to. Default None indicates printed to stdout.
    """
    soup = soup.prettify().encode("utf-8")
    if log_file is None:
        pprint(soup)
    else:
        pprint(soup, log_file)
