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
from Emr_Crawlers_Optimization import Emr_Crawlers_Logs
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

running_Sequence = []
started_on = datetime.now()
c_name = 'IMELCO'
opts.headless = True
try:
    # client= MongoClient('mongodb://su-du-ad:updatedSuperDuperAdmin@18.156.208.71:27017/emrweb?authSource=admin')
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
    for l_i in collection.find().sort('Crawled_on', -1).limit(1):
        last_insertion = l_i
except:
    # print('Fresh Starting News Crawler')
    last_insertion = None
if last_insertion == None:
    running_Sequence.append('Fresh Starting News Crawler on -> ' + str(datetime.now()))
    Crwl_time = datetime.now()
else:
    last_time = last_insertion['Crawled_on']
    running_Sequence.append('Last Crawled on -> '+str(last_insertion['Crawled_on'].date()))
    Crwl_time = last_insertion['Crawled_on']
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
    urls =['https://imelco.com/publications/press-releases']
    resp = requests.get(urls[0])
    soup = BeautifulSoup(resp.text, 'lxml').find('div',class_='vc_row wpb_row vc_row-fluid slant-top slant-top-noshadow').find('div',class_='wpb_text_column wpb_content_element').find_all(['div','a'])
    news = []
    news_list = []
    for i in soup[2:]:
        if '<div' in str(i):
            news.append(i.text.strip())
        elif '<a' in str(i) and i.get('target') and i.get('style')==None:
            news.append(i)
            news_list.append(news)
            news = []
    for i in news_list:            
        if i[2].get('href'):
            weblink = i[2].get('href')
            l = False
            for k in collection.find({ 'News_Weblink' : weblink }):
                if k:
                    l = True
                    # break
            Emr_Crawlers_Logs(c_name,l)
            if l:
                total_crwalled_links +=1
                Already_exist +=1
                # print('\n'+news['Link']+'\nNews Already Exist in DB\n')        
            else:
                news = copy.deepcopy(news_dict_template)
                news['title'] = i[2].find('h3').text.strip()
                news['Weblink (if available)'] = i[2].get('href')
                news['Source'] = urls[0]
                news['announcementType'] = 'Press Release - PDF'
                news['historySubCategory']= i[0]
                news['Language'] = 'English'
                news['Date'] = dateparser.parse(i[1]) if i[1]!='' else ''
                news['Crawled_on'] = datetime.now()
                total_crwalled_links +=1
                collection.insert_one(news)
    if Already_exist >=1:
        tmp_txt = ' , from which '+str(Already_exist) +' Links were Already Crawled '
    else:
        tmp_txt = ''

    running_Sequence.append(str(total_crwalled_links) + ' Links are crawled ' + tmp_txt)
    ended_on = datetime.now()
    # driver.quit()
except Exception as e:
    # driver.quit()
    Error_Time =  datetime.now()
    Reported_Error = traceback.format_exc()
rep = ''
try:
    Error = {}
    Error['Error_Detail'] = Reported_Error
    Error['Error_Time'] = Error_Time
except Exception as e:
    # driver.quit()
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
