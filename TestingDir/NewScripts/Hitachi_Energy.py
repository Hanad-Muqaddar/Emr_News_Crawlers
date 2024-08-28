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
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
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
# # ================================================================================

# ************************************************************************
running_Sequence = []

started_on = datetime.datetime.now()

c_name = 'HITACHI_ABB' # Name of the Collection

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
def parse_news_date(response):
    try:
        news_date = response.xpath("//meta[@itemprop='date']/@content").get()
        news_date = str(news_date)
        news_date = dateparser.parse(news_date)
    except:
        news_date = datetime.now()
    return news_date

def parse_filtered_news(announcement):
        api_url = "https://admin.new.emr-online.com/api/history/filterbody"
        payload = json.dumps({"originalBody": announcement})
        headers = {'Content-Type': 'application/json'}
        return_response = requests.request("POST", api_url, headers=headers, data=payload)
        new_data = return_response.text
        new_data = json.loads(new_data)
        status = new_data['statusCode']
        if status == 200:
            return new_data
        else:
            new_data =  ""
            return new_data
        
def parse_announcement(response):
        announcement = response.css(".aem-Grid--default--12").get()
        to_replace = response.css(".cmp-pagestage-text-only__heading-container").get()
        to_replace_1 = response.xpath("//div[@data-dm='breadcrumb.component']").get()
        to_replace2 = response.css(".cmp-pagestage-text-only__social-container").get()
        # to_replace_3 = response.css(".cmp-title__text").get()
        try:
            announcement = announcement.replace(to_replace, "")
        except:
            pass
        try:
            announcement = announcement.replace(to_replace_1, "")
        except:
            pass
        try:
            announcement = announcement.replace(to_replace2, "")
        except:
            pass
        return_data = parse_filtered_news(announcement)
        try:
            announcement = return_data['filteredBody']
        except:
            announcement = ""
        announcement = unicodedata.normalize("NFKD",announcement)
        try:
            emr_essentail = return_data['emrEssential']
        except:
            emr_essentail = ""
        try:
            emr_executive = return_data['emrExecutive']
        except:
            emr_executive = ""
        try:
            emr_lite = return_data['emrLite']
        except:
            emr_lite = ""
        try:
            emr_html = return_data['emrHtmlText']
        except:
            emr_html = ""
        return announcement , emr_essentail, emr_lite, emr_executive, emr_html

try:
    # proxies_list = ['us-wa','fr','jp','au','de']
    # import random
    # p = random.choice(proxies_list)
    # proxies = {'http': f"http://waleeProxy:Cheeta@1@{p}.proxymesh.com:31280",
    #         'https': f"http://waleeProxy:Cheeta@1@{p}.proxymesh.com:31280"}

     # defining variables
    opts = Options()
    # opts.add_argument("--window-size=190,100")
    # opts.add_argument("--disable-automation")
    opts.add_argument("--no-sandbox")
    opts.add_argument('--profile-directory=Default')
    opts.add_argument("start-maximized")
    opts.add_argument("disable-infobars")
    opts.add_argument("--lang=en")
    opts.add_argument("--enable-javascript")
    opts.add_argument("--enable-cookies")
    opts.add_argument("--headless")
    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9',
    'If-Modified-Since': 'Thu, 13 Jun 2024 04:41:47 GMT',
    'Origin': 'https://www.hitachienergy.com',
    'Priority': 'u=1, i',
    'Sec-Ch-Ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site'
}


    driver = webdriver.Chrome(options=opts)
     
    Main_url = "https://www.hitachienergy.com"
    page_source = "https://www.hitachienergy.com/news"
 
    driver.get(page_source)
    time.sleep(10)
    
    news_links = []
    links = driver.find_elements(By.XPATH, '//ul[contains(@class,"cmp-newslist__news-list")]/li[@class="cmp-newslist__news-item"]')
    for link in links:
        news_link = link.find_element(By.XPATH, './a[@class="cmp-newslist__news-item-link"]').get_attribute('href')
        news_links.append(news_link)
    
    driver.quit()
    
    print(news_links)
    print(len(news_links))

    db_list = []
    mydoc = collection.find()
    for x in mydoc:
        db_list.append(x['News_Weblink'])

    All_title_list = []
    mydoc = collection.find()
    for x in mydoc:
        All_title_list.append(x['title'])

    Emr_Crawlers_Logs(c_name,page_source,news_links)
    
    for i in news_links:
        if i in db_list:
            Already_exist += 1
            total_crwalled_links += 1
            print('Already Crawled')
            continue
        else:
            print("A gaya")
            result1 = requests.get(i, headers=headers)
            response1 = Selector(result1)

            title = response1.css("title ::text").get()
            print(title)
            if title in All_title_list:
                Already_exist += 1
                total_crwalled_links += 1
                print('Title Already Exist')
                continue
            
            else:
                try:
                    n_date = response1.xpath('//article[contains(@class,"webstorypage newspage-v2 page-v2 page")]//span[@class="cmp-newsinfo__item"][3]/text()').get()
                    news_date = dateparser.parse(n_date,  settings={'DATE_ORDER': 'DMY'})
                except:
                    news_date = datetime.datetime.now()
                
                try:
                    analysis = response1.xpath('//meta[@name="description"]/@content').get()
                except:
                    analysis = ""
                try:
                    image = response1.css(".cmp-container--full-width picture img::attr(href)").get()
                except:
                    image = ""
                sub_category = ""
                try:
                    announcement , emr_essentail, emr_lite, emr_executive, emr_html = parse_announcement(response1)
                except:
                    announcement = ""
                    emr_essentail = ""
                    emr_lite = ""
                    emr_executive = ""
                    emr_html = ""
                    
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
                # company_news['analysis'] = analysis
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

error_logs.insert_one(log)
