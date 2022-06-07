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
c_name = 'LEGRAND'
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
    urls = []
    for i in range(42):
        urls.append('https://www.legrandgroup.com/en/press/newsroom?page='+str(i+1))
    driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver',options=opts)
    driver.set_page_load_timeout(220)
    driver.implicitly_wait(220)
    for url in urls:
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        skip_all_next = False
        soup = BeautifulSoup(driver.page_source,'lxml')
        all_links = soup.find_all('div',class_ = 'module block-blocs')
        for i in all_links:
            weblink = 'https://www.legrandgroup.com' + i.find('div', class_ = 'text').find('a').get('href')
            l = False
            for k in collection.find({ 'News_Weblink' : weblink }):
                if k:
                    l = True
                    skip_all_next = True
                    break
                else:
                    skip_all_next = False
            
            if l:
                total_crwalled_links +=1
                Already_exist +=1
                # print('\n'+news['Link']+'\nNews Already Exist in DB\n')        
            else:
                if i.find('div', class_ = 'text').find('a').get('href'):
                    req= requests.get(weblink)
                    time.sleep(1)
                    soup_2 = BeautifulSoup(req.content, 'lxml')
                    try:
                        announcement = []
                        for j in soup_2.find('div', class_ = 'wysiwyg').find_all('p'):
                            announcement.append(j.get_text().replace('\xa0',' '))
                        ann = '\n'.join(announcement)
                    except:
                        try:
                            ann= i.find('div', class_ = 'text').get_text().strip()
                        except:
                            ann = ''
                
                news = copy.deepcopy(news_dict_template)
                news['Date'] = dateparser.parse(i.find('div' , class_ = 'info').get_text().strip().split('|', 1)[1].strip())
                news['announcementType'] = 'News'
                news['Source'] = url
                news['announcement'] = ann
                news['News_Weblink'] = weblink
                news['title'] = i.find('div', class_ = 'text').find('h4').get_text().strip()
                news['Language'] = 'English'
                news['historySubCategory'] = i.find('div' , class_ = 'info').get_text().strip().split('|', 1)[0].strip()
                news['Crawled_on'] = datetime.now()
                total_crwalled_links +=1
                collection.insert_one(news)
        if skip_all_next:
            running_Sequence.append('Next pages are Skipped')
            break
    if Already_exist >=1:
        tmp_txt = ' , from which '+str(Already_exist) +' Links were Already Crawled '
    else:
        tmp_txt = ''

    running_Sequence.append(str(total_crwalled_links) + ' Links are crawled ' + tmp_txt)
    ended_on = datetime.now()
    driver.quit()
except Exception as e:
    driver.quit()
    Error_Time =  datetime.now()
    Reported_Error = traceback.format_exc()
rep = ''
try:
    Error = {}
    Error['Error_Detail'] = Reported_Error
    Error['Error_Time'] = Error_Time
except Exception as e:
    driver.quit()
    rep = str(e)
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
