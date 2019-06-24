'''
Scrapes various news sources for links related to Florida man.
Stores results in headlines.csv
'''

import csv
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Specify news sources here
source = "https://www.local10.com/search?searchTerm=florida+man"

# Specify filename here where data is being stored
filename = "headlines.csv"

# Creates the chrome driver
driver = webdriver.Chrome("./chromedriver_win32/chromedriver.exe")
delay = 3

def scrape(source, filename):
    """Reads headlines and links of articles to a text file.

    Takes a search query string for Florida man articles and finds the headlines
    and corresponding article links into a text file.

    Parameters
    ----------
    source: string
        The source URL of a news source query for "Florida man".
    filename: string
        The name of the file the articles are being written into.
    """
    driver.get(source)
    load_limit = 10

    entries = [["title", "link", "date"]]

    for _ in range(load_limit):
        try:
            soup = BeautifulSoup(driver.page_source, "html5lib")
            headlines = soup.find_all("div", {"class" : "queryly_item"})
            for headline in headlines:
                article_title = headline.find_all("div", {"class" : "queryly_item_title"})[0].decode_contents()
                article_link = headline.a["href"]
                article_date = headline.find_all("div", {"class" : "queryly_item_date"})[0].decode_contents()
                print(article_title)
                entries.append([article_title, article_link, article_date])
            driver.find_element_by_class_name("queryly_paging").click()
            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, "queryly_item_title")))
        except Exception as e:
            print("Incurred the following error:\n" + str(e))
            print("Saving currently scraped results in 'headlines.csv'.")
            break

    write_to_csv(entries, filename)

def write_to_csv(content, filename):
    """Writes list to file specified by filename.

    If the file already exists, it will append to the end of the file. Otherwise
    creates a new file. Writes a newline for every string.

    Parameters
    ----------
    content: list
        A list of lists to be written into the csv file.
    filename:
        The name of the file the string is being written into.
    """
    df = pd.DataFrame(content[1:], columns=content[0])
    df.to_csv(filename, index=False)

if __name__ == "__main__":
    scrape(source, filename)
