"""
Scrapes various news sites for articles related to Florida man. 
Stores headlines in csv files in ./training_data 
"""
from bs4 import BeautifulSoup
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time 
import traceback
import utils

data_directory = "training_data/"
driver = webdriver.Chrome("chromedriver_win32/chromedriver.exe")

def scrape_floridaman_site(filename):
    """Scrapes https://floridaman.com/ for Florida man headlines. Saves headlines to filename.

    Parameters
    ----------
    filename: string
        The name of the file the articles are being written into.
    """
    driver.get("https://floridaman.com/")
    verify_article = lambda link: "https://floridaman.com" in link
    num_pages = 17

    entries = pd.DataFrame(columns=["title", "link"])
    for page in range(1, num_pages + 1):
        try:
            soup = BeautifulSoup(driver.page_source, "html5lib")
            headlines = soup.find_all("h3", {"class" : "entry-title"})
            for headline in headlines:
                article_title = headline.a.decode_contents().strip()
                article_link = headline.a["href"]
                if verify_article(article_link):
                    entry = pd.DataFrame({"title" : [article_title],
                                          "link" : [article_link]})
                    entries = entries.append(entry, ignore_index=True)
            driver.get("https://floridaman.com/page/{}/".format(page))
        except:
            utils.handle_exception(None)
            break
    driver.quit()
    utils.write_to_csv(entries, filename)

def scrape_cbs_miami(filename):
    """Scrapes CBS Miami for Florida man headlines. Saves headlines to filename.

    Parameters
    ----------
    filename: string
        The name of the file the articles are being written into.
    """
    driver.get("https://miami.cbslocal.com/search/?q=florida+man")
    entries = pd.DataFrame(columns=["title", "link"])

    # Wait until next page links are loaded
    _ = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "gsc-cursor-page")))
    soup = BeautifulSoup(driver.page_source, "html5lib")
    num_pages = int(soup.find_all("div", {"class" : "gsc-cursor-page"})[-1].text)
    try:
        for page_count in range(1, num_pages):
            soup = BeautifulSoup(driver.page_source, "html5lib")
            headlines = soup.find_all("a", {"class" : "gs-title", "dir" : "ltr"})
            for headline in headlines:
                headline_link = headline["href"]
                link_soup = BeautifulSoup(requests.get(headline_link, allow_redirects=False).text, "html5lib")
                headline_title = link_soup.find("h1", {"class" : "title"}).text
                entry = pd.DataFrame({
                    "title" : [headline_title],
                    "link" : [headline_link]
                })
                entries = entries.append(entry, ignore_index=False)
            driver.find_elements_by_class_name("gsc-cursor-page")[page_count].click()
    except:
        utils.handle_exception(None)
    driver.quit()
    utils.write_to_csv(entries, filename)

def scrape_local10(filename):
    """Scrapes local10 news for Florida man headlines. Saves headlines to filename.

    Parameters
    ----------
    filename: string
        The name of the file the articles are being written into.
    """
    driver.get("https://www.local10.com/search/?searchTerm=florida+man")
    entries = pd.DataFrame(columns=["title", "link"])
    verify_article = lambda title: "florida man" in title.lower()
    number_entries = 500
    click_attempts = 100
    
    try:
        while len(entries.index) < number_entries:
            next_page = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "queryly_paging")))
            soup = BeautifulSoup(driver.page_source, "html5lib")
            headlines = soup.find_all("div", {"class" : "queryly_item"})
            for headline in headlines: 
                article_title = headline.find("div", {"class" : "queryly_item_title"}).decode_contents()
                article_link = headline.a["href"]
                if verify_article(article_title):
                    entry = pd.DataFrame({
                        "title" : [article_title], 
                        "link" : [article_link]
                    })
                    entries = entries.append(entry, ignore_index = True)  
            if next_page.text == "Next Page":
                next_page.click()
            else:
                break
    except:
        utils.handle_exception(None)
    driver.quit()
    utils.write_to_csv(entries, filename)

if __name__ == "__main__":
    scrape_floridaman_site(data_directory + "floridaman_site_headlines.csv")
    scrape_cbs_miami(data_directory + "cbs_miami_headlines.csv")
    scrape_local10(data_directory + "local10_headlines.csv")
