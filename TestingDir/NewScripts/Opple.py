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
# opts = Options()
# opts.add_argument("--window-size=190,100")
# opts.add_argument("--disable-automation")
# opts.add_argument("--no-sandbox")
# opts.add_argument('--profile-directory=Default')
# opts.add_argument("start-maximized")
# opts.add_argument("disable-infobars")
# opts.add_argument("--lang=en")
# opts.add_argument("--enable-javascript")
# opts.add_argument("--enable-cookies")
# lang_dict = {'nl': 'en', 'fr': 'en', 'cs': 'en', 'da': 'en', 'de': 'en', 'es': 'en', 'it': 'en', 'hu': 'en', 'no': 'en', 'pl': 'en', 'pt': 'en', 'ro': 'en', 'sk': 'en', 'fi': 'en', 'sv': 'en', 'tr': 'en', 'el': 'en', 'bg': 'en', 'ru': 'en', 'uk': 'en', 'ar': 'en', 'id': 'en', 'vi': 'en', 'th': 'en', 'zh': 'en', 'ja': 'en', 'ko': 'en'}
# prefs = {
#   "translate_whitelists": lang_dict,
#   "translate":{"enabled":"true"}
# }
# opts.add_experimental_option("prefs", prefs)
# opts.headless = True

running_Sequence = []

started_on = datetime.datetime.now()

c_name = 'OPPLE' # Name of the Collection

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
headers = {"authority": "px.ads.linkedin.com",
"method": "GET",
"path": "/collect?v=2&fmt=js&pid=378011&time=1623762746618&url=https%3A%2F%2Fwww.opple.com%2Fen%2Fnews",
"scheme": "https",
"accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
"accept-encoding": "gzip, deflate, br",
"accept-language": "en-US,en;q=0.9",
"cookie": 'li_sugr=e0e6aa9f-664b-4466-a12f-589639c94a36; bcookie="v=2&0138023d-5814-407e-8330-78cd91c34b5d"; _guid=17992010-ca99-4fdc-a4b9-026cef964492; lang=v=2&lang=en-us; lidc="b=VGST07:s=V:r=V:a=V:p=V:g=2106:u=1:i=1623735634:t=1623822034:v=2:sig=AQFb64dRLjieoi8fcxzFMXM85KFMOPz3"; UserMatchHistory=AQIwy8mBidk8lgAAAXoObnxEmWf_y2EYTH38yB4P4DVryOjNBsNkacy978s0ZnT_inMVv1w6STKvldmgFEcNO8Lf35oodwcBG6vp_HTRkOV9g5xmXCgSOXcUI6k_HgeqwgO_EQebn1ipqod5QNO_O0g8QtoN0GTD4GjdXdofykkW8rq-byYEGMN0Wd5MK0Fl5k0WEky4kcAaBlyt-HoOWHe36bArk9e_q2y1UrOOaj9adQtp083Wr1mFsLVYjY6d23x0aMMloNib7ybp8daHRomJvbg-Oc25H-dmRIg; AnalyticsSyncHistory=AQLuPogGmS6IrgAAAXoObnxEbu5KYNYdDUnJKgLlv4OOckDqCGvLo6-KtV-nJNA6kBcPE6B4ug3FR52tDzeLkg',
"referer": "https://www.opple.com/",
"sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
"sec-ch-ua-mobile": "?0",
"sec-fetch-mode": "no-cors",
"sec-fetch-site": "cross-site",
"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"}

db_list = []
mydoc = collection.find()
for x in mydoc:
    db_list.append(x['News_Weblink'])
Optimization_links = []
page_source = 'https://www.opple.com/en/news'
try:
    for i in range(17):
        main_url = "https://www.opple.com/en/news?page={}".format(i)
        result = requests.get(main_url, headers=headers)
        soup = BeautifulSoup(result.content, 'html.parser')
        try:
            links = soup.find("tbody").find_all("td")
        except:
            break
        for j in links:
            news_weblink = "https://www.opple.com" + j.find("a").get('href')
            Optimization_links.append(news_weblink)
            if news_weblink in db_list:
                total_crwalled_links += 1
                Already_exist += 1
                print("Already Crawled")
                continue
            else:
                response = requests.get(news_weblink, headers=headers)
                soup2 = BeautifulSoup(response.content, 'html.parser')
                try:
                    analysis = soup2.find("meta", attrs={"name":"description"}).get("content")
                except:
                    analysis = ""
                try:
                    title = soup2.find("title").text
                except:
                    title = ""
                try:
                    news_date = soup2.find("span", class_='created').text
                    news_date = dateparser.parse(news_date)
                except:
                    news_date = ""
                try:
                    announcment = soup2.find("div", id='content').text
                except:
                    announcment = ""
                try:
                    image = soup2.find("div", id='content').find("img").get("src")
                except:
                    image = ""
                sub_category = ""
                announcement_type = 'News'
                
                language = 'en-US'
                crawled_on_date = datetime.datetime.now()
                company_news = {}
                company_news['companyId'] = ''
                company_news['location']=''
                company_news['comment']=''
                company_news['Date']= news_date
                company_news['Crawled_on']=crawled_on_date
                company_news['title']=title
                company_news['Language']= language
                company_news['announcementType']= announcement_type
                company_news['Source'] = page_source
                company_news['News_Weblink'] = news_weblink
                company_news['photo']= image
                company_news['videos']= ''
                company_news['announcement']=announcment
                company_news['historySubCategory']= sub_category
                company_news['analysis'] = analysis
                try:
                    collection.insert_one(company_news)
                    total_crwalled_links += 1
                except Exception as e:
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

error_logs.insert_one(log)

