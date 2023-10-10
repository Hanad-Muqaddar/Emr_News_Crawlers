import requests
import time
import json
import traceback
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
import copy as copy
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
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
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


opts = Options()
opts.add_argument("--window-size=190,100")
opts.add_argument("--disable-automation")
opts.add_argument("--no-sandbox")
opts.add_argument('--profile-directory=Default')
opts.add_argument("start-maximized")
opts.add_argument("disable-infobars")
opts.add_argument("--lang=en")
opts.add_argument("--enable-javascript")
opts.add_argument("--enable-cookies")

running_Sequence = []
started_on = datetime.now()
c_name = 'ZVEI'
opts.headless = True
try:
    file = open("/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/config.json")
    data = json.load(file)
    db_path = data[0]['Db_Path']
    client = MongoClient(db_path)
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
news_dict_template = { 
        "Date" : "",
        "announcementType" : "",
        "Source" : "",
        "News_Weblink" : "",
        "title" : "",
        "photo" : "",
        "announcement" :'',
        "Language" : "",
        "analysis" : "",
        "historySubCategory" : "",
}
try:
    counter = 1
    news_link = []
    while True:
        url = 'https://www.zvei.org/en/press-media/pressarea?tx_kesearch_pi1%5Bpage%5D='+str(counter)+'&cHash=c4c42d4f256b5dddc94fd126a2943972'
        # print('\nGetting Link '+str(counter))
        resp = requests.get(url)
        counter +=1 
        soup = BeautifulSoup(resp.content,'lxml').find('div',attrs={'id':'ke_search-results','class':'results content-list margin-top20'}).find_all('div',class_='right-column')
        if soup != []:
            # print(soup)
            for a in soup:
                tmp = {}
                tmp['link'] = 'https://www.zvei.org'+a.find('a').get('href')
                tmp['Date'] = dateparser.parse(a.find('p',class_='h5').text.strip(), settings={'DATE_ORDER': 'DMY'})
                # print(tmp)
                if tmp not in news_link:
                    news_link.append(tmp)
        else:
            break
    # print('Link out')

    Emr_Crawlers_Logs(c_name,news_link)
    for url in news_link:
        n_link = url['link']
        
        l = False
        for k in collection.find({ 'News_Weblink' :n_link}):
            if k:
                l = True
                break
            
        if l:
            total_crwalled_links +=1
            Already_exist +=1
            # print('\n'+news['Link']+'\nNews Already Exist in DB\n')        
        else:
            resp = requests.get(url['link'])
            soup = BeautifulSoup(resp.content,'lxml')
            news = copy.deepcopy(news_dict_template)
            news['title'] = soup.find('title').text.strip()
            news['announcementType'] = 'Press Release'
            news['Source'] = 'https://www.zvei.org/en/press-media/pressarea'
            news['News_Weblink'] = url['link']
            news['photo'] = soup.find('meta',attrs={'name':'twitter:image'}).get('content') if soup.find('meta',attrs={'name':'twitter:image'})!=None else ''
            news['Language'] = 'English'
            news['Date'] = url['Date']
            news['analysis'] = soup.find('meta',attrs={'name':'twitter:description'}).get('content') if soup.find('meta',attrs={'name':'twitter:description'})!=None else ''
            news['historySubCategory'] = soup.find('meta',attrs={'name':'keywords'}).get('content') if soup.find('meta',attrs={'name':'keywords'})!=None else ''
            ann = soup.find('div',class_='row content-area-middle').find_all('div',attrs={'class':'small-12 large-8 columns'})[1]

            news['announcement'] = ann.text
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
