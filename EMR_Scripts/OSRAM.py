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
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support import expected_conditions
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.touch_actions import TouchActions
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
# from bson.objectid import ObjectId
# from urllib.error import HTTPError
# from urllib.request import Request, urlopen
running_Sequence = []
started_on = datetime.now()
c_name = 'OSRAM'
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
try:
    ################ NEWS Release #####################################
    url = "https://9ps0m7duie-2.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%20(lite)%3B%20react%20(16.12.0)%3B%20react-instantsearch%20(5.7.0)%3B%20JS%20Helper%20(2.28.0)&x-algolia-application-id=9PS0M7DUIE&x-algolia-api-key=321a182fe8706b78ee3234b41c7b58f7"
    news_num = 10
    payload = json.dumps({
      "requests": [
        {
          "indexName": "prod_OSRAM_COM_en",
          "params": "query=&hitsPerPage=10&maxValuesPerFacet=200&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22content_type_keyword%22%2C%22bu_multi_keyword%22%2C%22dp_applications%22%2C%22dp_subapplications%22%2C%22dp_technology%22%2C%22dp_year%22%2C%22dp_city%22%5D&tagFilters=&facetFilters=%5B%5B%22bu_multi_keyword%3AOpto%20Semiconductors%22%5D%2C%5B%22content_type_keyword%3AReference%22%5D%5D"
        },
        {
          "indexName": "prod_OSRAM_COM_en",
          "params": "query=&hitsPerPage=1&maxValuesPerFacet=200&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=bu_multi_keyword&facetFilters=%5B%5B%22content_type_keyword%3AReference%22%5D%5D"
        },
        {
          "indexName": "prod_OSRAM_COM_en",
          "params": "query=&hitsPerPage=1&maxValuesPerFacet=200&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=content_type_keyword&facetFilters=%5B%5B%22bu_multi_keyword%3AOpto%20Semiconductors%22%5D%5D"
        }
      ]
    })
    headers = {
      'Content-Type': 'application/json'
    }
    resp = requests.request("POST", url, headers=headers, data=payload)
    newsData = resp.json()['results'][0]['hits']
    # print(newsData)
    # print(type(newsData))
    # print(len(newsData))
    for j in newsData:
        print(j['link'])
        l = False
        for k in collection.find({'News_Weblink': j['link'] }):
            if k:
                l = True
                break
        if l:
            total_crwalled_links +=1
            Already_exist +=1
            # print(j['link'])
            # print('\n'+news['Link']+'\nNews Already Exist in DB\n')        
        else:
            news = {}
            news["companyId"] = ""
            news["location"] = ""
            try:
                newsdate = j['dp_release_date']
                newsdate = str(newsdate)
                news['Date'] = dateparser.parse(newsdate)
            except Exception as e:
                news['Date'] = datetime.now()
            try:
                news['title'] = j['title']
            except:
                news['title'] = ""
            try:
                news['announcementType'] = j['dp_applications']
            except:
                news['announcementType'] = ""
            try:
                news['announcement'] = j['content']
            except:
                news['announcement'] = ""
            try:
                news['photo'] = j['src1_picture_stored_only']
            except:
                news['photo'] = ""
            try:
                news['Language'] =  'English'
            except:
                news['Language'] = ""
            try:
                news['Crawled_on'] = datetime.now()
            except:
                news['Crawled_on'] = ""
            news['Source'] = "https://www.osram.com/cb/news/index.jsp"
            try:
                news['News_Weblink'] = j['link']
            except:
                news['News_Weblink'] = ""
            try:
                news['historySubCategory'] = j['dp_subheadline']
            except:
                news['historySubCategory'] = ""
            
            try:
                news['analysis'] = j['dp_summary']
            except:
                news['analysis'] = ""
            validation_obj = {}
            validation_obj['companyId'] = news["companyId"]
            validation_obj['Date'] = news['Date']
            validation_obj['title'] = news['title']
            validation_obj['announcement'] = news['announcement']
            validation_obj['photo'] = news['photo']
            validation_obj['analysis'] = j['dp_summary']
            validation_obj['refrences'] = ''
            validation_obj['historySubCategory'] = ''
            news['validatedObject'] = validation_obj
            
            total_crwalled_links +=1
            collection.insert_one(news)

    ################ Press Release #####################################
    # 211
    for i in range(5):
        url = 'https://www.osram-group.de/en/media/press-releases?page='+str(i)
        cookie = 'www-osram-group-de#lang=en; ASP.NET_SessionId=50yd5verhptjn1obsai3atlz; AWSALB=hGTE64M7vVwh8A8tlATVS11ULcaJMUUblFoT23lBq6xZn0JwNvrtlcbBQSfe7U2gtbHqfX0zLgY8sdvwvUOV+mm9d/a4QBBukMGDX91s/2Vw+/MO0UBrrnNHLACl; AWSALBCORS=hGTE64M7vVwh8A8tlATVS11ULcaJMUUblFoT23lBq6xZn0JwNvrtlcbBQSfe7U2gtbHqfX0zLgY8sdvwvUOV+mm9d/a4QBBukMGDX91s/2Vw+/MO0UBrrnNHLACl; __CookieConsentV200={"consent":{"necessaryCookie":true,"performanceCookies":true},"accepted":true,"euCheck":false}'
        headers = {
        'accept': 'text/html, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': cookie,
        'referer':'https://www.osram-group.de/en/media/press-releases',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'}
        response = requests.request("GET", url, headers=headers)
        soup = BeautifulSoup(response.content,'lxml').find('div',class_='prContainer').find_all('div',class_='prItemWrapper row')
        # skip_next = False
        for x in soup:
            
            link = "https://www.osram-group.de"+x.find('a').get('href')
            l = False
            for k in collection.find({ 'News_Weblink' : link }):
                if k:
                    l = True
                    # print(link)
                    # skip_next = True
                    break
                # else:
                    # skip_next = False
            if l:
                
                total_crwalled_links +=1
                Already_exist +=1       
            else:
                print("In x loop")
                news = {}
                news["companyId"] = ""
                news["location"] = ""
                try:
                    resp = requests.request("GET", link, headers=headers)
                    sub_soup = BeautifulSoup(resp.content,'lxml')
                except:
                    sub_soup = None
                if sub_soup:
                    try:
                        ann = sub_soup.find('div',class_='prContent').text.strip()
                    except:
                        ann = ''
                    try:
                        image = sub_soup.find('meta',attrs={'property':'og:image'}).get('content')
                    except:
                        image = ''
                    try:
                        date_value = dateparser.parse(sub_soup.find('meta',attrs={'itemprop':'datePublished'}).get('content')) if sub_soup.find('meta',attrs={'itemprop':'datePublished'}).get('content')!= None else ''
                    except:
                        date_value = ''

                news['Date'] = dateparser.parse(x.get('id').replace('pr-',''),settings={'DATE_ORDER': 'DMY'}) if date_value == '' else date_value
                news['title'] = x.find(class_='titlePR').text.strip()
                news['announcementType'] = "Press Release"
                news['announcement'] = ann if ann != '' else x.find(class_='introPR').text[2:]
                news['photo'] = image
                news['Language'] =  'English'
                news['Source'] = "https://www.osram.com/cb/news/index.jsp"
                news['News_Weblink'] = link
                news['analysis'] = x.find(class_='introPR').text[2:]
                news['historySubCategory'] = ",".join([jj.text.strip() for jj in x.find_all('span',class_='addcomma')])
                news['Crawled_on'] = datetime.now()
                validation_obj = {}
                validation_obj['companyId'] = news["companyId"]
                validation_obj['Date'] = news['Date']
                validation_obj['title'] = news['title']
                validation_obj['announcement'] = news['announcement']
                validation_obj['photo'] = news['photo']
                validation_obj['analysis'] = news['analysis']
                validation_obj['refrences'] = ''
                validation_obj['historySubCategory'] = news['historySubCategory']
                news['validatedObject'] = validation_obj
                total_crwalled_links +=1
                collection.insert_one(news)
        # if skip_next:
        #     break

    

    if Already_exist >=1:
        tmp_txt = ' , from which '+str(Already_exist) +' Links were Already Crawled '
    else:
        tmp_txt = ''

    running_Sequence.append(str(total_crwalled_links) + ' Links are crawled ' + tmp_txt)
    ended_on = datetime.now()

except Exception as e:
    print(e)
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
