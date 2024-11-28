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
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from googletrans import Translator
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
# # ================================================================================

# ************************************************************************
# defining variables

running_Sequence = []

started_on = datetime.now()

c_name = 'Belden_International' # Name of the Collection

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
      # defining variables
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

    Web_Page = "https://www.belden.com/news#sort=%40contentpublisheddate%20descending"    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    driver.get(Web_Page)
    time.sleep(4)

    N_links = []
    links = driver.find_elements(By.XPATH, '//div[@class="CoveoResultList"]//div[@class="coveo-list-layout CoveoResult"]//a')
    for link in links:
        news_link = link.get_attribute('href')
        N_links.append(news_link)

    print(N_links)

    links_list = []
    mydoc = collection.find()
    for x in mydoc:
        links_list.append(x['News_Weblink'])

    for j in N_links:
        
        if j in links_list:
            total_crwalled_links += 1
            Already_exist += 1
            print("Already Crawled")
            continue
        else:
            print(j)
            response = requests.get(j)
            soup = BeautifulSoup(response.content, 'lxml')
            try:
                title = soup.find("title").text
                print(title)
            except:
                title = ""
            try:
                analysis = soup.find("meta", attrs={"name":"description"}).get("content")
            except:
                analysis = ""
            try:
                d = soup.find("div", class_='field-content-published-date').text
                news_date = dateparser.parse(d,  settings={'DATE_ORDER': 'MDY'} )
            except:
                news_date = ""
            try:
                announcement = soup.find("div", id='content').find("div", class_='row component column-splitter').text.strip()
            except:
                announcement = ""
            try:
                image = "https://www.belden.com" + soup.find("img").get("src")
            except:
                image = ""
            try:
                announcement_type = soup.find("div", class_="field-pre-text").text
            except:
                announcement_type = ""
            try:
                sub_category = soup.find('meta', attrs = {"property":"og:type"}).get("content")
            except:
                sub_category = ""
            page_source = "https://www.belden.com/news#sort=%40contentpublisheddate%20descending"
            language = "en-US"
            
            date = datetime.now()
            # Creating a list of links already avilable in database
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
            company_news['News_Weblink'] = j
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

    Emr_Crawlers_Logs(c_name,Web_Page,N_links)
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
