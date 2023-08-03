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
from googletrans import Translator

# ************************************************************************
# defining variables

running_Sequence = []

started_on = datetime.now()

c_name = 'Deha_Group' # Name of the Collection

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
try:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
    Main_url = "https://www.deha.de"
    Base_url = "https://www.deha.de/newsroom"
    result = requests.get(Base_url,headers=headers)
    soup = BeautifulSoup(result.content , 'lxml')


    def translate(Trans):
        translator = Translator()
        Trans_text = translator.translate(Trans,dest='en')
        return Trans_text.text
    
    news_links = []

    links = soup.find_all('div',{ "class" : "deha-news-list-item"}) 
    for link in links:
        news_link = Main_url + link.find('a',{ "class" : "deha-news-title"}).get('href')
        if news_link not in news_links:
            news_links.append(news_link)

    print(news_links)
    print(len(news_links))

     # Creating a list of links already avilable in database
    links_list = []
    mydoc = collection.find()
    for x in mydoc:
        links_list.append(x['News_Weblink'])

    for i in news_links:   
        if i in links_list:
            total_crwalled_links += 1
            Already_exist += 1
            print("Already Crawled")
            continue
        else:     
            response = requests.get(i, headers=headers)
            data = BeautifulSoup(response.content, 'lxml')

            try:
                title = data.find('title').text
                title = title.replace('– DEHA Gruppe','').strip()
                title = translate(title)
                print(title)
            except:
                title =""
                print(title)
            
            announcement_type = "News"

            language = "en-us"

            try:
                try:
                    image = Main_url + data.find('div', attrs = {"class":"deha-pic-container"}).get("style").split('url(')[1][:-1]
                except:
                    image = Main_url + data.find('figure', attrs = {"class":"deha-image"}).find('img', attrs = {"class":"img-fluid"}).get("src")
            except:
                image = ""
                print(image)

            try:
                sub_category = data.find('meta', attrs = {"name":"type"}).get("content")
                sub_category = translate(sub_category)
            except:
                sub_category = ""
            
            try:
                analysis = data.find('meta', attrs = {"name":"description"}).get("content")
                analysis = translate(analysis)
            except:
                analysis = ""
            try:
                date = data.find('div', attrs = {"class":"deha-news-detail-date"}).get_text().split('–')[1].strip()
                news_date = dateparser.parse(date,  settings={'DATE_ORDER': 'YMD'} )
                print(news_date)
            except:
                news_date = ""

            page_source = "https://www.deha.de/newsroom"
            news_weblink = i
            
            try:
                html = requests.get(i).text
                announcement = fulltext(html)
                announcement = announcement.replace('\n','<br>')
                announcement = translate(announcement)
                print(announcement)
                
            except:
                announcement = ""
            
            date = datetime.now()
       
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

error_logs.insert_one(log)
