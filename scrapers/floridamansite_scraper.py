'''
Scrapes floridaman.com for links related to Florida man.
Stores results in training_data/floridaman_com_headlines.csv.
'''

import pandas as pd
import traceback
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Specify news sources here
source = "https://floridaman.com/"

# Specify filename here where data is being stored
filename = "training_data/floridaman_com_headlines.csv"

# Specify how many times to click 'next page' to load more results
load_limit = 14

# Creates the chrome driver
chrome_options = Options()

# Set this line to true to hide browser
chrome_options.headless = True

driver = webdriver.Chrome("./chromedriver_win32/chromedriver.exe", options=chrome_options)
delay = 3

def scrape(source, filename):
    """Writes headlines and links of articles to a .csv file.

    Parameters
    ----------
    source: string
        The source URL of a news source query for "Florida man".
    filename: string
        The name of the file the articles are being written into.
    """
    driver.get(source)

    entries = pd.DataFrame(columns=["title", "link"])

    for page in range(2, load_limit + 2):
        try:
            soup = BeautifulSoup(driver.page_source, "html5lib")
            headlines = soup.find_all("h3", {"class" : "entry-title"})
            for headline in headlines:
                article_title = headline.a.decode_contents()
                article_link = headline.a["href"]
                if is_florida_man_article(article_link):
                    entry = pd.DataFrame({"title" : [article_title],
                                          "link" : [article_link]})
                    entries = entries.append(entry, ignore_index=True)
            driver.get(source + "page/{}/".format(page))
        except Exception:
            print("\nIncurred the following error:\n")
            print(traceback.format_exc())
            break

    write_to_csv(entries, filename)

def write_to_csv(content, filename):
    """Writes list to .csv file specified by filename.

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

def is_florida_man_article(link):
    """Returns boolean to check if link is a floridaman.com article

    Parameters
    ----------
    article: str
        A string of the href an <a> element contains
    """
    return "https://floridaman.com/" in link

if __name__ == "__main__":
    scrape(source, filename)
