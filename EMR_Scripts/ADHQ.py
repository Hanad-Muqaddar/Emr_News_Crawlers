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
running_Sequence = []
started_on = datetime.now()
c_name = 'ADHQ'
try:
    file = open("/home/emr/config.json")
    data = json.load(file)
    db_path = data[0]['Db_Path']
    client = MongoClient(db_path)
    # client= MongoClient('mongodb://su-du-ad:updatedSuperDuperAdmin@18.156.208.71:27017/emrweb?authSource=admin')
    # client= MongoClient('mongodb://su-du-ad:updatedSuperDuperAdmin@18.156.208.71:27017/emrweb?authSource=admin')
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
    # print('Fresh Starting News Crawler')
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
    total_page = json.loads(requests.get('https://www.adhq.com/news/json/').text)['total_pages']
    for i in range(total_page):
        req_url = 'https://www.adhq.com/news/json/'+str(i+1)
        data = json.loads(requests.get(req_url).text)['articles']
        running_Sequence.append('Crawling News Data for ADHQ, count - ' +str(i+1))
        for j in data:
            l = False
            for k in collection.find({ 'News_Weblink' : str('https://www.adhq.com/about/ad-news/'+j['url_segment']) }):
                if k:
                    l = True
                    break
            if l:
                total_crwalled_links +=1
                Already_exist +=1
                # print('\n'+news['Link']+'\nNews Already Exist in DB\n')        
            else:
                news = {}
                news['Date'] = dateparser.parse(j['date'])
                news['announcementType'] = 'News'
                news['Source'] = 'https://www.adhq.com/about/ad-news'
                news['News_Weblink'] = 'https://www.adhq.com/about/ad-news/'+j['url_segment']
                news['title'] = j['title']
                news['photo'] = 'https://www.adhq.com/content/news/images/' + j['image']
                news['announcement'] = j['description']
                news['Language'] =  'English'
                news['analysis'] = j['author']
                SC = []
                for x in j['topic']:
                    SC.append(x['news_categories_name'])
                news['historySubCategory'] = ','.join(SC)
                news['Crawled_on'] = datetime.now()
                total_crwalled_links +=1
                collection.insert_one(news)
        if Already_exist >=1:
            tmp_txt = ' , from which '+str(Already_exist) +' Links were Already Crawled '
        else:
            tmp_txt = ''

        running_Sequence.append(str(total_crwalled_links) + ' Links are crawled ' + tmp_txt)
        ended_on = datetime.now()

except Exception as e:

    Error_Time =  datetime.now()
    Reported_Error = traceback.format_exc()
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
