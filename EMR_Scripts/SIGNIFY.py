import requests
import time
import json
import traceback
from random import randint
from bs4 import BeautifulSoup
from pymongo import MongoClient
from bs4 import BeautifulSoup
from requests.api import head
from selenium import webdriver
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
from Emr_Crawlers_Optimization import Emr_Crawlers_Logs
running_Sequence = []
started_on = datetime.now()
c_name = 'SIGNIFY'
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
try:
    try:
        # total_page = json.loads(requests.get('https://www.signify.com/content/signify/en_AA/our-company/news/n13-press-releases.feeds.json').text)

        proxies = {'http': 'http://waleeProxy:Cheeta@1@de.proxymesh.com:31280',
            'https': 'http://waleeProxy:Cheeta@1@de.proxymesh.com:31280'}

        agent = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36", "Accept": "application/yang-data+json"}
        total_page = requests.get("https://www.signify.com/content/signify/en_AA/our-company/news/n13-press-releases.feeds.json", proxies=proxies)
        # headers=agent, verify=False
    except Exception as e:
        print(e)
    data = total_page.json()
    for j in data:
        N_link = str(j['link']) 
        Emr_Crawlers_Logs(c_name,N_link)
        l = False
        for k in collection.find({ 'News_Weblink' :N_link}):
            if k:
                # print("Skip Link")
                # print(j['link'])
                l = True
                break
        Emr_Crawlers_Logs(c_name,l)
        if l:
            total_crwalled_links +=1
            Already_exist +=1
            # print('\n'+news['Link']+'\nNews Already Exist in DB\n')
              
        else:
            # print("idr aagya ha")
            news = {}
            news['Date'] = dateparser.parse(j['publishedDate'])
            news['announcementType'] = 'News'
            news['Source'] = 'https://www.signify.com/global/our-company/news/press-releases'
            news['News_Weblink'] = j['link']
            news['title'] = j['title']
            news['photo'] = 'https://www.signify.com'+j['image']
            resp = requests.get(news['News_Weblink']).content
            ann = []
            for p in BeautifulSoup(resp,'lxml').find_all('span',class_ = 'p-body-copy-02'):
                ann.append(p.text.strip())
            news['announcement'] = '\n'.join(ann)
            news['Language'] =  'English'
            news['analysis'] = j['description']
            news['historySubCategory'] = j['tags']
            news['Crawled_on'] = datetime.now()
            total_crwalled_links +=1
            collection.insert_one(news)
            print("Inserted")
######################## EVENTS ########################################
    # total_page = json.loads(requests.get('https://www.signify.com/content/signify/en_AA/our-company/news/n13-press-releases.feeds.json').text)
    url = 'https://www.signify.com/global/our-company/news/events'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content,'lxml')
    tmp = soup.find('div',class_='gc04v3-gridcontainer section').find_next('div',class_='gc04v3-gridcontainer section').find('div',class_='p-grid')
    soup_1 = tmp.find_all('div',attrs={'id':['item_1','item_3'],'class':True,'style':False})
    for j in soup_1:
        l = False
        weblink = j.find('a').get('href')
        for k in collection.find({ 'News_Weblink' : weblink }):
            if k:
                l = True
                break
        if l:
            total_crwalled_links +=1
            Already_exist +=1
            # print('\n'+news['Link']+'\nNews Already Exist in DB\n')        
        else:
            sub_soup = BeautifulSoup(requests.get(weblink).content, 'lxml')
            news = {}
            ann = []
            date = sub_soup.find('meta',attrs={'name':'ISS_LAST_MODIFIED'}).get('content')
            news['Date'] = dateparser.parse(date)
            news['announcementType'] = 'Event'
            news['Source'] = url
            news['News_Weblink'] = weblink
            news['title'] = j.find('h3').text.strip() if j.find('h3') != None else ''
            try:
                news['photo'] = sub_soup.find('meta',attrs={'property':'og:image'}).get('content')
            except:
                news['photo'] =  ''
            tmp = soup.find('div',class_='p-body-text p-l-col1 p-m-col1 p-s-col1 p-xs-col1 p-text-smaller')
            tmp = tmp.find_next('div',class_='p-body-text p-l-col1 p-m-col1 p-s-col1 p-xs-col1 p-text-smaller') # Event Detail Added
            ann.append(tmp.text.strip())
            tmp = tmp.find_next('div',class_='p-body-text p-l-col1 p-m-col1 p-s-col1 p-xs-col1 p-text-smaller') # First Presenter 
            tmp = tmp.find_next('div',class_='p-body-text p-l-col1 p-m-col1 p-s-col1 p-xs-col1 p-text-smaller') # Second Presenter 
            tmp = tmp.find_next('div',class_='p-body-text p-l-col1 p-m-col1 p-s-col1 p-xs-col1 p-text-smaller') # First Presenter Detail
            tmp = tmp.find_next('div',class_='p-body-text p-l-col1 p-m-col1 p-s-col1 p-xs-col1 p-text-smaller') # Second Presenter 
            tmp = tmp.find_next('div',class_='p-body-text p-l-col1 p-m-col1 p-s-col1 p-xs-col1 p-text-smaller') # Keynotes Points Added
            ann.append(tmp.text.strip())
            # print(ann)
            news['announcement'] = '\n'.join(ann)
            news['Language'] =  'English'
            news['analysis'] = j.find('span',class_='p-body-copy-01').text.strip() if j.find('span',class_='p-body-copy-01')!= None else ''
            news['historySubCategory'] = sub_soup.find('meta',attrs={'name':'ISS_KEYWORD'}).get('content') if sub_soup.find('meta',attrs={'name':'ISS_KEYWORD'})!= None else ''
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
