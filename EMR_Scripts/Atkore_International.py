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

from urllib.parse import urlparse

import re

import traceback

import urllib

import dateparser

from datetime import datetime

from bson.objectid import ObjectId

from urllib.error import HTTPError

from urllib.request import Request, urlopen
from scrapy import Selector

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.service import Service
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
# ************************************************************************
# defining variables

running_Sequence = []

started_on = datetime.now()

c_name = 'Atkore_International' # Name of the Collection

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

    cookie = "_ga=GA1.2.48214244.1618300802; _fbp=fb.1.1618300804846.1549346976; cookielawinfo-checkbox-necessary=yes; cookielawinfo-checkbox-non-necessary=yes; visitor_id912931=37938159; visitor_id912931-hash=39db0b029cefdcf52ac71dd400c4318403a9dfc692e57a92dfee15afe35d1dd24939d672209096cfaa42d506f5b670a6da133ed7; CookieLawInfoConsent=eyJuZWNlc3NhcnkiOnRydWUsIm5vbi1uZWNlc3NhcnkiOnRydWV9; viewed_cookie_policy=yes; _gid=GA1.2.57467576.1623049451; _gat_gtag_UA_39634549_1=1"
    headers = {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control" : "max-age=0",
    "cookie": cookie,
    "sec-ch-ua" : '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36}"
            }

    Web_Page = "https://investors.atkore.com/news/default.aspx"      
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opts)

    driver.get(Web_Page)
    time.sleep(4)

    N_links = []
    links = driver.find_elements(By.XPATH, '//div[@id="newsList"]//div[@class="module_item-container"]//a[@class="module_headline-link"]')
    for link in links:
        news_link = link.get_attribute('href')
        N_links.append(news_link)

    print(N_links)


    # Creating a list of links already avilable in database
    links_list = []
    mydoc = collection.find()
    for x in mydoc:
        links_list.append(x['News_Weblink'])
      
    # Emr_Crawlers_Logs(c_name,Web_Page,N_links)

    for i in N_links:
        
        if i in links_list:
            total_crwalled_links += 1
            Already_exist += 1
            print("Already Crawled")
            continue
        else:
            response = requests.get(i, headers=headers)
            data = BeautifulSoup(response.content, 'lxml')
            try:
                title = data.find('title').text
            except:
                title = ""
            announcement_type = "News"
            try:
                sub_category = data.find('meta', attrs = {"property":"og:type"}).get("content")
            except:
                sub_category = ""
            try:
                language = data.find('meta', attrs = {"property":"og:locale"}).get("content")
            except:
                language = ""
            try:
                analysis = data.find('meta', attrs = {"property":"og:description"}).get("content")
            except:
                analysis = ""
            try:
                date = data.find('meta', attrs = {"property":"article:published_time"}).get("content")
                news_date = dateparser.parse(date,  settings={'DATE_ORDER': 'YMD'} )
            except:
                news_date = ""
            page_source = "https://www.atkore.com/news/"
            news_weblink = i
            try:
                image = data.find('meta', attrs = {"property":"og:image"}).get("content")
            except:
                image = ""
            try:
                announcement = data.find("div", id="main-content").find("div", class_='col-md-10').text
            except:
                announcement = data.find("div", id="main-content").text
            
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

log['Ending_time'] = Error_Time if rep == '' else ended_on

log['Error_Detail'] =  Error if rep == '' else ''

log['Crawler_Runing Sequence'] = running_Sequence if running_Sequence else ''

log['Links_Skipped'] = Already_exist

log['Last_news_crawl_time'] = last_time

log['Browser'] = 'None'

error_logs.insert_one(log)
