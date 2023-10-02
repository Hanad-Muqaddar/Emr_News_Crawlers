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

from datetime import datetime

from bson.objectid import ObjectId

from urllib.error import HTTPError

from urllib.request import Request, urlopen
from Emr_Crawlers_Optimization import Emr_Crawlers_Logs
# ************************************************************************
# defining variables

running_Sequence = []

started_on = datetime.now()

c_name = 'RDM' # Name of the Collection

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
    links_list = []
    result = requests.get("https://www.rdm.com/news")
    # result = requests.get("https://www.rdm.com/news/page/1/?rdm_news_cat%5B0%5D=353")
    soup = BeautifulSoup(result.content, 'lxml')
    data = soup.find_all("div", class_='long-card col-12')
    for i in data:
        news_weblink = i.find("a").get("href")
        links_list.append(news_weblink)

    print(links_list)
        
    db_list = []
    mydoc = collection.find()
    for x in mydoc:
        db_list.append(x['News_Weblink'])
        
    for j in links_list:
        Emr_Crawlers_Logs(c_name,j)
        if j in db_list:
            total_crwalled_links += 1
            Already_exist += 1
            print("Already exists.")
            continue
        else:
            news_weblink = j
            res = requests.get(news_weblink)
            soup = BeautifulSoup(res.content, 'lxml')
            try:
                sub_category = soup.find("meta", attrs={"property":"og:type"}).get("content")
            except:
                sub_category = ""
            try:
                title = soup.find("meta", attrs={"property":"og:title"}).get("content")
                print(title)
            except:
                title = ""
            try:
                image = soup.find("meta", attrs={"property":"og:image"}).get("content")
            except:
                image = ""
            try:
                news_date = soup.find("div", class_='col-md-12 meta-data-mobile').text.strip().split("\n")[0].strip()
                news_date = dateparser.parse(news_date)
            except:
                news_date = ""
            try:
                announcement_type = soup.find("div", class_='col-md-12 meta-data-mobile').text.strip().split("\n")[1].strip().split("-")[0].strip()
            except:
                announcement_type = ""
            try:
                announcement = soup.find_all("section")[1].text
            except:
                announcement = ""
            language = "en-US"
            page_source = "https://www.rdm.com/news"
            try:
                analysis = soup.find("meta", attrs={"property":"og:description"}).get("content")
            except:
                analysis = soup.find("meta", attrs={"property":"og:title"}).get("content")
            date = datetime.now()
            
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

log['Ending_time'] = Error_Time if rep == '' else datetime.now()

log['Error_Detail'] =  Error if rep == '' else ''

log['Crawler_Runing Sequence'] = running_Sequence if running_Sequence else ''

log['Links_Skipped'] = Already_exist

log['Last_news_crawl_time'] = last_time

log['Browser'] = 'None'

error_logs.insert_one(log)

