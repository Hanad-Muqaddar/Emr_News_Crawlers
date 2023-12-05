from email import header
from hashlib import new
import requests
import time
import json
from random import randint
from bs4 import BeautifulSoup
from pymongo import MongoClient
from bs4 import BeautifulSoup
from requests import api
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
import sys
import dateparser
from datetime import datetime,date, timedelta
from bson.objectid import ObjectId
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from scrapy import Selector
#from Emr_Crawlers_Optimization import Emr_Crawlers_Logs

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

# Now you can access the getName function
running_Sequence = []
started_on = datetime.now()
# c_name = 'ABB_New_Testing'
c_name = 'ABB'
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

headers = {"authority": "script.crazyegg.com",
"method": "GET",
"path": "/pages/data-scripts/0021/5198.json?t=1",
"scheme": "https",
"accept": "*/*",
"accept-encoding": "gzip, deflate, br",
"accept-language": "en-US,en;q=0.9",
"if-modified-since": "Tue, 01 Feb 2022 08:01:36 GMT",
"origin": "https://new.abb.com",
"sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
"sec-ch-ua-mobile": "?0",
"sec-ch-ua-platform": "Windows",
"sec-fetch-dest": "empty",
"sec-fetch-mode": "cors",
"sec-fetch-site": "cross-site",
"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"}

def parse_filtered_news(announcement):
    api_url = "https://admin.new.emr-online.com/api/history/filterbody"
    # api_url = "http://192.168.60.105:3000/api/history/filterbody"
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
    ################ NEWS Release #####################################
    api_date = datetime.now().isoformat().split('T')[0]
    url_api = 'https://global.abb/group/en/media/releases/group.abbglobal-news-search.json?feeds=abb:feeds/group_functions/corporate_communications/group_press_releases&feedsOperator=OR&dateFrom=2020-01-01&dateTo='+str(api_date)+'&limit=100&offset=0'
    total_page = json.loads(requests.get(url_api).text)
    Optimization_links = []
    for j in total_page['news'][:10]:
        n_link = 'https://global.abb/'+ j['path']

        l = False
        for k in collection.find({ 'News_Weblink' : str('https://global.abb/'+j['path']) }):
            if k:
                l = True
                break
        Optimization_links.append(l)
        if l:
            total_crwalled_links +=1
            Already_exist +=1
            print("Already Crawled")
            # print('\n'+news['Link']+'\nNews Already Exist in DB\n')        
        else:
            news = {}
            news['Date'] = dateparser.parse(j['publishedOn'])
            news['announcementType'] = j['newsType']
            news['Source'] = 'https://global.abb/group/en/media/releases/group'
            news['News_Weblink'] = 'https://global.abb/'+ j['path']
            news['title'] = j['title']
            news['photo'] = j['thumbnailImageUrl']
            try:
                result = requests.get(news['News_Weblink'], headers=headers, timeout=10)
                resp = Selector(result)
                announcement = resp.css(".abb--reading-size--component-fix").get()
                replace1 = resp.css(".oneabb-newsbank-news-Header-title").get()
                replace2 = resp.css(".oneabb-newsbank-news-Header-subtitle").get()
                try:
                    announcement = announcement.replace(replace1,"")
                except:
                    pass
                try:
                    announcement = announcement.replace(replace2,"")
                except:
                    pass
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
            news['announcement'] = announcement
            news['Language'] =  'English'
            news['analysis'] = j['description']
            news['historySubCategory'] = ''
            news['Crawled_on'] = datetime.now()
            news['emrExecutive'] = emr_executive
            news['emrEssential'] = emr_essentail
            news['emrLite'] = emr_lite
            news['News_Html'] = emr_html

            total_crwalled_links +=1
            collection.insert_one(news)

    Web_Page = 'https://global.abb/group/en/media/releases/group'        
    Emr_Crawlers_Logs(c_name,Web_Page,Optimization_links)


########################### Stories #############################################################

    api_date = datetime.now().isoformat().split('T')[0]
    url_api = 'https://global.abb/group/en/media/releases/stories.abbglobal-news-search.json?feeds=abb:feeds/group_functions/corporate_communications/group_web_stories&feedsOperator=OR&dateFrom=2019-01-01&dateTo='+str(api_date)+'&limit=200&offset=0'
    total_page = json.loads(requests.get(url_api).text)
    for j in total_page['news'][:10]:
        n_link = 'https://global.abb/'+ j['path']
        l = False
        for k in collection.find({ 'News_Weblink' : str('https://global.abb/'+j['path']) }):
            if k:
                l = True
                break
        if l:
            total_crwalled_links +=1
            Already_exist +=1
            # print('\n'+news['Link']+'\nNews Already Exist in DB\n')        
        else:
            news = {}
            news['Date'] = dateparser.parse(j['publishedOn'])
            news['announcementType'] = j['newsType']
            news['Source'] = 'https://global.abb/group/en/media/releases/stories'
            news['News_Weblink'] = 'https://global.abb/'+j['path']
            news['title'] = j['title']
            news['photo'] = j['thumbnailImageUrl']
            try:
                result = requests.get(news['News_Weblink'], headers=headers, timeout=10)
                resp = Selector(result)
                announcement = resp.css(".abb--reading-size--component-fix").get()
                replace1 = resp.css(".oneabb-newsbank-news-Header").get()
                announcement = announcement.replace(replace1,"")
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
            news['announcement'] = announcement
            news['Language'] =  'English'
            news['analysis'] = j['description']
            news['historySubCategory'] = ''
            news['Crawled_on'] = datetime.now()
            news['emrExecutive'] = emr_executive
            news['emrEssential'] = emr_essentail
            news['emrLite'] = emr_lite
            news['News_Html'] = emr_html
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
# error_logs.insert_one(log)
