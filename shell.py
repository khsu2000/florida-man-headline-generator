from collections import Counter
from collections import defaultdict
import ngrams_lm
import numpy as np
import pandas as pd
import utils

def init_shell():
    """Assigns initial values to global variables. Global variables are defined here.

    Parameters
    ----------
    None
    """
    # Value of n for n-grams language model 
    global n
    # Directory that training_data is stored in 
    global training_directory
    # List of files the language model is currently using
    global used_files
    n = 2
    training_directory = "./training_data/"
    used_files = ["cbs_miami_headlines.csv", "floridaman_site_headlines.csv", "local10_headlines.csv", "user_headlines.csv"]

def greeting(entries):
    """Prints out the greeting message.

    Parameters
    ----------
    entries: DataFrame
        A DataFrame containing all headline entries.
    filenames: list
        A list of .csv files that the headlines were read from. 
    """
    print("Hello! This program uses a n-grams language model to generate `Florida Man` headlines. Currently, we have {0} total headlines scraped from various news sources and are using the following .csv files as training data for our model: {1}".format(len(entries.index), used_files))

def get_seed():
    """Sees if user wants to enter a seed to fix numpy randomness.

    Parameters
    ----------
    None
    """
    seed = input("\n[OPTIONAL] Enter an integer seed: ")
    try:
        seed = int(seed)
        np.random.seed(seed)
        print("Done! Random seed is set to {}.\n".format(seed))
    except:
        print("Continuing without seed.\n")

def set_n(headline_aggregate, entries):
    """Changes the value of n. Returns the newly trained headline_aggregate.

    Parameters
    ----------
    headline_aggregate: dictionary
        A dictionary of histories and corresponding frequencies for following words.
    entries: DataFrame
        A DataFrame containing all headline entries.
    """
    global n
    user_n = input("Enter a new value for n (must be a positive integer): ")
    try:
        user_n = int(user_n)
        if user_n < 1:
            raise
        n = user_n
        print("Done! n is now {}.\n".format(n))
        return (ngrams_lm.generate_grams(n, entries), entries)
    except:
        print("Invalid value for n; did not update n.\n")

def print_headlines(headline_aggregate, entries):
    """Prints headlines based on user's prompt.

    Prompts user to see if headlines should be saved to a text file at the end.
    Additionally, if print_headlines fails to generate a headline after too many
    attempts, print_headlines will automatically stop.

    Parameters
    ----------
    headline_aggregate: dictionary
        A dictionary of histories and corresponding frequencies for following words.
    entries: DataFrame
        A DataFrame containing all headline entries.
    """
    # Limit on how many attempts at headline construction are allowed
    consecutive_invalid_limit = 2000
    headline_count = input("How many headlines would you like to generate? ")
    try:
        headline_count = int(headline_count)
        if headline_count < 1:
            raise Exception()
    except:
        print("Could not interpret input as positive integer.\n")
        return
    print()
    successfully_generated_count = 0
    consecutive_invalid_count = 0
    headlines = set()
    while len(headlines) < headline_count:
        headline = ngrams_lm.generate_headline(n, headline_aggregate)
        if utils.validate_headline(headline, entries):
            old_size = len(headlines)
            headlines.add(headline)
            if len(headlines) > old_size:
                consecutive_invalid_count = 0
                print("{0}. {1}".format(len(headlines), headline))
        elif consecutive_invalid_count >= consecutive_invalid_limit:
            print("\nFailed to construct headline after {} attempts. Try decreasing n or adding more training data.".format(consecutive_invalid_count))
            break
        else:
            consecutive_invalid_count += 1
    save_check = input("\nDo you want to save these headlines to a text file? [y/n] ").lower().strip()
    if save_check == "yes" or save_check == "y":
        filename = ""
        invalid_chars = ("\\", "/", ":", "*", "?", "\"", "<", ">", "|", " ")
        is_valid_fname = lambda fname: len(fname) > 0 and (sum([c in fname for c in invalid_chars]) == 0)
        while not is_valid_fname(filename):
            filename = input("Please enter a file name: ").lower().strip()
            if not is_valid_fname(filename):
                print("\nFile name cannot contain the following characters: {}".format(invalid_chars))
        if filename[-4:] != ".txt":
            filename += ".txt"
        utils.write_to_text(headlines, filename)
        print("Finished writing headlines to {}".format(filename))
    print()

def add_headline(headline_aggregate, entries):
    """Allows user to add custom headlines in separate .csv file.

    Returns updated headline_aggregate and entries. All user added headlines are
    saved inside user_headlines.csv.

    Parameters
    ----------
    headline_aggregate: dictionary
        A dictionary of histories and corresponding frequencies for following words.
    entries: DataFrame
        A DataFrame containing all headline entries.
    """
    user_headlines = pd.read_csv(training_directory + "user_headlines.csv")
    print("All user-added `Florida Man` headlines will be saved to `training_data/user_headlines.csv`. There are currently {} entries in user_headlines.csv.\n".format(len(user_headlines.index)))
    user_headline = input("Please enter a valid headline (enter `quit` to stop): ").lower().strip()
    while user_headline != "quit":
        if not utils.validate_headline(user_headline, entries):
            print("Valid headlines must be between {0} and {1} words, contain the phrase `Florida Man`, and not already exist in the training dataset. Suggested headline was not added to the entries.\n".format(utils.MIN_WORDS, utils.MAX_WORDS))
        else:
            print("User suggested headline `{0}` successfully added.\n".format(user_headline))
            user_headline = pd.DataFrame({
                "title" : [user_headline],
                "link" : ["~"]
            })
            user_headlines = user_headlines.append(user_headline, ignore_index=True, sort=True)
        user_headline = input("Please enter a valid headline (enter `quit` to stop). ").lower().strip()
    user_headlines.to_csv(training_directory + "user_headlines.csv", index=False)
    entries = utils.load_files(training_directory, used_files)
    headline_aggregate = ngrams_lm.generate_grams(n, entries)
    print("user_headlines.csv currently contains {0} entries.\n".format(len(user_headlines.index)))
    return (headline_aggregate, entries)

def clear_custom_headlines(headline_aggregate, entries):
    """Clears all headlines in user_headlines.csv

    Parameters
    ----------
    headline_aggregate: dictionary
        A dictionary of histories and corresponding frequencies for following words.
    entries: DataFrame
        A DataFrame containing all headline entries.
    """
    response = input("Are you sure you want to clear all entries in user_headlines.csv? [y/n] ").lower().strip()
    if response == "yes" or response == "y":
        cleared = pd.DataFrame(columns=["title", "link"])
        cleared.to_csv(training_directory + "user_headlines.csv", index=True)
        entries = utils.load_files(training_directory, used_files)
        headline_aggregate = ngrams_lm.generate_grams(n, entries)
        print("Cleared all headlines in user_headlines.csv.\n")
        return (headline_aggregate, entries)
    else:
        print("Did not clear headlines from user_headlines.csv.\n")

def inspect_data(headline_aggregate, entries):
    """Allows user to inspect each .csv file and drop/add .csv files as well.

    Will return updated headline_aggregate and entries if any .csv files are
    added or dropped. Additionally, this process mutates global variable
    filenames.

    Parameters
    ----------
    headline_aggregate: dictionary
        A dictionary of histories and corresponding frequencies for following words.
    entries: DataFrame
        A DataFrame containing all headline entries.
    """
    data_summary = lambda entries, filenames: print("Our training data currently includes {0} entries from the following files: {1}".format(len(entries.index), filenames))
    inspect_prompt = \
"""Enter one of the following options:
    Add:  Add file to training data
    Drop: Drop file from training data
    View: Inspect training data
    Quit: Exit to main selection
>>> """
    def add():
        try:
            filename = input("Enter the name of the .csv file to be incorporated into the training data (enter `quit` to stop): ").strip()
            if filename == "quit":
                print("No file added.")
                return
            if filename[-4:] != ".csv":
                filename += ".csv"
            if filename in used_files:
                print("`{0}` already in dataset. Unable to add `{0}` to dataset.".format(filename))
            if filename not in utils.get_files(training_directory, training_directory):
                print("`{0}` not found in training data directory `{1}`. Unable to add `{0}` to dataset.".format(filename, training_directory))
                return 
            df = pd.read_csv(training_directory + filename)
            if "title" not in df.columns or "link" not in df.columns:
                print("New .csv file must include columns `title` and `link`. Unable to add `{}` to dataset.".format(filename))
                return
            used_files.append(filename)
            used_files.sort()
            entries = utils.load_files(training_directory, used_files)
            headline_aggregate = ngrams_lm.generate_grams(n, entries)
            print("Successfully added `{}` to training dataset.".format(filename))
            data_summary(entries, used_files)
            return (headline_aggregate, entries)
        except Exception as e:
            utils.handle_exception(e, "Failed to add `{}` to training dataset.".format(filename))

    def delete():
        print("The training dataset currently consists of the following .csv files: {}".format(used_files))
        filename = input("Select a file to remove from the training dataset (enter `quit` to stop): ").strip()
        if filename == "quit":
            print("No file removed.\n")
            return
        if filename[-4:] != ".csv":
            filename += ".csv"
        if filename not in used_files:
            print("`{0}` is not found in the list of used files. Unable to drop `{0}`.".format(filename))
            return
        if len(used_files) == 1:
            print("Cannot remove all data from training dataset.")
            return 
        used_files.remove(filename)
        entries = utils.load_files(training_directory, used_files)
        headline_aggregate = ngrams_lm.generate_grams(n, entries)
        print("Successfully removed `{}` from training data.".format(filename))
        data_summary(entries, used_files)
        return (headline_aggregate, entries)

    def view_data():
        print("The training dataset currently consists of the following .csv files: {}".format(used_files))
        filename = input("Select a file to view (enter `quit` to stop): ").strip()
        if filename == "quit":
            return
        if filename[-4:] != ".csv":
            filename += ".csv"
        if filename not in used_files:
            print("`{0}` not in dataset. Unable to view `{0}`.".format(filename))
            return
        df = pd.read_csv(training_directory + filename)
        if len(df.index) == 0:
            print("No entries.")
            return 
        for i, row in df.iterrows():
            print(
"""
{0}
    {1}
    {2}
""".format(i + 1, row["title"], row["link"])
            )
        return 

    options = {
        "quit": None,
        "add": add,
        "drop": delete,
        "view": view_data
    }
    data_summary(entries, used_files)
    fn = utils.option_mux(inspect_prompt, options)
    modified_dataset = False
    while fn is not None:
        out = fn()
        print()
        if out is not None:
            headline_aggregate, entries = out
            modified_dataset = True
        data_summary(entries, used_files)
        fn = utils.option_mux(inspect_prompt, options)
    print()
    if modified_dataset:
        return (headline_aggregate, entries)

def guessing_quiz(headline_aggregate, entries):
    """A quiz game where users guess if a headline was generated or genuine.

    Parameters
    ----------
    headline_aggregate: dictionary
        A dictionary of histories and corresponding frequencies for following words.
    entries: DataFrame
        A DataFrame containing all headline entries.
    """
    # Proportion of generated headlines
    generated_proportion = 0.5

    real_headlines = entries.loc[entries["link"] != "~"]
    num_correct = 0
    num_questions = 0
    presented_indices = set()
    print("Welcome to the guessing game! The objective of this game is to guess if a headline is generated or genuine. Enter `real` if you think the headline belongs to a real news article, and `fake` if you believe it was generated. Enter `quit` to stop the game.\nNote: We will not consider user-added headlines as real headlines.\n")
    user_input = ""
    while user_input != "quit":
        num_questions += 1
        headline = None
        selected_ind = -1 if np.random.uniform() < 0.5 else np.random.randint(0, len(real_headlines))
        while headline is None or headline in presented_indices:
            if selected_ind == -1:
                headline = ngrams_lm.generate_headline(n, headline_aggregate)
            else:
                headline = real_headlines.iloc[selected_ind]["title"]
                presented_indices.add(selected_ind)
        print("Q{0}: {1}".format(num_questions, headline))
        while True:
            user_input = input("Is this article real or fake? ").lower().strip()
            if user_input not in ("real", "fake", "quit"):
                print("Please enter a valid response. Valid responses include {`real`, `fake`, `quit`}.")
            else:
                if user_input == "quit":
                    num_questions -= 1
                    if num_questions == 0:
                        print("\nNo questions answered.\n")
                    else:
                        print("\n`{0}` was a {1} article! Of the {2} questions you've answered, you classified {3}% or {4} of the headlines correctly.\n".format(headline, "fake" if selected_ind == -1 else "real", num_questions, round(100 * num_correct / num_questions, 2), num_correct))
                    return
                elif (user_input == "real" and selected_ind != -1) or (user_input == "fake" and selected_ind == -1):
                    prompt = "Correct!"
                    num_correct += 1
                else:
                    prompt = "Incorrect."
                if selected_ind == -1:
                    print("{} This headline was generated by the language model!\n".format(prompt))
                    break
                else:
                    print("{0} This was a real `Florida Man` headline! Here's the actual news article: {1}\n".format(prompt, real_headlines.iloc[selected_ind]["link"]))
                    break

if __name__ == "__main__":
    init_shell()
    entries = utils.load_files(training_directory, used_files)
    headline_aggregate = ngrams_lm.generate_grams(n, entries)
    greeting(entries)
    get_seed()
    options = {
        "add": add_headline,
        "clear": clear_custom_headlines,
        "files": inspect_data,
        "setn": set_n,
        "generate": print_headlines,
        "quiz": guessing_quiz,
        "quit": None,
        "exit": None,
        "exit()": None,
    }
    while True:
        commands_prompt = \
"""Enter one of the following commands:
    Add:      Add custom headline to training dataset
    Clear:    Clear all custom headlines 
    Files:    Add/remove files from training data, view dataset files
    SetN:     Change the value of n (n is currently {})  
    Generate: Generate a batch of headlines
    Quiz:     Play guessing quiz
    Quit:     Exit
>>> """.format(n)
        fn = utils.option_mux(commands_prompt, options)
        if fn is None:
            exit()
        out = fn(headline_aggregate, entries)
        if out is not None:
            headline_aggregate, entries = out
