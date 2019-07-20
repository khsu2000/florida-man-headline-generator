"""
Scrapes miami.cbslocal.com for links related to Florida man.
Stores results in cbsmiami_headlines.csv.
"""

import pandas as pd
import traceback
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Specify news sources here
source = "https://miami.cbslocal.com/search/?q=florida+man"

# Specify filename here where data is being stored
filename = "training_data/cbs_miami_headlines.csv"

# Creates the chrome driver
chrome_options = Options()

# Set to true to hide browser
chrome_options.headless = False
driver = webdriver.Chrome("./chromedriver_win32/chromedriver.exe", options=chrome_options)
delay = 3

def scrape(source, filename):
    """Writes headlines and links of articles to a text file.

    Parameters
    ----------
    source: string
        The source URL of a news source query for "Florida man".
    filename: string
        The name of the file the articles are being written into.
    """
    driver.get(source)
    entries = pd.DataFrame(columns=["title", "link"])
    soup = BeautifulSoup(driver.page_source, "html5lib")
    last_page = int(soup.find_all("div", {"class" : "gsc-cursor-page"})[-1].text)
    try:
        for page_count in range(2, last_page + 1):
            soup = BeautifulSoup(driver.page_source, "html5lib")
            headlines = soup.find_all("a", {"class" : "gs-title", "dir" : "ltr"})
            for headline in headlines:
                headline_link = headline["href"]
                link_soup = BeautifulSoup(requests.get(headline_link, allow_redirects=False).text, "html5lib")
                headline_title = link_soup.find("h1", {"class" : "title"}).text
                print(headline_title)
                entry = pd.DataFrame({
                    "title" : [headline_title],
                    "link" : [headline_link]
                })
                entries = entries.append(entry, ignore_index=False)
            driver.find_element_by_xpath('//*[@id="___gcse_0"]/div/div/div/div[5]/div[2]/div/div/div[2]/div[11]/div/div[{}]'.format(page_count)).click()
    except:
        print("\nIncurred the following error:\n")
        print(traceback.format_exc())
        write_to_csv(entries, filename)
        return

    write_to_csv(entries, filename)

def write_to_csv(content, filename):
    """Writes list to file specified by filename.

    If the file already exists, it will append to the end of the file. Otherwise
    creates a new file. Writes a newline for every string.

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

if __name__ == "__main__":
    scrape(source, filename)
