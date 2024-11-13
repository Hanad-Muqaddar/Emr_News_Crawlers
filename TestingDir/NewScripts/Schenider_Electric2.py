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
        'cookie': 'visitorOriginStatus=external; AWSALB=ee0d8sdIANgWz3qfUQpXLwlpjSLG0fvIFKWTZevqXEhJFJ/vRVq9T81vSsUfdhuBtUEYcSjcGK/DJ57uf7flp5A3ND9hn6BU/HDBGVj1I44QGtSpRJB5E0oPUxLd; AWSALBCORS=ee0d8sdIANgWz3qfUQpXLwlpjSLG0fvIFKWTZevqXEhJFJ/vRVq9T81vSsUfdhuBtUEYcSjcGK/DJ57uf7flp5A3ND9hn6BU/HDBGVj1I44QGtSpRJB5E0oPUxLd; _gcl_au=1.1.1700038501.1721053979; OptanonAlertBoxClosed=2024-07-15T14:33:00.312Z; _fbp=fb.1.1721053980428.915424709765820502; visitorOriginStatus=external; _ga=GA1.1.1081535430.1721053982; _mkto_trk=id:178-GYD-668&token:_mch-www.se.com-1721053982357-87505; _evga_c320={%22uuid%22:%2281d216181558237d%22}; _sfid_10cb={%22anonymousId%22:%2281d216181558237d%22%2C%22consents%22:[]}; _cs_c=0; mdLogger=false; kampyle_userid=c940-4397-b899-2fb9-7816-14b5-84ea-5c05; AKA_A2=A; __gtm_campaign_url=; ak_bmsc=964DB2658AE7256D2F99B0CF9D822E78~000000000000000000000000000000~YAAQVJ42FyTrMWiSAQAANgJKdhmni4WfmPm1TMUNo3tw6FJG2+LRDwpGoVzl8TZVKprmTmQplP5HY9IX0x9GJc25BwuR3AC6EAqR4HbK0pSamcs8wzJauOAJ/hdmUGMF2s46wZvEVIVufHYUDWYBzsn1mFXZ8DhYi1Hwe6NJAUZHHAgg2DZsAmEGx63Y0C5aWVBxSvJ2rnT6hX1xNADX35nyFQkGmgYW47NjYFGIHlDSQ7SO7a4ObmSf167dvVZTWGeWY+HIUCl3E+CjX3oJe4JTETsgUPFUawveHzkizaUR53yaZrjC+sX/RDv6SyJH+JquixZjiNVkekkvn3DEKVXuu1YNC/coks6UBepsIfrfSsPK+J2c/7KsUIVy4lwU/KUNYRqJ8L1Kv4lcrhEsF/8XeSrg+j8BRtWcQ+RLfGnqJMuOY+crNC+wrfyg1scCuZbCyMxICDkjXiSf; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Oct+10+2024+16%3A56%3A55+GMT%2B0500+(Pakistan+Standard+Time)&version=202407.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=bc4a5bae-01b5-4181-b245-1946a9c7afef&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&intType=3&geolocation=PK%3BPB&AwaitingReconsent=false; TEAL=v:1190b6cfacb882145216592064068536f2878677960$t:1728563216193$sn:2$en:1$s:1728561416192%3Bexp-sess; _cs_cvars=%7B%7D; _cs_id=9b105d11-cd03-a0e6-9425-da34198c6078.1721053983.2.1728561416.1728561416.1708007454.1755217983326.1; _mkto_trk=id:178-GYD-668&token:_mch-www.se.com-1721053982357-87505; _cs_s=1.0.1.1728563217520; bm_sv=869F16D7F0FA4D18CDB4851998F68813~YAAQVJ42FyLtMWiSAQAA+hZKdhl+Vnt+G1kMKTBLkkJPKFQ0y1zPWs6AY9cNalMZhz5IwcEnF2gMxSPAyjEWWE/OiHDYyFOYu5UC8eHqSV99fiwSb7Ko2V49cbd6aa/DqPBmYxqoJfjX7hxGNxHaPs5EN6NbSs4yTb9dpQrLlIekm6U1sNSXvO9PG1DmP4Lpwkw8vcSGBAPCvfNxLpiU7GIZbsaLEot9Qzly55KDj7dGF8uL/0Q7IWEVE29qWWvL~1; _ga_MXD394MGXR=GS1.1.1728561416.2.0.1728561420.0.0.0; kampyleUserSession=1728561420353; kampyleUserSessionsCount=2; kampyleSessionPageCounter=1; kampyleUserPercentile=79.78088371373941; kampylePageLoadedTimestamp=1728561420376',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    }
    proxies = {}
    db_list = []
    mydoc = collection.find()
    for x in mydoc:
        db_list.append(x['News_Weblink'])

    result = requests.get("https://www.se.com/us/en/about-us/newsroom/news/", headers=headers, proxies=proxies)
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
