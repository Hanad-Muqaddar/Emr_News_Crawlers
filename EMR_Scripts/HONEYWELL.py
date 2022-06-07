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
c_name = 'HONEYWELL'
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
    urls ='https://www.honeywell.com/us/en/in-the-news'
    print('First link hogya')
    req = requests.get(urls)
    soup = BeautifulSoup(req.content,'lxml').find('div', class_ ='content-grid-items').find_all('a', target = '_blank')
    for i in soup:
        weblink = i.get('href')
        if weblink !="https://www.renewableenergymagazine.com/biofuels/united-honeywell-invest-in-new-clean-tech-20210909":
            continue
        print(weblink)
        if weblink[:1] == '/':
            print("idr nai aaya")
            weblink = 'https://www.honeywell.com'+weblink
        l = False
        print("False hogya ha")
        for k in collection.find({'News_Weblink': weblink }):
            print("is mn aagya ha")
            if k:
                l = True
                print("Pala sa pari hui hn")
                break
        if l:
            total_crwalled_links +=1
            Already_exist +=1
            # print('\n'+news['Link']+'\nNews Already Exist in DB\n')        
        else:
            print("Insert horaha ha")
            image = 'https://www.honeywell.com'+i.find('div', class_ = 'col-12 col-md-5 text-center').find('img').get('src')
            print(image)
            title = i.find('div', class_ = 'col-12 col-md-7 pl-md-0 pr-md-0').find('h4').text.strip()
            print(title)
            announcement = i.find('div', class_ = 'col-12 col-md-7 pl-md-0 pr-md-0').find('div',class_ = 'body1').text.strip()
            print(announcement)
            news = copy.deepcopy(news_dict_template)
            news['announcementType'] = 'News'
            news['Source'] = urls
            news['News_Weblink'] = weblink
            news['title'] = title
            news['announcement'] = announcement
            news['Language'] = 'English'
            news['photo'] = image
            news['Crawled_on'] = datetime.now()
            total_crwalled_links +=1
            print(news)
            collection.insert_one(news)
    if Already_exist >=1:
        tmp_txt = ' , from which '+str(Already_exist) +' Links were Already Crawled '
    else:
        tmp_txt = ''

    running_Sequence.append(str(total_crwalled_links) + ' Links are crawled ' + tmp_txt)
    running_Sequence.append('Starting Press Release Crawler')
    req = requests.get('https://www.honeywell.com/us/en/press')
    # driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver',options=opts)
    # driver.set_page_load_timeout(220)
    # driver.implicitly_wait(220)
    # driver.get(urls)
    soup = BeautifulSoup(req.content,'lxml').find('ul',class_='data-list list-component__grid-list d-flex flex-row flex-wrap grid-articlegrid')
    soup = soup.find_all('li', class_ = 'data-list__item list-component__item col-md-12 col-12 col-md-4 col-lg-4 list--three-column')
    for i in soup:
        weblink = 'https://www.honeywell.com'+i.find('a',attrs={'class':True,'target':True}).get('href')
        # if weblink[:1] == '/':
        #     weblink = 'https://www.honeywell.com'+weblink
        l = False
        for k in collection.find({ 'News_Weblink' : weblink }):
            if k:
                l = True
                break
        if l:
            total_crwalled_links +=1
            Already_exist +=1
            # print('\n'+news['Link']+'\nNews Already Exist in DB\n')        
        else:
            try:
                resp = requests.get(weblink)
            except:
                continue
            sub_soup_1 = BeautifulSoup(resp.content,'lxml')
            news = copy.deepcopy(news_dict_template)
            ann = ['']
            date = i.find('span',class_ = 'list-component__item-displaydate').text.strip().split('|')[0]
            try:
                sub_soup = BeautifulSoup(resp.content,'lxml').find('div',class_ = 'cmp-text').find_all('p')
            except:
                sub_soup = None
            if sub_soup!=None:
                for p in sub_soup:
                    ann.append(p.text.strip())
            news['announcement'] = '\n'.join(ann)
            # news['Date'] = soup.find('meta',attrs={''})
            news['title'] = sub_soup_1.find('title').text.strip()
            news['historySubCategory'] = sub_soup_1.find('meta',attrs={'name':'keywords'}).get('content') if sub_soup_1.find('meta',attrs={'name':'keywords'})!=None else ''
            news['Source'] = 'https://www.honeywell.com/us/en/press'
            news['analysis'] = sub_soup_1.find('meta',attrs={'name':'description'}).get('content') if sub_soup_1.find('meta',attrs={'name':'description'})!=None else ''
            news['News_Weblink'] = weblink
            news['announcementType'] = 'Press Release'
            news['Language'] = 'English'
            news['Date'] = dateparser.parse(date)
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
    # Reported_Error = traceback.format_exc()
    Reported_Error = str(e)


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
