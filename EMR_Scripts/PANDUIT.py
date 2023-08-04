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


from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


# ************************************************************************

running_Sequence = []

started_on = datetime.datetime.now()

c_name = 'PANDUIT' # Name of the Collection

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
    opts.headless = False

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(version='114.0.5735.90').install()), options=opts)
    driver.get("https://www.panduit.com/en/about/media-resources.html")
    Main_url = "https://www.panduit.com"


    news_links = []
    news_dates = []
    links = driver.find_elements(By.XPATH, '//ul/li[1]//div[@class="fullwidthcontainer section"]//div[@class="text section"]')
    for link in links:
        news_link = link.find_element(By.XPATH, ".//a[text() = 'Read More']").get_attribute('href')
        news_links.append(news_link)
        try: 
            news_date = link.find_element(By.XPATH, "./div/p[1]/b").text
            news_dates.append(news_date)
        except:
            news_date = ""
            news_dates.append(news_date)

    print(news_links)
    print(len(news_links))
    print(news_dates)
    print(len(news_dates))

    db_list = []
    mydoc = collection.find()
    for x in mydoc:
        db_list.append(x['News_Weblink'])

    for news_link , d in zip(news_links,news_dates):

    # headers = {
    #     'Cookie': 'AWSALB=JbCkIr+AtI72m9HbLWNw7bktd7WB3btj/faED/qYUQeUgoe+/I+HDkbmL65o1ounCii6QADP+k7lK3Ot2vZTuah5pBapeDyGaq4aj84Y2jWINxGXdTDife5ObF3E; AWSALBCORS=JbCkIr+AtI72m9HbLWNw7bktd7WB3btj/faED/qYUQeUgoe+/I+HDkbmL65o1ounCii6QADP+k7lK3Ot2vZTuah5pBapeDyGaq4aj84Y2jWINxGXdTDife5ObF3E',
    #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36'
    #     }
    # result = requests.get("https://www.panduit.com/en/about/media-resources.html", headers=headers)
    # response = Selector(result)
    # divs = response.css(".enhanced-columncontrol")
    # for i in divs:
        
    #     try:
    #         news_link =  i.xpath(".//a[contains(text(), 'Read More')]/@href").get()
    #         news_link = "https://www.panduit.com" + news_link.replace("/content/panduit/na", "")
    #         # print(news_link)
    #     except:
    #         news_link = ""
    #     if news_link == "":
    #         continue
        if news_link in db_list:
            Already_exist += 1
            total_crwalled_links += 1
            print("Already Crawled")
            continue
        else:
            # try:
            #     final_date = ""

            #     # news_date = i.xpath("normalize-space()").get()
            #     # matches = datefinder.find_dates(news_date)
            #     # date = [match for match in matches]
            #     # final_date = date[0]
            #     # # news_date = i.find("span", class_='date').text
            #     # # news_date = dateparser.parse(news_date,  settings={'DATE_ORDER': 'DMY'})
            # except:
            #     final_date = ""
            new_request = requests.get(news_link , headers=headers)
            response1 = Selector(new_request)
            try:
                title = response1.xpath("//title/text()").get().replace("Panduit |", "").strip()
                print(title)
            except:
                title = ""
            try:
                analysis = response1.xpath('//meta[@name="description"]/@content').get()
                print(analysis)
            except:
                analysis = ""

            try:            
                news_date = dateparser.parse(d,  settings={'DATE_ORDER': 'MDY'} )
                print(news_date)            
            except:
                news_date = ""

            try:
                image = ""
            except:
                image = ""
            sub_category = ""
            announcement = response1.xpath("normalize-space(//div[@class='aem-Grid aem-Grid--8 aem-Grid--default--8 '])").get()
            print(announcement)
            announcement_type = "News"
            language = "en-US"
            page_source = "https://www.panduit.com/en/about/media-resources.html"
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
            company_news['News_Weblink'] = news_link
            company_news['photo']= image
            company_news['videos']= ''
            company_news['announcement']=announcement
            company_news['historySubCategory']= sub_category
            company_news['analysis'] = analysis
            # print(company_news)
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
