'''
Scrapes various news sources for links related to Florida man.
Stores links in news_articles.txt
'''

import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver

sources = ["https://www.local10.com/search?searchTerm=florida+man"]

driver = webdriver.Chrome()

'''
driver.get(sources[0])

html = driver.page_source
soup = BeautifulSoup(html)

print(soup.prettify())
'''
