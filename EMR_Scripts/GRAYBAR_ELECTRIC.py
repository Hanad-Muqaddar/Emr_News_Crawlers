from hashlib import new
from unicodedata import category
import requests
import time
import json
from random import randint
from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium import webdriver
# from seleniumwire import webdriver as wireWebdriver  # Import from seleniumwire
from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import re
from datetime import date, timedelta
import datetime
import dateparser
import copy
from datetime import datetime
today = datetime.now()
import traceback
from scrapy import Selector

log_obj={
    'Crawler_name':'hitachiabbNewsCrawler',
    'Starting_time':datetime.now(),
    'Ending_time':'',
    'Running_sequance':[],
    }
def CreateDbConnection(key):
    try:
        client= MongoClient(key)
        log_obj['Running_sequance'].append('Connected to Server')
    except:
        log_obj['Running_sequance'].append('Not Connected')
    return client

def check_link_exists(url,db,collection):
    ch=db.get_collection(collection).find({'News_Weblink':url})
    check=[]
    for x in ch:
        check.append(x)
    if(len(check)==0):
        return False
    else:
        return True 


def Parser1(mainPageUrl, localdb, localcollectionname):
    result = requests.get(mainPageUrl)
    response = Selector(result)
    trs = response.css(".news tbody tr")
    for tr in trs:
        try:
            news_web_link = "https://www.graybar.com/" + tr.css("a ::attr(href)").get()
        except:
            news_web_link = ""
        if news_web_link == "":
            continue

        status=check_link_exists(news_web_link,localdb,localcollectionname)
        if status:
            continue
        else:
            try:
                news_date = tr.xpath(".//td[@data-label='Date']/text()").get()
                news_date = dateparser.parse(news_date)
            except:
                news_date = ""
            try:
                title = tr.css('a ::text').get()
            except:
                title = ""
            try:
                category = tr.xpath('.//td[@data-label="Category"]/text()').get()
            except:
                category = ""
            result2 = requests.get(news_web_link)
            response2 = Selector(result2)

            try:
                announcement = response2.xpath("normalize-space(//div[@class='col-sm-9'])").get()
            except:
                announcement = ""
            

            NewsData= {}
            NewsData['companyId'] = ''
            NewsData['location']='' 
            NewsData['comment']=''
            NewsData['Date']=news_date
            NewsData['Source'] = "https://www.graybar.com/news"
            NewsData['historySubCategory']=category
            NewsData['News_Weblink'] = news_web_link
            NewsData['photo']= ""
            NewsData['videos']= ""
            NewsData['Language']= 'English'
            today=datetime.today()
            NewsData['Crawled_on']=today
            NewsData['title']=title
            NewsData['announcement']=announcement
            NewsData['announcementType']=category

            try:
                localdb.get_collection(localcollectionname).insert(NewsData)
                # print("Inserted")
            except Exception as e:
                print(e)
            
                       
        
if __name__ == "__main__": 

    try:
             
        key='mongodb://su-du-ad:updatedSuperDuperAdmin@18.156.208.71:27017/emrweb?authSource=admin'
        dbName='TEMP_EMR_NEWS_Crawler_DB'
        collectionName='GRAYBAR_ELECTRIC'
#         key='mongodb://localhost:27017/'
#         dbName='GE'
#         collectionName='news_test'
        url='https://www.graybar.com/news'
    #     url='https://www.hitachiabb-powergrids.com/content/pg/www/en/news/all-news/jcr:content/root/container/newslist.L2NvbnRlbnQvcGcvd3d3L2VuL21lZGlhL2pjcjpjb250ZW50L3Jvb3QvY29udGFpbmVyL2NvbnRhaW5lci9uZXdzbGlzdA==.list.json?page=0'
        Client=CreateDbConnection(key)
        db =  Client[dbName]
        Parser1(url,db,collectionName)
        log_collection=db['logs']
        log=copy.deepcopy(log_obj)
        log['Ending_time']=datetime.now()
        log_collection.insert_one(log)
    except:
        log_collection=db['logs']
        rep = traceback.format_exc()
        log=copy.deepcopy(log_obj)
        log_obj['Running_sequance'].append(rep)
        log['Ending_time']=datetime.now()
        log_collection.insert_one(log)
