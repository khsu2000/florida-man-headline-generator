# florida-man-headline-generator
Welcome to my first personal project! I initially took on this project during the summer after my freshman year at UC Berkeley, but refactored and rewrote nearly all of the code just before the start of my junior year. 

This is a "Florida Man" headline generator. Using headlines scraped from various news sources as training data, an n-grams language model is able to generate fake headlines that sound like they could belong to real articles. To see this in action, I encourage you to clone this repository and run shell.py! From there, you're able to start a terminal program that allows you to add custom headlines to the training data, generate headlines in bulk, or play a guessing game to determine if a presented headline is generated or genuine. To check the required packages needed to run any of the files, check out requirements.txt.

## Project Breakdown
There are three main components to this project: 
1. [Web Scrapers](./scraper.py)
2. [N-gram Language Model](./ngrams_lm.py)
3. [Interactive Shell](./shell.py) 

### Web Scrapers
I gathered the "Florida Man" headlines from three different news sources: [Local 10 News](https://www.local10.com/), [CBS Miami](https://miami.cbslocal.com/), and a [dedicated Florida Man site](https://floridaman.com/). All scrapers were built with Selenium and BeautifulSoup; Selenium allowed the scrapers to load and interact (for example, like pressing the "Next Page" buttons) with the sites while BeautifulSoup helped parse the page's actual contents. To run Selenium, a [Chrome webdriver](https://sites.google.com/a/chromium.org/chromedriver/home) was also required. I last scraped for headlines on 8/8/2020, and the ChromeDriver version I used was 84.0.4147.30.

While all scrapers used Selenium and BeautifulSoup, each site required a unique scraper, as the sites were all built with different HTML templates. Deciding how to tackle each site to scrape their headlines required me to study each site's source and find selectors I could use to parse the information. 

When going back to rewrite the scraper code, I realized that I had initially taken unnecessarily roundabout or even unreliable approaches to finding some webpage elements. One example of this was in my original implementation of the Local 10 news scraper; to locate the "Next Page" button, I had originally used the button's XPath. However, the button's XPath is not guaranteed to remain the same between executions, so this resulted in inconsistent behavior. Instead, my current implementation uses the button's class name, which is always fixed.

### N-Gram Language Model
The N-gram language model is a predictive language model that is used for applications like producing Shakespeare-like text. The model works by splitting a text corpus into grams of fixed-length (in words) and using the grams to form a conditional probability distribution that maps a text history to possible outcomes. As an example, if the text history were "Florida man..." the language model may predict that the next word is "arrested" with 30% probability, "assaults" with 25% probability, "reported" with 10% probability, etc. The model then randomly chooses a word based on that distribution, and then updates the text history; in the case that "arrested" were chosen, the new text history would be "man arrested...", and then another word would be chosen. The value of N in the name N-gram language model is the length of each gram, or phrase. The above example is a bigram, where the text history and phrases are two words long. 

My implementation of the N-gram language model takes advantage of Python's built-in defaultdict and Counter to create a density function using the scraped headlines as a text corpus. The language model code is relatively well encapsulated after refactoring, so that the interactive shell's code in shell.py only needs to call `generate_grams` to produce the distribution from the training data, and passing the distribution into `generate_headline` returns a new headline as a string. 

### Interactive Shell
The interactive shell was allows a user to interact with the language model. The full list of commands are as follows:
* Add custom headlines to training dataset/text corpus
* Clear all custom headlines (remove all user added headlines)
* Add/remove files from training data, view each .csv file individually
* Change the value of n and retrain the model 
* Generate a batch of headlines, option to save them to a .txt file
* Play guessing quiz to determine if headlines are real or generated headlines

While I added no new functionality when I refactored the code, I sped up the runtime of multiple functions, improved the consistency of the text prompts to users, and made the code more concise. 

## Authors
Kevin Hsu 
