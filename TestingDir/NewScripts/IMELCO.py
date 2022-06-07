# Packages to be imported
import requests

import time

import json

from random import randint

from bs4 import BeautifulSoup

from pymongo import MongoClient

from bs4 import BeautifulSoup

from selenium import webdriver

# from webdriver_manager.chrome import ChromeDriver

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support import expected_conditions

from selenium.webdriver.common.by import By

# from selenium.webdriver.common.touch_actions import TouchActions

from urllib.parse import urlparse

import re

import traceback

import urllib

import dateparser

from datetime import datetime

from bson.objectid import ObjectId

from urllib.error import HTTPError

from urllib.request import Request, urlopen
from newspaper import fulltext

# ************************************************************************
# defining variables

running_Sequence = []

started_on = datetime.now()

c_name = 'IMELCO' # Name of the Collection

total_crwalled_links = 0

Already_exist = 0

# *************************************************************************

# trying to connect with mongodb

try:

    client = MongoClient('mongodb://su-du-ad:updatedSuperDuperAdmin@18.156.208.71:27017/emrweb?authSource=admin') # Staging DB 

    running_Sequence.append('Connected to DB Server')

except:

    running_Sequence.append('Not Connected')

# *************************************************************************

client_name = 'TEMP_EMR_NEWS_Crawler_DB'

news =  client[client_name]

collection = news[c_name]

error_logs = client['Logs_DB']['Logs_TEMP_EMR_NEWS_Crawler_DB']

last_insertion = None

last_time = ''

# ****************************************************************************

try:

    for l_i in collection.find().sort('Date', -1).limit(1):

        last_insertion = l_i

except:

    last_insertion = None

if last_insertion == None:

    running_Sequence.append('Fresh Starting News Crawler on -> ' + str(datetime.now()))

    Crwl_time = datetime.now()

else:

    last_time = last_insertion['Date']

    running_Sequence.append('Last News Crawled on -> '+str(last_insertion['Date'].date()))

    Crwl_time = last_insertion['Date']

# ****************************************************************************

####################################################

############# Every Company Logic Here #############

####################################################

# *****************************************************************************
try:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
    Main_url = "https://imelco.com" 
    Base_url = "https://imelco.com/publications/press-releases" 
    result = requests.get(Base_url, verify=False)
    soup = BeautifulSoup(result.content , 'lxml')
    
    news_Titles = []
    news_dates = [] 
    pdfs = []

    N_Titles = soup.find_all('h3',attrs = {"style":"display:inline-block; margin:0.25em 0;"})
    for title in N_Titles:
        news_Titles.append(title.get_text(strip=True))
        
    N_Dates = soup.find_all('div',attrs = {"style":"display:inline-block; font-style: italic; font-size: 0.75em; margin-right:0.25em; "})
    for N_Date in N_Dates:
        news_dates.append(N_Date.get_text(strip=True))

    pdf = soup.find('div',attrs = { "id" : "wpv-view-layout-1088"}).find_all('a',attrs = { "target" : "_blank"})
    for p in pdf:
        p= p.get('href')
        pdfs.append(p)

    pdf_set = set(pdfs)    



    # print(news_Titles)
    # print(news_dates)
    # print(len(news_Titles))
    # print(len(news_dates))

    for i , N_Date, p in zip(news_Titles,news_dates,pdf_set):     
       
        title = i 
        # print(title)      
        announcement_type = "News"
        language = "en-us"        
        image = ""        
        sub_category = ""        
        analysis = ""
        try:
            # print(N_Date)
            news_date = dateparser.parse(N_Date,  settings={'DATE_ORDER': 'YMD'} )
            # print(news_date)
        except:
            news_date = ""

        page_source = "https://imelco.com/publications/press-releases" 
        news_weblink = p      
        announcement = ""
        
        date = datetime.now()
        # Creating a list of links already avilable in database
        links_list = []
        mydoc = collection.find()
        for x in mydoc:
            links_list.append(x['News_Weblink'])

        if news_weblink in links_list:
            total_crwalled_links += 1
            Already_exist += 1
            continue
        else:
            company_news = {}
            company_news['companyId'] = ''
            company_news['location']=''
            company_news['comment']=''
            company_news['Date']= news_date
            company_news['Crawled_on']=date
            company_news['title']=title
            company_news['Language']= language
            company_news['announcementType']= announcement_type
            company_news['Source'] = page_source
            company_news['News_Weblink'] = news_weblink
            company_news['photo']= image
            company_news['videos']= ''
            company_news['announcement']=announcement
            company_news['historySubCategory']= sub_category
            company_news['analysis'] = analysis
            try:
                collection.insert_one(company_news)
                total_crwalled_links += 1
            except Exception as e:
                running_Sequence.append(e)
    
    if Already_exist >= 1:

        tmp_txt = ' , from which '+str(Already_exist) +' Links were Already Crawled '

    else:

        tmp_txt = ''

    running_Sequence.append(str(total_crwalled_links) + ' Links are crawled ' + tmp_txt)

    ended_on = datetime.now()
except:
    Error_Time =  datetime.now()

    Reported_Error = traceback.format_exc()


# **************************************************************************
rep = ''

try:

    Error = {}

    Error['Error_Detail'] = Reported_Error

    Error['Error_Time'] = Error_Time

except Exception as e:

    rep = traceback.format_exc()

    pass


log = {}

log['Crawler_name'] = c_name+'.py'

log['Crawler_type'] = c_name

log['Starting_time'] = started_on

log['Ending_time'] = Error_Time if rep == '' else ended_on

log['Error_Detail'] =  Error if rep == '' else ''

log['Crawler_Runing Sequence'] = running_Sequence if running_Sequence else ''

log['Links_Skipped'] = Already_exist

log['Last_news_crawl_time'] = last_time

log['Browser'] = 'None'

error_logs.insert_one(log)
