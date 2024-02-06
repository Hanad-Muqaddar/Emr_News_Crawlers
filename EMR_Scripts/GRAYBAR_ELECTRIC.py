# Packages to be imported
from os import link
import requests

import time

import json

from random import randint

from bs4 import BeautifulSoup

from pymongo import MongoClient, response

from bs4 import BeautifulSoup

from selenium import webdriver

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support import expected_conditions

from selenium.webdriver.common.by import By

import re

import traceback

import urllib

import dateparser

import datetime

from bson.objectid import ObjectId

from urllib.error import HTTPError

from urllib.request import Request, urlopen

from scrapy import Selector

from newspaper import fulltext
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
# from Emr_Crawlers_Optimization import Emr_Crawlers_Logs

# ================================================================================
# Comment these lines when you are running locally
import importlib.util
# Specify the absolute path to Emr_Crawlers_Optimization.py
module_path = '/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/Emr_Crawlers_Optimization.py'
# Load the module using the absolute path
spec = importlib.util.spec_from_file_location('Emr_Crawlers_Optimization', module_path)
Emr_Crawlers_Optimization = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Emr_Crawlers_Optimization)
Emr_Crawlers_Logs = Emr_Crawlers_Optimization.Emr_Crawlers_Logs
# ================================================================================
running_Sequence = []

started_on = datetime.datetime.now()

c_name = 'GRAYBAR_ELECTRIC' # Name of the Collection

total_crwalled_links = 0

Already_exist = 0

# *************************************************************************

# trying to connect with mongodb

try:
    # file = open("/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/config.json")
    # data = json.load(file)
    # db_path = data[0]['Db_Path']
    # client = MongoClient(db_path)
    
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
  
    opts = Options()
    # opts.add_argument("--window-size=190,100")
    # opts.add_argument("--disable-automation")
    opts.add_argument("--no-sandbox")
    opts.add_argument('--profile-directory=Default')
    opts.add_argument("start-maximized")
    opts.add_argument("disable-infobars")
    opts.add_argument("--lang=en")
    opts.add_argument("--enable-javascript")
    opts.add_argument("--enable-cookies")
    opts.headless = True

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opts)
     

    page_source = "https://www.graybar.com/news"
    driver.get(page_source)
    time.sleep(5)

    page_source = driver.page_source
        # print(page_source)
    response = Selector(text=page_source)

    Base_Link = "https://www.graybar.com"
    links = response.xpath('//td[@data-label="Title"]/a/@href').getall()
    f_links = ['/'+link if link[0] != '/' else link for link in links]
    final_links = [Base_Link+link for link in f_links]
    dates = response.xpath('//td[@data-label="Date"]/text()').getall()
    announcement_type = response.xpath('//td[@data-label="Category"]/text()').getall()
    titles = response.xpath('//td[@data-label="Title"]/a/text()').getall()

    db_list = []
    mydoc = collection.find()
    for x in mydoc:
        db_list.append(x['News_Weblink'])

    Emr_Crawlers_Logs(c_name,page_source,final_links)

    for i , j ,k , title in zip(final_links, dates, announcement_type, titles):
        if i in db_list:
            Already_exist += 1
            total_crwalled_links += 1
            print("Already Crawled")
            continue
        else:
            print("a gaya")
            result1 = requests.get(i)
            response1 = Selector(result1)
            try:
                news_date = dateparser.parse(j)
            except:
                news_date = ""
            try:
                title = title.strip()
                print(title)
            except:
                title = ""
                print("title,....")
            try:
                analysis = response1.xpath("//meta[@name='description']/@content").get()
            except:
                analysis = ""
            try:
                image = response1.css(".col-sm-9 img::attr(src)").get()
            except:
                image = ""

            sub_category = ""

            try:
                announcement = fulltext(result1.text)
                announcement = announcement.replace('\n','<br>')
            except:
                announcement = ""

            try:
                announcement_type = k.strip()
            except:
                announcement_type = ""

            language = "en-US"
            
            crawled_date = datetime.datetime.now()

            company_news = {}
            company_news['companyId'] = ''
            company_news['location']=''
            company_news['comment']=''
            company_news['Date']= news_date
            company_news['Crawled_on']=crawled_date
            company_news['title']=title
            company_news['Language']= language
            company_news['announcementType']= announcement_type
            company_news['Source'] = page_source
            company_news['News_Weblink'] = i
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
