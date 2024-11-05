import requests
import time
import json
import traceback
from random import randint
from bs4 import BeautifulSoup
from pymongo import MongoClient
from bs4 import BeautifulSoup
from selenium import webdriver
from scrapy import Selector
# from webdriver_manager.chrome import ChromeDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
import re
import pandas as pd
import os
import csv
import urllib
import time
import dateparser
from datetime import datetime,date, timedelta
from bson.objectid import ObjectId
from urllib.error import HTTPError
from urllib.request import Request, urlopen
# from Emr_Crawlers_Optimization import Emr_Crawlers_Logs

# ================================================================================
# # Comment these lines when you are running locally
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
started_on = datetime.now()
c_name = 'FEGIME'

try:
    client = MongoClient('mongodb://su-du-ad:updatedSuperDuperAdmin@18.156.208.71:27017/emrweb?authSource=admin') # Staging DB 
    running_Sequence.append('Connected to DB Server')
except:
    running_Sequence.append('Not Connected')

client_name = 'TEMP_EMR_NEWS_Crawler_DB'
news =  client[client_name]
collection = news[c_name]
error_logs = client['Logs_DB']['Logs_TEMP_EMR_NEWS_Crawler_DB']
last_insertion = None
last_time = ''

try:
    for l_i in collection.find().sort('Date', -1).limit(1):
        last_insertion = l_i
except:
    print('Fresh Starting News Crawler')
    last_insertion = None

if last_insertion == None:
    running_Sequence.append('Fresh Starting News Crawler on -> ' + str(datetime.now()))
    Crwl_time = datetime.now()
else:
    last_time = last_insertion['Date']
    running_Sequence.append('Last News Crawled on -> '+str(last_insertion['Date'].date()))
    Crwl_time = last_insertion['Date']
    
total_crwalled_links = 0
Already_exist = 0

try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    }
    Optimization_links = []
    urls = ['https://www.fegime.com/news/page/1']
    # urls = ['https://www.fegime.com/news/page/1','https://www.fegime.com/news/page/2','https://www.fegime.com/news/page/3']

    for url in urls:
        main_resp = requests.get(url, headers=headers)
        response = Selector(text=main_resp.text)
        for i in response.xpath('//section[contains(@class,"container section-content")]//article'):
            website = i.xpath('.//link/@href').get()
            print(website)
            
            l = False
            for k in collection.find({ 'News_Weblink' : website }):
                if k:
                    l = True
                    break
            
            Optimization_links.append(l)
            if l:
                total_crwalled_links +=1
                Already_exist +=1
                print('\n' + str(news['Link']) + '\nNews Already Exist in DB\n')        
            else:
                date_element = i.xpath('.//time[@class="date"]/a/span[2]')
                date_text = date_element.xpath('normalize-space(.)').get()
                photo = i.xpath('.//figure//img/@src').get()
                title = i.xpath('normalize-space(.//figcaption)').get()
                analysis = i.xpath('normalize-space(.//div[contains(@class, "card-text")])').get()
                ann = ['']
                resp = requests.get(website, headers=headers)
                sub_soup = BeautifulSoup(resp.content, 'lxml').find('div', attrs={'class': 'article-body wysiwyg-content clearfix mb-2', 'itemprop': 'articleBody'}).find_all('p')
                for ps in sub_soup:
                    ann.append(ps.text.strip())
                announcement = '\n'.join(ann)

                news = {}
                news['Date'] = dateparser.parse(date_text)
                news['Crawled_on'] = datetime.now()
                news['announcementType'] = 'NEWS'
                news['Source'] = url
                news['News_Weblink'] = website
                news['title'] = title
                news['announcement'] = announcement
                news['Language'] = 'English'
                news['analysis'] = analysis
                news['photo'] = photo
                news['historySubCategory'] = ""
                total_crwalled_links += 1
                collection.insert_one(news)
                
        if Already_exist >=1:
            tmp_txt = ' , from which '+str(Already_exist) +' Links were Already Crawled '
        else:
            tmp_txt = ''

        running_Sequence.append(str(total_crwalled_links) + ' Links are crawled ' + tmp_txt)
        ended_on = datetime.now()

    Web_Page = "https://www.fegime.com/news/page/1"        
    Emr_Crawlers_Logs(c_name, Web_Page, Optimization_links)
    
except Exception as e:
    Error_Time =  datetime.now()
    Reported_Error = traceback.format_exc()
    print(Reported_Error)
    
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