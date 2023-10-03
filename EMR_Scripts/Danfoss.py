# Packages to be imported
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

import unicodedata
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

# c_name = 'Danfoss_Testing' # Name of the Collection
c_name = 'Danfoss' # Name of the Collection

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


def parse_filtered_news(announcement):
    api_url = "https://admin.new.emr-online.com/api/history/filterbody"
    # api_url = "http://192.168.60.105:3000/api/history/filterbody"
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

# ****************************************************************************

####################################################

############# Every Company Logic Here #############

####################################################

# *****************************************************************************

try:
    Base_url = "https://www.danfoss.com"
    result = requests.get("https://www.danfoss.com/sitemap.xml/en/")
    soup = BeautifulSoup(result.content, "html.parser")
    links = soup.find_all('loc')
    final_links = [link.text for link in links if "/news/" in link.text or "/case-stories/" in link.text]
    final_links.remove('https://www.danfoss.com/en/service-and-support/case-stories/')
    final_links.remove('https://www.danfoss.com/en/about-danfoss/news/')
    db_list = []
    mydoc = collection.find()
    for x in mydoc:
        db_list.append(x['News_Weblink'])

    for i in final_links:
        Emr_Crawlers_Logs(c_name,i)
        if i in db_list:
            Already_exist += 1
            total_crwalled_links += 1
            continue 
        elif "/news/" in i:
            result1 = requests.get(i)
            response1 = Selector(result1)
            try:
                news_date = response1.css('.sub-title ::text').get()
                news_date = dateparser.parse(news_date)
            except:
                news_date = ""
            try:
                title = response1.css(".page-heading ::text").get()
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
                announcement = response1.css(".page-content").get()
                replace1 = response1.css(".card-wrapper").getall()
                for tl in replace1:
                    announcement = announcement.replace(tl, "")
                images = response1.css(".page-content picture img::attr(src)").getall()
                img_src_set = response1.css(".page-content picture img::attr(data-src)").getall()
                images1 = response1.css(".page-content picture img").getall()
                final_img_src = []
                for ii, jj, kk in zip(images, img_src_set, images1):
                    a = '<img src="' + ii
                    b = '<img src="https://www.danfoss.com' + jj
                    f_img = kk.replace(a, b)
                    final_img_src.append(f_img)
                for bef_img , after_img in zip(images1, final_img_src):
                    announcement = announcement.replace(bef_img, after_img)
                return_data = parse_filtered_news(announcement)
                announcement = return_data['filteredBody']
                announcement = unicodedata.normalize("NFKD",announcement)
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

            announcement_type = "News"
            language = "en-US"
            page_source = "https://www.danfoss.com/en/about-danfoss/news/?sort=startDate_desc"
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

        elif "/case-stories/" in i:
            result1 = requests.get(i)
            response1 = Selector(result1)
            try:
                news_date = response1.css('.sub-title ::text').get()
                news_date = dateparser.parse(news_date)
            except:
                news_date = ""
            try:
                title = response1.css(".page-heading ::text").get()
            except:
                title = ""
            try:
                analysis = response1.xpath("//meta[@name='description']/@content").get()
            except:
                analysis = ""
            try:
                image =  response1.xpath("//meta[@property='og:image']/@content").get()
            except:
                image = ""
            sub_category = ""
            try:
                announcement = response1.css(".page-content").get()
                replace1 = response1.css(".card-wrapper").getall()
                for tl in replace1:
                    announcement = announcement.replace(tl, "")
                images = response1.css(".page-content picture img::attr(src)").getall()
                img_src_set = response1.css(".page-content picture img::attr(data-src)").getall()
                images1 = response1.css(".page-content picture img").getall()
                final_img_src = []
                for ii, jj, kk in zip(images, img_src_set, images1):
                    a = '<img src="' + ii
                    b = '<img src="https://www.danfoss.com' + jj
                    f_img = kk.replace(a, b)
                    final_img_src.append(f_img)
                for bef_img , after_img in zip(images1, final_img_src):
                    announcement = announcement.replace(bef_img, after_img)
                return_data = parse_filtered_news(announcement)
                announcement = return_data['filteredBody']
                announcement = unicodedata.normalize("NFKD",announcement)
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

            announcement_type = "Case Stories"
            language = "en-US"
            page_source = "https://www.danfoss.com/en/service-and-support/case-stories/?sort=startDate_desc"
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
