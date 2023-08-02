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

# from datetime import datetime
import datetime

from bson.objectid import ObjectId

from urllib.error import HTTPError

from urllib.request import Request, urlopen

from scrapy import Selector

from newspaper import Article

import feedparser

import unicodedata
# ************************************************************************

running_Sequence = []

started_on = datetime.datetime.now()

c_name = 'EATON' # Name of the Collection

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
        new_data = ""
        return new_data

count_break = 0

try:
    proxies_list = ['us-wa','fr','jp','au','de']
    import random
    p = random.choice(proxies_list)
    proxies = {'http': f"http://waleeProxy:Cheeta@1@de.proxymesh.com:31280",
            'https': f"http://waleeProxy:Cheeta@1@de.proxymesh.com:31280"}
    headers = {"Connection": "keep-alive",
                "sec-ch-ua":  'Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
                "sec-ch-ua-mobile": "?0",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36",
                "sec-ch-ua-platform": "Windows",
                "Accept": "*/*",
                "Origin": "https://www.eaton.com",
                "Sec-Fetch-Site": "cross-site",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://www.eaton.com/",
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9'
                }
    result = requests.get("https://www.eaton.com/us/en-us/company/news-insights/news-releases.html", headers=headers, proxies=proxies, timeout=20)
    # result = requests.get("https://www.eaton.com/us/en-us/company/news-insights/news-releases.html", headers=headers, timeout=20)
    # print(result)
    response = Selector(result)
    # print(response)
    data = response.css(".results-list-submodule .results-list-submodule__name-link ::attr(href)").getall()
    print(data)

    db_list = []
    mydoc = collection.find()
    for x in mydoc:
        db_list.append(x['News_Weblink'])

    for i in data:
        try:
            news_weblink = i
        except:
            news_weblink = ""
        if news_weblink == "":
            continue
            
        
        if news_weblink in db_list:
            # print("Link Already exists")
            total_crwalled_links += 1
            Already_exist += 1
            print("Already Crawled")
            continue
        else:
            # news, image = parse_newspaper_data(news_weblink)
            # print("Comes here at first point")
            result1 = requests.get(news_weblink , headers=headers, proxies=proxies,)
            result1.encoding = 'utf-8'
            response1 = Selector(result1)
            # print("reach to point 2")

            try:
                image =  response1.xpath("//meta[@property='og:image']/@content").get()
            except:
                image = ""
            try:
                analysis = response1.xpath("//meta[@name='description']/@content").get()
            except:
                analysis = ""
            try:
                title = response1.css(".eaton-title__headline ::text").get()
                if title == None:
                    title = response1.css(".b-heading-h1 ::text").get()
            except:
                title = ""
            try:
                news_date = dateparser.parse(response1.xpath("//meta[@name='publish-date']/@content").get())
            except:
                news_date = ""
            try:
                sub_category = "Press Release"
            except:
                sub_category = ""
            try:
                announcement_type = response1.xpath("//meta[@name='content-type']/@content").get()
            except:
                announcement_type = ""
            try:
                announcement = response1.xpath("//div[@class='responsivegrid aem-GridColumn aem-GridColumn--default--12']").get()
                try:
                    announcement = announcement.replace("\n", "").replace("\r", "").replace("\t", "")
                except:
                    pass
                try:
                    to_replace = response1.xpath("//div[@class='title aem-GridColumn aem-GridColumn--default--12']").get()
                except:
                    pass
                try:
                    to_replace = to_replace.replace("\n", "").replace("\r", "").replace("\t", "")
                except:
                    pass
                try:
                    to_replace2 = response1.css(".social-share").get()
                except:
                    pass
                try:
                    to_replace2 = to_replace2.replace("\n", "").replace("\r", "").replace("\t", "")
                except:
                    pass
                try:
                    to_replace_3 = response1.css(".eaton-text-default__content div").get()
                except:
                    pass
                try:
                    announcement = announcement.replace(to_replace, "")
                except:
                    pass
                try:
                    announcement = announcement.replace(to_replace2, "")
                except:
                    pass
                try:
                    announcement = announcement.replace(to_replace_3, "")
                except:
                    pass
                try:
                    announcement = announcement.replace('data-src="', 'src="https://www.eaton.com')
                except:
                    pass
                try:
                    ret_obj = parse_filtered_news(announcement)
                except Exception as e:
                    print(e)

                announcement = ret_obj['filteredBody']
                try:
                    emr_essentail = ret_obj['emrEssential']
                except:
                    emr_essentail = ""
                try:
                    emr_executive = ret_obj['emrExecutive']
                except:
                    emr_executive = ""
                try:
                    erm_lite = ret_obj['emrLite']
                except:
                    erm_lite = ""
                announcement = unicodedata.normalize("NFKD",announcement)
                emr_html = ret_obj['emrHtmlText']
            except:
                announcement = ""
                emr_essentail = ""
                erm_lite = ""
                emr_executive = ""
                emr_html = ""


            language = "en"
            page_source = "https://www.eaton.com/us/en-us/company/news-insights/news-releases.html"
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
            company_news['News_Weblink'] = news_weblink
            company_news['photo']= image
            company_news['videos']= ''
            company_news['unique_news'] = True
            company_news['announcement']=announcement
            company_news['historySubCategory']= sub_category
            company_news['analysis'] = analysis
            company_news['emrExecutive'] = emr_executive
            company_news['emrEssential'] = emr_essentail
            company_news['emrLite'] = erm_lite
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

error_logs.insert_one(log)
