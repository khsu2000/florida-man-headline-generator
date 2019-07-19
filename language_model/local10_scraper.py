'''
Scrapes various news sources for links related to Florida man.
Stores results in headlines.csv.
'''

import csv
import pandas as pd
import traceback
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

# Specify news sources here
source = "https://www.local10.com/search?searchTerm=florida+man"

# Specify filename here where data is being stored
filename = "training_data/local10_headlines2.csv"

# Specify how many times to click 'next page' to load more results
load_limit = 200

# Creates the chrome driver
chrome_options = Options()

# Uncomment this line to change driver to headless; may lead to error with clicking images on accident
# chrome_options.headless = True

driver = webdriver.Chrome("./chromedriver_win32/chromedriver.exe", options=chrome_options)
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

    entries = pd.DataFrame(columns=["title", "link", "date"])

    for _ in range(load_limit):
        try:
            soup = BeautifulSoup(driver.page_source, "html5lib")
            headlines = soup.find_all("div", {"class" : "queryly_item"})
            for headline in headlines:
                article_title = headline.find_all("div", {"class" : "queryly_item_title"})[0].decode_contents()
                article_link = headline.a["href"]
                article_date = headline.find_all("div", {"class" : "queryly_item_date"})[0].decode_contents()
                if is_florida_man_article(article_title):
                    print(article_title)
                    entry = pd.DataFrame({"title" : [article_title],
                                          "link" : [article_link],
                                          "date" : [article_date]})
                    entries = entries.append(entry, ignore_index = True)

            # Delay for element to be clickable
            WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="resultdata"]/a[1]/h3')))
            buttons = driver.find_elements_by_xpath('//*[@id="resultdata"]/a[1]/h3')
            for btn in buttons:
                if btn.get_attribute("innerHTML").strip().lower() == "next page":
                    next_page = btn
                    break
            actions = ActionChains(driver)
            actions.move_to_element(next_page).click().perform()
            undoMisclick()

            # Delay for next set of articles to load
            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, "queryly_item_title")))
        except Exception:
            print("\nIncurred the following error:\n")
            print(traceback.format_exc())
            write_to_csv(entries, filename)
            return

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
    content = content.drop_duplicates()
    content.to_csv(filename, index=False)

    print("Scraped {} sources.".format(len(content.index)))
    print("Saving currently scraped results in '{}'.".format(filename))

def is_florida_man_article(article):
    """Returns boolean to check if 'florida man' in article headline.

    Parameters
    ----------
    article: str
        A string name of the article's title
    """
    return "florida man" in article.lower()

def undoMisclick():
    """Checks if URL is local10 news; if URL is not local10 news, stops scraper.

    Parameters
    ----------
    None
    """
    global load_limit

    if driver.current_url != source:
        print("\nAccidentally navigated to a wrong location; stopping scraper.")
        print("Navigated to: {}".format(driver.current_url))
        raise Exception("Navigated to invalid URL.")

if __name__ == "__main__":
    scrape(source, filename)
