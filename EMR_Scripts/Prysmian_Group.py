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

from selenium.webdriver.common.touch_actions import TouchActions

from urllib.parse import urlparse

import re

import traceback

import urllib

import dateparser

from datetime import datetime

from bson.objectid import ObjectId

from urllib.error import HTTPError

from urllib.request import Request, urlopen

# ************************************************************************
# defining variables

running_Sequence = []

started_on = datetime.now()

c_name = 'Prysmian_Group' # Name of the Collection

total_crwalled_links = 0

Already_exist = 0

# *************************************************************************

# trying to connect with mongodb

try:
    file = open("/home/emr/config.json")
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
    links = ["https://www.prysmiangroup.com/en/media/news","https://www.prysmiangroup.com/en/media/press-releases"]
    for i in links:
        result = requests.get(i)
        page_source = i
        soup = BeautifulSoup(result.content, 'lxml')
        loop_number = int(soup.find("li", class_='pager-last').find("a").get("href").split("=")[1])
        for pages in range(loop_number + 1):
            main_url = i + "?page={}".format(pages)
            response = requests.get(main_url)
            soup = BeautifulSoup(response.content, 'lxml')
            all_links = soup.find_all("a", class_='btn btn-default btn-discover toggle-stick-to-bottom')
            dates = soup.find_all("div", class_="news-archive-date")
            dates_list = []
            for z in dates:
                dates_list.append(z.text.strip())
                
            links_list = []
            for j in all_links:
                links_list.append("https://www.prysmiangroup.com" + j.get("href"))
                
            db_list = []
            mydoc = collection.find()
            for x in mydoc:
                db_list.append(x['News_Weblink'])

            for k,l in zip(links_list, dates_list):
                if k in db_list:
                    # print("Link Already exists in database")
                    total_crwalled_links += 1
                    Already_exist += 1
                    continue
                else:
                    res = requests.get(k)
                    soup = BeautifulSoup(res.content, 'lxml')
                    try:
                        title = soup.find("meta", attrs = {"property":"og:title"}).get("content")
                    except:
                        title = ""
                    try:
                        sub_category = soup.find("meta", attrs = {"property":"og:type"}).get("content")
                    except:
                        sub_category = ""
                    try:
                        news_weblink = "https://" + soup.find("meta", attrs = {"property":"og:url"}).get("content")
                    except:
                        news_weblink = ""
                    try:
                        analysis = soup.find("meta", attrs = {"name":"description"}).get("content")
                    except:
                        analysis = ""
                    try:
                        image = soup.find("meta", attrs = {"property":"og:image"}).get("content")
                    except:
                        image = ""
                    news_date = dateparser.parse(l)
                    try:
                        announcement = soup.find("div", class_='main-container container-fluid pry-container').text
                    except:
                        announcement = ""
                    try:
                        announcement_type = news_weblink.replace("https://www.prysmiangroup.com/en/","").split("/")[0]
                    except:
                        announcement_type = ""
                    language = "en-US"
                    crawled_date = datetime.now()
                    
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

