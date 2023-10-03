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
# ************************************************************************
# defining variables

running_Sequence = []

started_on = datetime.now()

c_name = 'Acquity_Brands' # Name of the Collection

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
# Check Last News addedd in DB for the Collection

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

def get_all_links_and_dates():
    import requests
    from bs4 import BeautifulSoup
    iterator_list = [2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022]
    error_links = []
    no_news_links = []
    all_links = []
    all_dates = []
    for i in reversed(iterator_list):
        link = "https://www.investors.acuitybrands.com/news-releases?9e1608fd_year%5Bvalue%5D={}&op=Filter&9e1608fd_widget_id=9e1608fd&form_build_id=form-AMfIjMtTMV-ccl57LMyeLuiEhh_co9fLurJOLZqzCkU&form_id=widget_form_base".format(i)
        try:
            res = requests.get(link)
        except:
            error_links.append(link)
        try:
            soup = BeautifulSoup(res.content, 'lxml')
            news = soup.find("ul", class_='text-list-date unlisted').find_all("li")
        except:
            no_news_links.append(link)
        try:
            for j in news:
                all_links.append("https://www.investors.acuitybrands.com" + j.find("a").get('href'))
                all_dates.append(j.find("span").text.strip())
            while True:
                try:
                    next_page = soup.find("div", class_='nir-widget--pager').find("li", class_='pager__item pager__item--next').find("a").get("href")
                    next_page = "https://www.investors.acuitybrands.com/news-releases" + next_page
                except:
                    next_page = None
                if next_page:
                    res = requests.get(next_page)
                    soup = BeautifulSoup(res.content, 'lxml')
                    news = soup.find("ul", class_='text-list-date unlisted').find_all("li")
                    for k in news:
                        all_links.append("https://www.investors.acuitybrands.com" + k.find("a").get('href'))
                        all_dates.append(k.find("span").text.strip())
                else:
                    break
        except:
            continue
    return all_links,all_dates,error_links,no_news_links

def get_newsweblinks(collection):
    my_doc = collection.distinct('News_Weblink')
    return my_doc

try:
    links, dates, error_l, no_news = get_all_links_and_dates()
    main_news_list = get_newsweblinks(collection)
    for i,j in zip(links,dates):
        Emr_Crawlers_Logs(c_name,i)
        if i in main_news_list:
            total_crwalled_links += 1
            Already_exist += 1
            continue
        else:
            news_weblink = i
            result = requests.get(news_weblink)
            soup = BeautifulSoup(result.content, 'lxml')
            try:
                title = soup.find("meta", attrs={'property':"og:title"}).get("content").split("|")[0].strip()
            except:
                title = ""
            try:
                analysis = soup.find("meta", attrs={"property":"og:description"}).get("content")
            except:
                analysis = ""
            try:
                announcement = soup.find("div", id='block-nir-pid2472-content').text
            except:
                announcement = ""
            try:
                sub_category = soup.find("meta", attrs={"property":"og:type"}).get("content")
            except:
                sub_category = ""
            try:
                image = soup.find("meta", attrs={"itemprop":"image"}).get("content")
            except:
                image = ""
            announcement_type = "Investor Relations News Releases"
            try:
                date = j
                news_date = dateparser.parse(date)
            except:
                news_date = ""
            try:
                pdf_link = "https://www.investors.acuitybrands.com/" + soup.find("span", class_='file file--mime-application-pdf file--application-pdf').find("a").get("href")
            except:
                pdf_link = ""
            crawled_date = datetime.now()
            language = "en-US"
            page_source = "https://www.investors.acuitybrands.com/news-releases"
            
            investor_news = {}
            investor_news['companyId'] = ''
            investor_news['location']=''
            investor_news['comment']=''
            investor_news['Date']= news_date
            investor_news['Crawled_on']=crawled_date
            investor_news['title']=title
            investor_news['Language']= language
            investor_news['announcementType']= announcement_type
            investor_news['Source'] = page_source
            investor_news['News_Weblink'] = news_weblink
            investor_news['photo']= image
            investor_news['videos']= ''
            investor_news['announcement']=announcement
            investor_news['historySubCategory']= sub_category
            investor_news['analysis'] = analysis
            investor_news['Pdf'] = pdf_link
            try:
                collection.insert_one(investor_news)
                main_news_list.append(news_weblink)
                total_crwalled_links += 1
                print("Successfully Inserted Record.")
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

log['Crawler_name'] = 'Acuity_Brands_Investors.py'

log['Crawler_type'] = c_name

log['Starting_time'] = started_on

log['Ending_time'] = Error_Time if rep == '' else ended_on

log['Error_Detail'] =  Error if rep == '' else ''

log['Crawler_Runing Sequence'] = running_Sequence if running_Sequence else ''

log['Links_Skipped'] = Already_exist

log['Last_news_crawl_time'] = last_time

log['Browser'] = 'Chrome'

error_logs.insert_one(log)