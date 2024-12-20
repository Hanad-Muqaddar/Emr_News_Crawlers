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
def parse_filtered_news(announcement):
    api_url = "https://admin.new.emr-online.com/api/history/filterbody"
    # api_url = "http://192.168.60.105:3000/api/history/filterbody"
    payload = json.dumps({"originalBody": announcement})
    headers = {'Content-Type': 'application/json'}
    return_response = requests.request("POST", api_url, headers=headers, data=payload, proxies=proxies)
    new_data = return_response.text
    new_data = json.loads(new_data)
    status = new_data['statusCode']
    if status == 200:
        return new_data
    else:
        new_data =  ""
        return new_data
    
try:
    # proxies = {'http': 'http://waleeProxy:Cheeta@1@uk.proxymesh.com:31280', 'https': 'http://waleeProxy:Cheeta@1@uk.proxymesh.com:31280'}
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'cookie': '__gtm_campaign_url=; OptanonAlertBoxClosed=2024-12-20T10:35:55.450Z; OptanonConsent=isGpcEnabled=0&datestamp=Fri+Dec+20+2024+15%3A35%3A55+GMT%2B0500+(Pakistan+Standard+Time)&version=202410.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=fcb23695-fdaf-43f9-b3dc-e8535cd6f476&interactionCount=3&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&intType=1; TEAL=v:2193e3a3646b33494322956559491536f53306737d0$t:1734692758753$s:1734690956403%3Bexp-sess$sn:1$en:2; _ga=GA1.1.1267902491.1734690961; _gcl_au=1.1.449186749.1734690961; _rdt_uuid=1734690969874.322ef938-da4a-476e-b1e0-5de03037ba98; drift_campaign_refresh=4cb91656-18e6-4839-9180-1022078f2480; _cs_c=0; kampyle_userid=10a9-6998-937f-a8db-ab3d-77a3-3f10-4b30; kampyleUserSession=1734690971089; kampyleUserSessionsCount=1; kampyleSessionPageCounter=1; kampyleUserPercentile=47.01120137018269; kampylePageLoadedTimestamp=1734690971236; _cs_id=e85c3796-d1bc-a354-da47-17ebe5a3cf84.1731669863.3.1734690971.1734689961.1708007454.1765833863488.1; _mkto_trk=id:178-GYD-668&token:_mch-se.com-c74c7dd22a4f865a2d8c696089091637; _ga_MXD394MGXR=GS1.1.1734690960.1.0.1734690972.0.0.0; _cs_s=6.0.1.9.1734692773042; _fbp=fb.1.1734690974053.656297913992928818',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }
    proxies = {}
    db_list = []
    mydoc = collection.find()
    for x in mydoc:
        db_list.append(x['News_Weblink'])

    result = requests.get("https://www.se.com/us/en/about-us/newsroom/news/", proxies=proxies)
    res = Selector(result)

    # data = res.css(".sdl-wiztopic-press-releases_wiztopic-card .wiztopic-content")
    News_Links = res.xpath('//div[@id="se2--wiztopic-event-list-cards-container---"]/div[contains(@class,"se2--wiztopic-event-list--wiztopic-card")]//div[@class="slide-content"]/a[@class="extra-link-wrapper"]/@href').getall()
    f_News_Links = [ "https://www.se.com" + l for l in News_Links]
    print(f_News_Links)

    Web_Page = "https://www.se.com/us/en/about-us/newsroom/news/"
    Emr_Crawlers_Logs(c_name+"_Second",Web_Page,f_News_Links)
    for news_weblink in f_News_Links:
        
        if news_weblink in db_list:
            total_crwalled_links += 1
            Already_exist += 1
            print("Already Crawled")
            continue
        else:
            result2 = requests.get(news_weblink)
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
                print(title)
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
                announcement = ''.join(response1.xpath('//div[@class="description se-rich-text se2-text-small"]//text()').getall())
                announcement = announcement.replace("\n", "<br/>").replace("  ", " ")
                # return_data = parse_filtered_news(announcement)
                # announcement = return_data['filteredBody']
                # announcement = unicodedata.normalize("NFKD",announcement)
                # emr_essentail = return_data['emrEssential']
                # emr_executive = return_data['emrExecutive']
                # emr_lite = return_data['emrLite']
                # emr_html = return_data['emrHtmlText']

            except Exception as e:
                announcement = ""
                # emr_essentail = ""
                # emr_executive = ""
                # emr_lite = ""
                # emr_html = ""
                
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
            # company_news['emrExecutive'] = emr_executive
            # company_news['emrEssential'] = emr_essentail
            # company_news['emrLite'] = emr_lite
            # company_news['News_Html'] = emr_html
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
    print(e)
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
