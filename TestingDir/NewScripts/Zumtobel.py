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

options = Options()
options.add_argument("--window-size=1980,1020")
options.add_argument("--headless")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36")


running_Sequence = []

started_on = datetime.datetime.now()

c_name = 'Zumtobel' # Name of the Collection

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
    # driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver')
    driver = webdriver.Chrome(executable_path='/home/ubuntu/chrome_driver/chromedriver.exe', options= options)
    links = ['https://z.lighting/en/group/news-insights/?category=company', 'https://z.lighting/en/group/news-insights/?category=zumtobel']
    for i in links:
        driver.get(i)
        # driver.get_screenshot_as_file("/home/emr/TestingDir/ScreenShots/screenshot.png")
        page_source = i
        time.sleep(3)
        try:
            accept_button = driver.find_element_by_xpath("//div[@class='CookieAgreement-buttonWrapper']/button")
            accept_button.click()
        except:
            pass
        # page_source = i
        time.sleep(15)
        # try:
        #     while True:
        #         button = driver.find_element_by_xpath("//button[@class='s-button-white NewsLandingItems-showMore']")
        #         button.click()
        #         time.sleep(3)
        # except Exception as e:
        #     pass
        # driver.get_screenshot_as_file("/home/emr/TestingDir/ScreenShots/screenshot2.png")
        time.sleep(3)
        response = Selector(text=driver.page_source.encode('utf-8'))
        head_link = response.css(".NewsLandingHead-title a::attr(data-url)").get()
        all_links = response.css(".NewsLandingItems-itemLink ::attr(href)").getall()
        all_links.append(head_link)
        f_links = ['https://z.lighting' + j for j in all_links]
        # print('Links aagay hn')
        # print(f_links)
        for j in f_links:
            news_weblink = j
            db_list = []
            mydoc = collection.find()
            # print('1')
            for x in mydoc:
                db_list.append(x['News_Weblink'])
            # print('2')
            if news_weblink in db_list:
                # print('skip')
                total_crwalled_links += 1
                Already_exist += 1
                continue
            driver.get(j)
            # print("Inner Links chal raha hn")
            time.sleep(5)
            response1 = Selector(text=driver.page_source.encode('utf-8'))
            try:
                image = 'https://z.lighting' + response1.css(".NewsStoryPopup-image img::attr(src)").get()
            except:
                image = ""
            try:
                title = response1.css(".NewsStoryPopup-title ::text").get()
            except:
                title = ""
            try:
                announce = response1.css('.NewsStoryPopup-blockWrapper p::text').getall()
                announcement = ""
                for j in announce:
                    announcement = announcement + j
            except:
                announcement = ""
            try:
                date = response1.css('.NewsStoryPopup-date ::text').get()
                news_date = dateparser.parse(date)
            except:
                news_date = ""
            try:
                analysis = response1.css('.NewsStoryPopup-blockWrapper p::text').get()
            except:
                analysis = ""

            announcement_type = 'News'
            crawled_on_date = datetime.datetime.now()
            language = "en"
            sub_category = ""
            
            company_news = {}
            company_news['companyId'] = ''
            company_news['location']=''
            company_news['comment']=''
            company_news['Date']=news_date
            company_news['Crawled_on']=crawled_on_date
            company_news['title']= title
            company_news['Language']= language
            company_news['announcementType']= announcement_type
            company_news['Source'] = page_source
            company_news['News_Weblink'] = news_weblink
            company_news['photo']= image
            company_news['videos']= ''
            company_news['announcement']= announcement
            company_news['historySubCategory']= sub_category
            company_news['analysis'] = analysis
            try:
                collection.insert_one(company_news)
                # print("Inserted")
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

