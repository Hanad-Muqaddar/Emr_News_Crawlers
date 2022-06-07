from socket import SO_REUSEPORT
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
from selenium.webdriver.common.touch_actions import TouchActions
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
c_name = 'ROCKWELL'
opts.headless = True
try:
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
    driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver',options=opts)
    driver.set_page_load_timeout(220)
    driver.implicitly_wait(220)
    driver.get('https://ir.rockwellautomation.com/press-releases/default.aspx')
    urls = []
    for i in BeautifulSoup(driver.page_source, 'lxml').find('ul', class_ = 'sbOptions').find_all('li'):
        urls.append('https://ir.rockwellautomation.com/press-releases/default.aspx'+i.find('a').get('href'))
    news_list = []
    for link in urls:
        driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver',options=opts)
        driver.set_page_load_timeout(700)
        driver.implicitly_wait(700)
        driver.get(link)
        time.sleep(10)
        running_Sequence.append('Getting News for '+ link)
        soup = BeautifulSoup(driver.page_source, 'lxml').find('div', class_ = 'news-widget ModulePressRelease').find('div', class_ = 'items').find_all('div', class_  =['ModuleItemRow ModuleItem','ModuleItemRow ModuleItemAlt'])
        skip_next = False
        if soup != None:
            for i in soup:
                date = i.find('span', class_ = 'ModuleDate').text.strip()
                name = i.find('a').text.strip()
                news_link = 'https://ir.rockwellautomation.com'+i.find('a').get('href')
                resp = requests.get(news_link)
                sub_soup = BeautifulSoup(resp.content, 'lxml').find('div',class_ = 'q4default').find_all('p')

                if sub_soup != None:
                    ann = []
                    for ps in sub_soup:
                        ann.append(ps.text.strip())
                    announcement = '\n'.join(ann)
                else:
                    announcement = ''

                news = copy.deepcopy(news_dict_template)
                news['Date'] = dateparser.parse(date)
                news['announcementType'] = 'Press Release'
                news['Source'] = link
                news['News_Weblink'] = news_link
                news['title'] = name
                news['announcement'] = announcement
                news['Language'] = 'English'
                # print(news_link)
                news_list.append(news)
        for i in news_list:
            weblink = i['News_Weblink']
            l = False
            for k in collection.find({ 'News_Weblink' : weblink }):
                if k:
                    l = True
                    skip_next = True
                    break
                else:
                    skip_next = False
            if l:
                total_crwalled_links +=1
                Already_exist +=1
                # print('\n'+news['Link']+'\nNews Already Exist in DB\n')        
            else:
                i['Crawled_on'] = datetime.now()
                total_crwalled_links +=1
                collection.insert_one(i)
        if skip_next:
            running_Sequence.append(link+'\n Next Links are skipped')
            break
        else:
            pass
    driver.quit()

########################## Event ###########################################

    driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver',options=opts)
    driver.set_page_load_timeout(220)
    driver.implicitly_wait(220)
    driver.get('https://ir.rockwellautomation.com/events-and-presentations/default.aspx')
    try:
        soup = BeautifulSoup(driver.page_source,'lxml').find_all('div',class_=['past-events','upcomingevents'],id=False)
    except:
        soup = None
    if soup != None:
        for i in soup:
            if i.text.strip() != 'No items found.':
                try:
                    soup = i.find('div',class_='event-list').find_all('div',class_=['ModuleItemRow clearfix alt','ModuleItemRow clearfix'])
                except:
                    soup = None
                if soup != None:
                    for j in soup:
                        weblink = 'https://ir.rockwellautomation.com'+j.find('a').get('href')
                        l = False
                        for k in collection.find({ 'News_Weblink' : weblink }):
                            if k:
                                l = True
                                skip_next = True
                                break
                            else:
                                skip_next = False
                        if l:
                            total_crwalled_links +=1
                            Already_exist +=1
                            # print('\n'+news['Link']+'\nNews Already Exist in DB\n')        
                        else:
                            date = j.find('span',class_='ModuleDate').text.strip()
                            title = j.find('a').text.strip()
                            news = copy.deepcopy(news_dict_template)
                            news['Date'] = dateparser.parse(date)
                            news['announcementType'] = 'Event'
                            news['Source'] = 'https://ir.rockwellautomation.com/events-and-presentations/default.aspx'
                            news['News_Weblink'] = weblink
                            news['title'] = title
                            news['Language'] = 'English'
                            news['Crawled_on'] = datetime.now()
                            total_crwalled_links +=1
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
