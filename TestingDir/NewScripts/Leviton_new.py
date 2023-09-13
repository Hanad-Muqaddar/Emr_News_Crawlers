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
from newspaper import fulltext

from scrapy import Selector

# ************************************************************************
# defining variables

running_Sequence = []

started_on = datetime.now()

c_name = 'LEVITON' # Name of the Collection

total_crwalled_links = 0

Already_exist = 0

# *************************************************************************

# trying to connect with mongodb

try:

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
        new_data =  ""
        return new_data

try:
    proxies = {'http': f"http://waleeProxy:Cheeta@1@de.proxymesh.com:31280",
            'https': f"http://waleeProxy:Cheeta@1@de.proxymesh.com:31280"}
    
    print("Starting a script")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
    Base_url = "https://www.leviton.com/sites/Satellite?pagename=LC/Utilities/GetAllPressReleases&d=Default&id=1469251297323"
    Main_url = "https://www.leviton.com"
    try:
        page = requests.get(Base_url,headers=headers, proxies=proxies)
    except Exception as e:
        print(e)
    json_result = page.json()
    print(json_result)
    
    news_links = []
    news_dates = []

    for data in json_result['pressreleases']:
        date = data['shortdescription']
        news_dates.append(date)

        link = Main_url + data['assoc_link']
        news_links.append(link)


    db_list = []
    mydoc = collection.find()
    for x in mydoc:
        db_list.append(x['News_Weblink'])
    print(news_links)

    All_title_list = []
    mydoc = collection.find()
    for x in mydoc:
        All_title_list.append(x['title'])

    print(news_links)
    print(news_dates)

    for i,d in zip(news_links, news_dates):
        
        if i in db_list:
            total_crwalled_links += 1
            Already_exist += 1
            print("Already Crawled")
            continue

        else:
            response = requests.get(i, headers=headers)
            data = BeautifulSoup(response.content, 'lxml')
            response1 = Selector(response)
            try:
                title = data.find('div', attrs = {"class":"title--a"}).get_text(strip=True)
                print(title)
            except:
                title = data.find('title').text
                print(title)
            
            if title in All_title_list:
                Already_exist += 1
                total_crwalled_links += 1
                print('Title Already Exist')
                continue
            
            else:
            
                announcement_type = "Press Release"
                language = "en-us"
                image = "" 

                try:
                    sub_category = data.find('meta', attrs = {"name":"type"}).get("content")
                except:
                    sub_category = ""
                
                try:
                    analysis = data.find('meta', attrs = {"name":"description"}).get("content")
                except:
                    analysis = ""
                try:
                    news_date = dateparser.parse(d )
                    # print(news_date)
                except:
                    news_date = ""

                page_source = "https://www.leviton.com/en/company/news-events/press-releases"
                news_weblink = i
                
                try:
                    announcement = response1.xpath("//div[@class='ss-rg wrapper text__wrapper align-left__wrapper']").get()
                    replace1 = response1.xpath("//div[@class='ss-rg wrapper text__wrapper align-left__wrapper']//div[@class='title--a']").get()
                    announcement = announcement.replace(replace1, "")
                    announcement = announcement.replace('\n','<br>')
                    return_data = parse_filtered_news(announcement)
                    announcement = return_data['filteredBody']
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
                
                date = datetime.now()
                # Creating a list of links already avilable in database
                
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

# error_logs.insert_one(log)
