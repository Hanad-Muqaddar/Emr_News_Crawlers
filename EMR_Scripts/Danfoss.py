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

c_name = 'Danfoss' # Name of the Collection

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
# Writing driver path
try:
    driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver',options=opts)
    print("1st step")
    links = ["https://www.danfoss.com/en/about-danfoss/news/?sort=startDate_desc", "https://www.danfoss.com/en/service-and-support/case-stories/?sort=startDate_desc"]
    for i in links:
        driver.get(i)
        page_source = i
        time.sleep(5)
        try:
            accept_button = driver.find_element_by_xpath("//div[@class='coi-button-group']/button[@class='coi-banner__accept']")
            accept_button.click()
        except:
            pass
        print("First Step")
        links = driver.find_elements_by_xpath("//div[@class='col-md-9 list__wrapper']//li[@class='tile  clearfix  ']/a")
        news_weblinks = []
        try:
            for j in links:
                news_weblinks.append(j.get_attribute("href"))
        except Exception as e:
            print(e)
        print(news_weblinks)
        links_list = []
        mydoc = collection.find()
        for x in mydoc:
            links_list.append(x['News_Weblink'])

        for z in news_weblinks:
            if z in links_list:
                total_crwalled_links += 1
                Already_exist += 1
                continue
            else:
                result = requests.get(z)
                soup = BeautifulSoup(result.content, 'lxml')
                try:
                    title = soup.find("meta", attrs={"property":"og:title"}).get("content")
                except:
                    title = ""
                news_weblink = z
                try:
                    analysis = soup.find("meta", attrs={"property":"og:description"}).get("content")
                except:
                    analysis = ""
                try:
                    sub_category = soup.find('meta', attrs = {"property":"og:type"}).get("content")
                except:
                    sub_category = ""
                try:
                    image = soup.find("meta", attrs={"property":"og:image"}).get("content")
                except:
                    image = ""
                try:
                    d = soup.find("div", class_='sub-title').text.strip()
                    news_date = dateparser.parse(d)
                except:
                    news_date = ""
                try:
                    announcement = soup.find("div", attrs = {"role":"main"}).text.strip()
                except:
                    announcement = ""
                try:
                    announcement_type = soup.find("div", class_='breadcrumbs-container').find_all("li")[2].text.strip()
                except:
                    announcement_type = ""
                language = "en-US"
                crawled_date = datetime.now()
                break_condition = 0
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
        try:
            while True:
                button = driver.find_element_by_xpath("//li[@class='next']")
                button.click()
                time.sleep(5)
                links = driver.find_elements_by_xpath("//div[@class='col-md-9 list__wrapper']//li[@class='tile  clearfix  ']/a")
                news_weblinks = []
                for j in links:
                    news_weblinks.append(j.get_attribute("href"))
                links_list = []
                mydoc = collection.find()
                for x in mydoc:
                    links_list.append(x['News_Weblink'])

                for z in news_weblinks:
                    if z in links_list:
                        total_crwalled_links += 1
                        Already_exist += 1
                        continue
                    else:
                        result = requests.get(z)
                        soup = BeautifulSoup(result.content, 'lxml')
                        try:
                            title = soup.find("meta", attrs={"property":"og:title"}).get("content")
                        except:
                            title = ""
                        news_weblink = z
                        try:
                            analysis = soup.find("meta", attrs={"property":"og:description"}).get("content")
                        except:
                            analysis = ""
                        try:
                            sub_category = soup.find('meta', attrs = {"property":"og:type"}).get("content")
                        except:
                            sub_category = ""
                        try:
                            image = soup.find("meta", attrs={"property":"og:image"}).get("content")
                        except:
                            image = ""
                        try:
                            d = soup.find("div", class_='sub-title').text.strip()
                            news_date = dateparser.parse(d)
                        except:
                            news_date = ""
                        try:
                            announcement = soup.find("div", attrs = {"role":"main"}).text.strip()
                        except:
                            announcement = ""
                        try:
                            announcement_type = soup.find("div", class_='breadcrumbs-container').find_all("li")[2].text.strip()
                        except:
                            announcement_type = ""
                        language = "en-US"
                        crawled_date = datetime.now()
                        break_condition = 0
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

log['Browser'] = 'Chrome'

error_logs.insert_one(log)

