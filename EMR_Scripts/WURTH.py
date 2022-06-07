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
from selenium.webdriver.common.touch_actions import TouchActions
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
c_name = 'WURTH'
opts.headless = True

def News_SinglePageParser( url ):
    req= requests.get(url)
    soup = BeautifulSoup(req.content,'lxml')   
    news = {}
    news['Date'] = ''
    news['Language'] = 'English'
    news['announcementType'] = 'News'
    news['Source'] = url
    news['News_Weblink'] =url 
    news['announcement'] =  soup.find('article',class_='div_text_companyprofile').text.strip() if soup.find('article',class_='div_text_companyprofile')!=None else ''
    news['title'] = soup.find('title').text.strip()
    news['photo'] = soup.find('meta',attrs={'property':'og:image'}).get('content') if soup.find('meta',attrs={'property':'og:image'})!= None else ''
    news['Language'] =  'English'
    news['analysis'] = soup.find('meta',attrs={'property':'og:description'}).get('content') if soup.find('meta',attrs={'property':'og:description'})!= None else ''
    news['historySubCategory'] = soup.find('meta',attrs={'name':'keywords'}).get('content').split(',') if soup.find('meta',attrs={'name':'keywords'})!= None else ''
    news['Crawled_on'] = datetime.now()
    return news
def get_date(i):
    day = i.find('div',class_='pp_date_day').text.strip()
    month = i.find('div',class_='pp_date_month').text.strip()
    year = i.find('div',class_='pp_date_year').text.strip()
    time = i.find('span',class_='pp_release_time').text.strip() if i.find('span',class_='pp_release_time')!= None else ''
    return day+'/'+month+'/'+year+'-'+time
try:
    # client= MongoClient('mongodb://su-du-ad:updatedSuperDuperAdmin@18.156.208.71:27017/emrweb?authSource=admin')
    file = open("/home/emr/config.json")
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
try:
    driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver',options=opts)
    driver.set_page_load_timeout(220)
    driver.implicitly_wait(220)
    driver.get('https://news.wuerth.com/?h=1&all=1')

    while True:
        if BeautifulSoup(driver.page_source,'lxml').find('a',class_='pp_button_grey newscount_more button_more'):
            driver.find_element_by_css_selector('#ppmodule_allheadlines > div > div > div.pp_bigheadlines_end > div > a').click()
            time.sleep(2)
        else:
            break
        
    storePostsURL =[]
    soup = BeautifulSoup(driver.page_source,'lxml').find('div',class_='archive_item_container pp_big_headlines_item_container')
    for i in soup.find_all('div',class_='mm_listitem'):
        data = {'Date':get_date(i),'link':'https:'+i.find('a').get('href')}
        storePostsURL.append(data)

    for i in storePostsURL:
        l = False
        for k in collection.find({ 'News_Weblink' : i['link'] }):
            if k:
                l = True
                break
        if l:
            total_crwalled_links +=1
            Already_exist +=1       
        else:
            total_crwalled_links +=1
            news = News_SinglePageParser(i['link'])
            news['Date'] =  dateparser.parse(i['Date'])
            collection.insert_one(news)
       
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
