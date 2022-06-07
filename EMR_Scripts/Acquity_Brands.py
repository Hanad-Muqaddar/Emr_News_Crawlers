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

# ************************************************************************
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
lang_dict = {'nl': 'en', 'fr': 'en', 'cs': 'en', 'da': 'en', 'de': 'en', 'es': 'en', 'it': 'en', 'hu': 'en', 'no': 'en', 'pl': 'en', 'pt': 'en', 'ro': 'en', 'sk': 'en', 'fi': 'en', 'sv': 'en', 'tr': 'en', 'el': 'en', 'bg': 'en', 'ru': 'en', 'uk': 'en', 'ar': 'en', 'id': 'en', 'vi': 'en', 'th': 'en', 'zh': 'en', 'ja': 'en', 'ko': 'en'}
prefs = {
  "translate_whitelists": lang_dict,
  "translate":{"enabled":"true"}
}
opts.add_experimental_option("prefs", prefs)
opts.headless = True
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
try:

    driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver',options=opts)  # path to the driver is here
    url = "https://insights.acuitybrands.com/news-releases"
    driver.implicitly_wait(30)
    try:
        SCROLL_PAUSE_TIME = 20
        driver.get(url)
        last_height = driver.execute_script("return document.body.scrollHeight")    
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            
        news_links = driver.find_elements_by_xpath("//section[@class='level-two']/div//ul/li/a[@class='item-link view hooked']")
    except Exception as e:
        running_Sequence.append(e)

    links = []
    for i in news_links:
        links.append(i.get_attribute('href'))
    driver.close()

    for i in links:
        result = requests.get(i)
        soup = BeautifulSoup(result.content, 'lxml')
        try:
            title = soup.find("title").text.strip()
        except:
            title = ""
        try:
            analysis = soup.find("meta", attrs={"name":"description"}).get("content").strip()
        except:
            analysis = ""
        page_source = "https://insights.acuitybrands.com/"
        try:
            d = soup.find("meta", attrs={"itemprop":"datePublished"}).get("content").strip()
            news_date = dateparser.parse(d, settings={'DATE_ORDER': 'YMD'})
        except:
            news_date = ""
        try:
            announcement = soup.find("div", id='item-content').find("section", class_='level-three').text
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
        news_weblink = i
        date = datetime.now()
        language = "en-US"
        announcement_type = "News Releases"
        
        links_list = []
        mydoc = collection.find()
        for x in mydoc:
            links_list.append(x['News_Weblink'])
        if news_weblink in links_list:
            total_crwalled_links += 1
            Already_exist += 1
            continue
        else:
            company_news = {}
            company_news['companyId'] = ''
            company_news['location']=''
            company_news['comment']=''
            company_news['Date']= news_date
            company_news['Crawled_on']=date
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

except Exception as e:

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

log['Browser'] = 'Chrome'

error_logs.insert_one(log)




