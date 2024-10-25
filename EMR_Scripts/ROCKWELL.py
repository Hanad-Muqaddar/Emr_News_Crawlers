# Packages to be imported
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

from requests_html import HTMLSession

import re

import traceback

from scrapy import Selector

import urllib

import dateparser

import datetime

from bson.objectid import ObjectId

from urllib.error import HTTPError

from urllib.request import Request, urlopen

from scrapy import Selector

import feedparser

from newspaper import fulltext
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
running_Sequence = []

started_on = datetime.datetime.now()

c_name = 'ROCKWELL' # Name of the Collection

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

def set_proxy(session, proxy):
    session.proxies = {
        'http': f"http://{proxy}",
        'https': f"http://{proxy}"
    }

try:
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }

    Main_url = "https://www.rockwellautomation.com"
    page_source = "https://www.rockwellautomation.com/en-us/company/investor-relations/news/jcr:content/root/main-par/generic_container/GenericContainerParsys/column_control_1712903781/Col1/generic_filter.genericSearch.json?rootPath=%2Fcontent%2Frockwell-automation%2Fglobal%2Fna%2Fen&deepCount=false&contentType=news-press&company=rockwell-automation%3Ametadata%2Fcompany%2Fnewsroom%2Fpress-releases&sort=pubAsc&numPerPage=10&page=1"
    
    session = HTMLSession()
    set_proxy(session, 'waleeProxy:Cheeta@1@uk.proxymesh.com:31280')
    result = session.get(page_source, headers=headers)
    result_json = result.json()
    
    news_links = []
    for i in result_json["results"]:
        link = i["link"]
        news_links.append(link)

    db_list = []
    mydoc = collection.find()
    for x in mydoc:
        db_list.append(x['News_Weblink'])

    Emr_Crawlers_Logs(c_name,page_source,news_links)

    for i in news_links:
        
        if i in db_list:
            Already_exist += 1
            total_crwalled_links += 1
            print("Already Crawled")
            continue
        
        else:
            result1 = session.get(i,headers=headers)
            response1 = Selector(result1)
            try:
                ne_date = response1.xpath('//div[@class="hero-banner__subtitle-text"]/text()').get()
                f_ne_date = ne_date.split('|')[1]
                news_date = dateparser.parse(f_ne_date,  settings={'DATE_ORDER': 'DMY'})
                print(news_date)
            except:
                news_date = ""
            try:
                title = response1.xpath('//h1[@class="hero-banner__title"]/text()').get().strip()
                print(title)
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
                announcement = fulltext(result1.text)
                announcement = announcement.replace('\n','<br>')
                print(announcement)
            except:
                announcement = ""
            announcement_type = "Press Release"
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
    
    # url = "https://ir.rockwellautomation.com/services/EventService.svc/GetEventList"
    # payload = json.dumps({
    #         "serviceDto": {
    #             "ViewType": "2",
    #             "ViewDate": "",
    #             "Signature": "",
    #             "LanguageId": "1",
    #             "RevisionNumber": "1",
    #             "TagList": [],
    #             "StartIndex": 0,
    #             "ItemCount": 25,
    #             "IncludeTags": True
    #         },
    #         "excludeSelection": 0,
    #         "year": -1,
    #         "eventSelection": 3,
    #         "sortOperator": 1,
    #         "includePressReleases": True,
    #         "includePresentations": True,
    #         "includeFinancialReports": True
    #         })
    
    # response = session.post(url, data=payload)
    # print(f"\n\n\n{response.text}\n\n\n")
    # Base_Link = "https://ir.rockwellautomation.com"
    # for j in response.json()['GetEventListResult']:
        
    #     db_list = []
    #     mydoc = collection.find()
    #     for x in mydoc:
    #         db_list.append(x['News_Weblink'])
        
    #     web_link = Base_Link + j['LinkToDetailPage']
    #     if web_link in db_list:
    #         Already_exist += 1
    #         total_crwalled_links += 1
    #         continue
    #     else:
    #         result1 = session.get(web_link)
    #         response1 = Selector(result1)
    #         try:
    #             news_date = j['StartDate']
    #             news_date = dateparser.parse(news_date,  )
    #         except:
    #             news_date = ""
    #         try:
    #             title = j['Title']
    #         except:
    #             title = ""
    #         try:
    #             analysis = response1.xpath("//meta[@name='description']/@content").get()
    #         except:
    #             analysis = ""
    #         try:
    #             image = response1.xpath("//meta[@property='og:image']/@content").get()
    #         except:
    #             image = ""
    #         sub_category = ""
    #         try:
    #             announcement = fulltext(result1.text)
    #             announcement = announcement.replace('\n','<br>')
    #         except:
    #             announcement = ""
    #         announcement_type = "Events"
    #         language = "en-US"
    #         page_source = "https://www.rockwellautomation.com/en-us/company/investor-relations/events-presentations.html"
    #         crawled_date = datetime.datetime.now()

    #         company_news = {}
    #         company_news['companyId'] = ''
    #         company_news['location']=''
    #         company_news['comment']=''
    #         company_news['Date']= news_date
    #         company_news['Crawled_on']=crawled_date
    #         company_news['title']=title
    #         company_news['Language']= language
    #         company_news['announcementType']= announcement_type
    #         company_news['Source'] = page_source
    #         company_news['News_Weblink'] = web_link
    #         company_news['photo']= image
    #         company_news['videos']= ''
    #         company_news['announcement']=announcement
    #         company_news['historySubCategory']= sub_category
    #         company_news['analysis'] = analysis
    #         print(company_news)
    #         print("********************")
    #         try:
    #             # collection.insert_one(company_news)
    #             total_crwalled_links += 1
    #         except Exception as e:
    #             running_Sequence.append(e)
    
    if Already_exist >= 1:

        tmp_txt = ' , from which '+str(Already_exist) +' Links were Already Crawled '
    else:

        tmp_txt = ''

    running_Sequence.append(str(total_crwalled_links) + ' Links are crawled ' + tmp_txt)

    ended_on = datetime.datetime.now()
except Exception as e:
    Error_Time =  datetime.datetime.now()

    Reported_Error = traceback.format_exc()
    print(Reported_Error, e)

    running_Sequence.append(e)

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
