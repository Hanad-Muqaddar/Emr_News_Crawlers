# Packages to be imported
from functools import total_ordering
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

from urllib.parse import urlparse

import re

import traceback

import urllib

import dateparser

# from datetime import datetime
import datetime

from bson.objectid import ObjectId

from urllib.error import HTTPError

from urllib.request import Request, urlopen

from scrapy import Selector

# ************************************************************************
# defining variables
# opts = Options()
# opts.add_argument("--window-size=190,100")
# opts.add_argument("--disable-automation")
# opts.add_argument("--no-sandbox")
# opts.add_argument('--profile-directory=Default')
# opts.add_argument("start-maximized")
# opts.add_argument("disable-infobars")
# opts.add_argument("--lang=en")
# opts.add_argument("--enable-javascript")
# opts.add_argument("--enable-cookies")
# lang_dict = {'nl': 'en', 'fr': 'en', 'cs': 'en', 'da': 'en', 'de': 'en', 'es': 'en', 'it': 'en', 'hu': 'en', 'no': 'en', 'pl': 'en', 'pt': 'en', 'ro': 'en', 'sk': 'en', 'fi': 'en', 'sv': 'en', 'tr': 'en', 'el': 'en', 'bg': 'en', 'ru': 'en', 'uk': 'en', 'ar': 'en', 'id': 'en', 'vi': 'en', 'th': 'en', 'zh': 'en', 'ja': 'en', 'ko': 'en'}
# prefs = {
#   "translate_whitelists": lang_dict,
#   "translate":{"enabled":"true"}
# }
# opts.add_experimental_option("prefs", prefs)
# opts.headless = True

running_Sequence = []

started_on = datetime.datetime.now()

c_name = 'MERSEN' # Name of the Collection

total_crwalled_links = 0

Already_exist = 0

# *************************************************************************

# trying to connect with mongodb

try:
    file = open("/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/config.json")
    data = json.load(file)
    db_path = data[0]['Db_Path']
    client = MongoClient(db_path)
    # client = MongoClient('mongodb://su-du-ad:updatedSuperDuperAdmin@18.156.208.71:27017/emrweb?authSource=admin') # Staging DB 

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

    running_Sequence.append('Fresh Starting News Crawler on -> ' + str(datetime.datetime.now()))

    Crwl_time = datetime.datetime.now()

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
    for i in range(0,12):
        main_page_link = 'https://www.mersen.com/news-media/events-news?page={}'.format(i)
        result = requests.get(main_page_link)
        data = Selector(result)
        news = data.css(".home-news__item")
        for j in news:
            try:
                date = j.css(".date ::text").get()
                date = dateparser.parse(date)
            except:
                date = ""
            try:
                title = j.css(".field--name-title ::text").get()
            except:
                title = ""
            try:
                image = "https://www.mersen.com/" + j.css(".inner img::attr(data-src)").get()
            except:
                image = ""
            try:
                news_weblink = "https://www.mersen.com/" + j.css(".go-link ::attr(href)").get()
            except:
                news_weblink = ""
                
            db_list = []
            mydoc = collection.find()
            for x in mydoc:
                db_list.append(x['News_Weblink'])
            if news_weblink in db_list:
                total_crwalled_links += 1
                Already_exist += 1
                continue
            
            try:
                result2 = requests.get(news_weblink)
                data2 = Selector(result2)
            except:
                data2 = ""
            try:
                annou = data2.css(".description p::text").getall()
                announcement = ""
                for j in annou:
                    announcement = announcement + j
            except:
                announcement = ""
            try:
                analysis = data2.xpath("//meta[@property='og:description']/@content").get()
            except:
                analysis = ""
            
            company_news = {}
            company_news['companyId'] = ''
            company_news['location']=''
            company_news['comment']=''
            company_news['Date']= date
            company_news['Crawled_on']= datetime.datetime.now()
            company_news['title']=title
            company_news['Language']= 'English'
            company_news['announcementType']= 'News'
            company_news['Source'] = "https://www.mersen.com/news-media/events-news"
            company_news['News_Weblink'] = news_weblink
            company_news['photo']= image
            company_news['videos']= ''
            company_news['announcement']=announcement
            company_news['historySubCategory']= ""
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

    ended_on = datetime.datetime.now()
except Exception as e:
    Error_Time =  datetime.datetime.now()

    Reported_Error = traceback.format_exc()

    running_Sequence.append(e)


# **************************************************************************

# **************************************************************************

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

log['Browser'] = 'Chrome'

error_logs.insert_one(log)

