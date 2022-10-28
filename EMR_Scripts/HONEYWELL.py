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

# ************************************************************************
running_Sequence = []

started_on = datetime.datetime.now()

c_name = 'HONEYWELL' # Name of the Collection

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
def parse_filtered_news(announcement):
    api_url = "https://admin.new.emr-online.com/api/history/filterbody"
    payload = json.dumps({
                            "originalBody": announcement
                            })
    headers = {
                'Content-Type': 'application/json'
                }
    return_response = requests.request("POST", api_url, headers=headers, data=payload)
    new_data = return_response.text
    new_data = json.loads(new_data)
    status = new_data['statusCode']
    if status == 200:
        return new_data
    else:
        new_data =  ""
        return new_data
    
try:
    result = requests.get("https://www.honeywell.com/us/en/press")
    response = Selector(result)
    links = response.xpath('//div[@class="list-component__item-headline"]/parent::a/@href').getall()
    final_links = ["https://www.honeywell.com" + link if "https://www.honeywell.com" not in link else link for link in links[:10]]
    # print(final_links)
    db_list = []
    mydoc = collection.find()
    for x in mydoc:
        db_list.append(x['News_Weblink'])
    for i in final_links:
        if i in db_list:
            Already_exist += 1
            total_crwalled_links += 1
            continue
        else:
            result1 = requests.get(i)
            response1 = Selector(result1)
            try:
                news_date = response1.css(".author-date__time::text").get()
                news_date = dateparser.parse(news_date,  settings={'DATE_ORDER': 'DMY'})
            except:
                news_date = ""
            try:
                title = response1.xpath("//title/@text()").get()
            except:
                title = ""
            try:
                analysis = response1.xpath("//meta[@name='description']/@content").get()
            except:
                analysis = ""
            try:
                image = response1.xpath("//meta[@property='og:image']/@content").get()
            except:
                image = ""
            sub_category = ""
            
            try:
                announcement = response1.css('.aem-Grid--phone--10').get()
                announcement = announcement.replace('\n','<br>')
                replace1 = response1.css(".headline h1").get()
                replace2 = response1.css(".author-date").get()
                replace3 = response1.css(".socialutilitylinks").get()
                try:
                    announcement = announcement.replace(replace1, "")
                except:
                    pass
                try:
                    announcement = announcement.replace(replace2, "")
                except:
                    pass
                try:
                    announcement = announcement.replace(replace3, "")
                except :
                    pass
                return_data = parse_filtered_news(announcement)
                announcement = return_data['filteredBody']
                emr_essentail = return_data['emrEssential']
                emr_executive = return_data['emrExecutive']
                emr_lite = return_data['emrLite']
                emr_html = return_data['emrHtmlText']
            except:
                announcement = ""
                emr_essentail = ""
                emr_executive = ""
                emr_lite = ""
                emr_html = ""
                
            announcement_type = ""
            language = "en-US"
            page_source = "https://www.honeywell.com/us/en/press"
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
            company_news['emrExecutive'] = emr_executive
            company_news['emrEssential'] = emr_essentail
            company_news['emrLite'] = emr_lite
            company_news['News_Html'] = emr_html
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
