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
from newspaper import fulltext
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

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

# defining variables
running_Sequence = []

started_on = datetime.now()

c_name = 'Belden_International'

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

    opts = Options()
    user_agent = "Mozilla/5.0 (Linux; Android 9; SM-N975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36"
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-automation")
    opts.add_argument("--no-sandbox")
    opts.add_argument('--profile-directory=Default')
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--lang=en")
    opts.add_argument("--enable-javascript")
    opts.add_argument("--enable-cookies")
    opts.add_argument(f'--user-agent={user_agent}')
    opts.headless = False
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    driver.maximize_window()

    # headers = {
    #     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #     'cookie': '__uxq412__ses.ddf1=*; sp=1e9d9deb-261f-4a6b-87b4-19e6534c2e8c; OptanonAlertBoxClosed=2024-09-26T10:28:17.477Z; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Sep+26+2024+15%3A28%3A17+GMT%2B0500+(Pakistan+Standard+Time)&version=202405.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=cf119496-bdcb-48a4-84db-a675861b3ad7&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&intType=1; _ga_5MPZPNNXMT=GS1.1.1727346497.1.0.1727346497.0.0.0; _ga=GA1.1.1705416635.1727346498; __uxq412__id.ddf1=75f4d860-09ea-4e13-a386-e63a4737ac47.1727346494.1.1727346525.1727346494.a08a122e-f920-4c60-af5e-14e66416057b',
    #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
    #     }
    

    Web_Page = "https://investor.belden.com/news/default.aspx"
    driver.get(Web_Page)
    time.sleep(5)
    Main_url = "https://investor.belden.com"

    news_links = []
    links = driver.find_elements(By.XPATH, '//div[@class="module_headline"]/a[@class="module_headline-link"]')
    for link in links:
        news_link = link.get_attribute('href')
        news_links.append(news_link)

    print(news_links)
    print(len(news_links))

    db_list = []
    mydoc = collection.find()
    for x in mydoc:
        db_list.append(x['News_Weblink'])
    
    for i in news_links:
        if i in db_list:
            total_crwalled_links += 1
            Already_exist += 1
            print("Already Crawled")
            continue
        else:
            driver.get(i)  
            # result1 = requests.get(i, headers=headers)
            time.sleep(3)
            response1 = Selector(text=driver.page_source)

            try:
                title = response1.xpath('normalize-space(//h3[contains(@class,"evergreen-news-title")])').get()
                print(title)
            except:
                continue
                title = ""
            
            announcement_type = "News"
            language = "en-us"
            image = ""
            sub_category = ""
            
            try:
                analysis = response1.xpath('//meta[@name="description"]/@content').get()
            except:
                analysis = ""
            try:
                N_date = response1.xpath('normalize-space(//span[contains(@id,"_spanDate")])').get()
                print(N_date)
                news_date = dateparser.parse(N_date,  settings={'DATE_ORDER': 'DMY'})
                print(news_date)
            except:
                news_date = ""

            news_weblink = i
            print(news_weblink)

            try:
                announcement = fulltext(driver.page_source)
                announcement = announcement.replace('\n','<br>')
                print(announcement)                
            except:
                announcement = ""

            
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
            company_news['Source'] = Web_Page
            company_news['News_Weblink'] = news_weblink
            company_news['photo']= image
            company_news['videos']= ""
            company_news['announcement']=announcement
            company_news['historySubCategory']= sub_category
            company_news['analysis'] = analysis
            try:
                collection.insert_one(company_news)
                total_crwalled_links += 1
            except Exception as e:
                running_Sequence.append(e)

    Emr_Crawlers_Logs(c_name+"_Second",Web_Page,news_links)
    if Already_exist >= 1:

        tmp_txt = ' , from which '+str(Already_exist) +' Links were Already Crawled '

    else:

        tmp_txt = ''

    running_Sequence.append(str(total_crwalled_links) + ' Links are crawled ' + tmp_txt)

    ended_on = datetime.now()
except Exception as e:
    print(e)
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

# error_logs.insert_one(log)
