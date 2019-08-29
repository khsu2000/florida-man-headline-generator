# florida-man-headline-generator
This is my first personal project! I took this on during the summer after my freshman year at Berkeley.  

This is a "Florida Man" headline generator. It uses headlines scraped from various news sources as training data for a n-grams language model. By running n_grams_lm.py, a user opens up an interactive mode with options like adding custom training headlines, generating headlines in bulk, or playing a guessing quiz. 

## Overview 
There are two main components to this project: 
* scrapers (python files in /scrapers)
* the interactive program (n_grams_lm.py)

Each source has its own scraper. The scrapers use Selenium python and BeautifulSoup to extract Florida Man articles from three sources: Local 10 news, CBS Miami, and a dedicated Florida Man website. They use pandas dataframes to keep track of news headlines and corresponding article links before saving the data to .csv files. 

The interactive program itself can be broken down into headline generation and user interaction. The program first starts by initially training the language model with the data from the included scrapers and a default value of n=2 (it can also take in a random seed from the user before this). It then internally tracks the language model (stored as a dictionary) and the training data used (stored as a pandas dataframe). After the initial training, the program enters a loop where it takes commands from the user. 

The full list of commands are as follows: 
* Change the value of n and retrain the model 
* Generate a batch of headlines (with the option to save to .txt file) 
* Add a custom headline to the training data and retrain the model 
* Clear all custom user headlines 
* Inspect what .csv files are included in the training data (this option includes the abilities to add other .csv files or remove .csv files from the training data) 
* Play a guessing game where the user has to guess if a headline is generated or genuine. 


## Prerequisites 
To just run n_grams_lm.py, you need numpy and pandas. However, it does need access to the training data, which is contained inside scrapers/training_data/. Make sure that scrapers/training_data/ stays in the same directory as n_grams_lm.py. 

To run any of the scrapers in scrapers/, you need pandas, BeautifulSoup, and Selenium. Additionally, you need to download a selenium chromedriver. You don't need numpy to run the scrapers. 

## Adding/Dropping Data 
All training data is stored in scrapers/training_data/. Make sure that all .csv files you want the language model to use has at least the following two columns: "title" and "link". If you want to add training data, make sure you place your new .csv file in scrapers/training_data/. When dropping data, make sure that n_grams_lm.py initially has some training data to use. If there is no training data, n_grams_lm.py will error. Finally, make sure you leave user_headlines.csv in training_data/. This is used for adding custom headlines. If you don't want to use user-added headlines in the language model, you should use the interactive mode's drop data or clear custom headlines options. If you want to add or drop data, there are two ways to do so: 
* You can add/drop data from the option listed in n_grams_lm.py's interactive mode. This will only apply changes for your current execution of n_grams_lm.py. 
* To make permanent changes that persist between executions of n_grams_lm.py, you can edit the "filenames" variable in n_grams_lm.py. This is a list of file names that n_grams_lm.py automatically uses each time to create its language model. Just add or remove the file names that you want n_grams_lm.py to use every time it's executed. 

Obviously, make sure that all .csv files you're working with are actually present in scrapers/training_data/. 

## Authors
Kevin Hsu 
