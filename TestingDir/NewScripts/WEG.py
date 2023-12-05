# Packages to be imported
import requests

import time

import json

from random import randint

from pymongo import MongoClient

from bs4 import BeautifulSoup

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

# from datetime import datetime
import datetime

from bson.objectid import ObjectId

from urllib.error import HTTPError

from urllib.request import Request, urlopen

from scrapy import Selector

import xmltodict
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

started_on = datetime.datetime.now()

c_name = 'WEG' # Name of the Collection

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
    print("Reached to first line")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
    main_url = "https://www.weg.net/institutional/US/en/rss"
    try:
        result = requests.get(main_url, headers=headers)
    except Exception as e:
        print(e)

    xml_data = xmltodict.parse(result.text)
    json_dump = json.dumps(xml_data)
    json_data = json.loads(json_dump)
    urls = json_data['rss']['channel']['item']

    db_list = []
    mydoc = collection.find()
    for x in mydoc:
        db_list.append(x['News_Weblink'])
    
    Optimization_links = []
    page_source = "https://www.weg.net/institutional/US/en/all-news/list"
    
    for i in range(len(urls)):
        try:
            image = json_data['rss']['channel']['item'][i]['content:encoded']
            link = re.compile("""src=[\"\'](.+)[\"\']""")
            links = link.finditer(image)
            for l in links:
                img = l.groups()
            image = list(img)[0]
        except:
            image = ""
        try:
            announcement_type = "Press Release"
        except:
            announcement_type = ""
        try:
            news_date = dateparser.parse(json_data['rss']['channel']['item'][i]['pubDate'])
        except:
            news_date = ""
        try:
            news_weblink = json_data['rss']['channel']['item'][i]['link']
            # print(news_weblink)
        except:
            news_weblink = ""
        Optimization_links.append(news_weblink)
        
        if news_weblink in db_list:
            total_crwalled_links += 1
            Already_exist += 1
            print("Already Crawled")
            continue
        else:
            try:
                announcement = json_data['rss']['channel']['item'][i]['description']
            except:
                announcement = ""
            try:
                title = json_data['rss']['channel']['item'][i]['title']
            except:
                title = ""
            crawled_on_date = datetime.datetime.now()
            analysis = ""
            

            company_news = {}
            company_news['companyId'] = ''
            company_news['location']=''
            company_news['comment']=''
            company_news['Date']=news_date
            company_news['Crawled_on']=crawled_on_date
            company_news['title']= title
            company_news['Language']= 'English'
            company_news['announcementType']= announcement_type
            company_news['Source'] = page_source
            company_news['News_Weblink'] = news_weblink
            company_news['photo']= image
            company_news['videos']= ''
            company_news['announcement']= announcement
            company_news['historySubCategory']= ''
            company_news['analysis'] = analysis
            try:
                collection.insert_one(company_news)
                total_crwalled_links += 1
            except Exception as e:
                print(e)
                running_Sequence.append(e)
    
    Emr_Crawlers_Logs(c_name,page_source,Optimization_links)
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

