# Packages to be imported
from functools import total_ordering
from hashlib import new
from urllib import response
import requests

import time

import json

from random import randint

from bs4 import BeautifulSoup

from pymongo import MongoClient

from bs4 import BeautifulSoup

from selenium import webdriver

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

import datetime

from bson.objectid import ObjectId

from urllib.error import HTTPError

from urllib.request import Request, urlopen

from scrapy import Selector
# ************************************************************************

running_Sequence = []

started_on = datetime.datetime.now()

c_name = 'SCHNIDER_ELECTRIC' # Name of the Collection

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

    # running_Sequence.append('Last News Crawled on -> '+str(last_insertion['Date'].date()))

    Crwl_time = last_insertion['Date']

# ****************************************************************************

####################################################

############# Every Company Logic Here #############

####################################################

# *****************************************************************************

try:
    proxies = {'http': 'http://alihaider99:cheeta@jp.proxymesh.com:31280',
            'https': 'http://alihaider99:cheeta@jp.proxymesh.com:31280'}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
    result = requests.get("https://www.se.com/us/en/about-us/newsroom/news/", headers=headers, proxies=proxies)
    res = Selector(result)
    data = res.css(".sdl-wiztopic-press-releases_wiztopic-card .wiztopic-content")
    for i in data:
        try:
            news_weblink = "https://www.se.com" + i.css("a::attr(href)").get()
        except:
            news_weblink = ""
        
        if news_weblink == "":
            continue
            
        db_list = []
        mydoc = collection.find()
        for x in mydoc:
            db_list.append(x['News_Weblink'])
        if news_weblink in db_list:
            total_crwalled_links += 1
            Already_exist += 1
            continue
        else:
            result2 = requests.get(news_weblink, headers=headers)
            response1 = Selector(result2)
            date_get = response1.css(".sdl-wiztopic-press-release_publication-data p:nth-child(2) span").xpath("normalize-space()").get()
            location = response1.css('.sdl-wiztopic-press-release_publication-data p:nth-child(1) span').xpath("normalize-space()").get()
            try:
                image = response1.xpath("//meta[@name='og:image']/@content").get()
            except:
                image = ""
            try:
                analysis = ""
            except:
                analysis = ""
            try:
                title = response1.xpath('//meta[@name="og:title"]/@content').get()
            except:
                title = ""
            try:
                news_date = date_get
                news_date = dateparser.parse(news_date)
            except:
                news_date = ""
            try:
                sub_category = response1.xpath('//meta[@name="og:type"]/@content').get()
            except:
                sub_category = ""
            try:
                announcement_type = "Press Release"
            except:
                announcement_type = ""
            try:
                announcement = response1.xpath("normalize-space(//div[@class='wiztopic-rich-text'])").get()
            except:
                announcement = ""
            language = "en"
            page_source = "https://www.se.com/us/en/about-us/newsroom/news/"
            crawled_date = datetime.datetime.now()
            company_news = {}
            company_news['companyId'] = ''
            company_news['location'] = location
            company_news['comment']=''
            company_news['Date']= news_date
            company_news['Crawled_on']=crawled_date
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

# error_logs.insert_one(log)
