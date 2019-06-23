'''
Scrapes various news sources for links related to Florida man.
Stores results in headlines.csv
'''

import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Specify news sources here
source = "https://www.local10.com/search?searchTerm=florida+man"

# Specify filename here where data is being stored
filename = "headlines.csv"

driver = webdriver.Chrome("C:/Users/kevin/Downloads/chromedriver_win32/chromedriver.exe")
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
    entry_limit = 100

    write_to_file("title,url", filename)

    for _ in range(entry_limit):
        soup = BeautifulSoup(driver.page_source, "html5lib")
        headlines = soup.find_all("div", {"class" : "queryly_item"})
        for headline in headlines:
            article_title = headline.find_all("div", {"class" : "queryly_item_title"})[0].decode_contents()
            article_link = headline.a["href"]
            print(article_title)
            write_to_file(article_title + "," + article_link, filename)
        driver.find_element_by_class_name("queryly_paging").click()
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, "queryly_item_title")))

def write_to_file(str, filename):
    """Writes string to file specified by filename.

    If the file already exists, it will append to the end of the file. Otherwise
    creates a new file. Writes a newline for every string.

    Parameters
    ----------
    str: string
        The string to be written into the file.
    filename:
        The name of the file the string is being written into.
    """
    f = open(filename, "a+")
    f.write("\n" + str)
    f.close()

if __name__ == "__main__":
    scrape(source, filename)
