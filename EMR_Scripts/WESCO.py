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
log_obj={
    'Crawler_name':'WescoNewsCrawler',
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
    
def News_SinglePageParser(news_url,news_date,source):
    response3 =  requests.get(news_url)
    NewsData= {}
    NewsData['Date']=news_date
    NewsData['Source'] = source
    NewsData['historySubCategory']=''
    NewsData['News_Weblink'] = news_url
    try:
        title = BeautifulSoup(response3.content,'lxml').find('section',class_='main').find('div',class_='wd_title wd_language_left').text.strip()
    except:
        title=''
    try:
        NewsData['announcement'] = BeautifulSoup(response3.content,'lxml').find('section',class_='main').find('div',class_='wd_body wd_news_body').text
    except:
        NewsData['announcement']=''
    NewsData['companyId'] = ''
    NewsData['location']='' 
    NewsData['comment']=''
    NewsData['title']=title
    NewsData['announcementType']='News Releases'
    NewsData['photo']= ''
    NewsData['Language']= 'English'
    today=datetime.today()
    NewsData['Crawled_on']=today        
    refrences=''
    analysis=''
    validatedObject  ={}
    validatedObject['companyId']=NewsData['companyId']
    validatedObject['Date']=NewsData['Date']
    validatedObject['title']=NewsData['title']
    validatedObject['announcement']=NewsData['announcement']
    validatedObject['announcementType']=NewsData['announcementType']
    validatedObject['photo']=NewsData['photo']
    validatedObject['analysis']=analysis
    validatedObject['refrences ']=refrences
    validatedObject['historySubCategory']= NewsData['historySubCategory']
    NewsData['validatedObject']=validatedObject 
    return NewsData
    
def History_newsParser(url,localDb,localCollectionName):
    all_news=[]
    start_page=0
    try:
        response1 =  requests.get(url)
        pagination = BeautifulSoup(response1.content,'lxml').find('section',class_='main').find('div',class_='wd_page_menu').find_all('li')
        end_page=int(pagination[-2].find('a').text)
    except:
        end_page=1 

    count=0
    flag=False
    while (start_page<end_page):
 
        if(flag):
            break
        page_url='http://wesco.investorroom.com/news-releases?l=100&o='+str(count)
        try:
            response2 =  requests.get(url)
            news_liks = BeautifulSoup(response2.content,'lxml').find('section',class_='main').find('ul',class_='wd_layout-simple wd_item_list').find_all('li',class_='wd_item')
        except:
            rep = traceback.format_exc()
            log_obj['Running_sequance'].append (rep)
            break
            
        for news in news_liks:
            news_url=news.find('div',class_='wd_title').find('a').get('href')
            status=check_link_exists(news_url,localDb,localCollectionName)
            if(status):
                flag=True
#                 print ('exist')
#                 print ('*************')
                break
            else:
#                 print ("Not Exist in db")
                source=page_url
                try:
                    news_date=news.find('div',class_='wd_date').text
                    news_date=dateparser.parse(news_date)
                except:
                    news_date=''
                data=News_SinglePageParser(news_url,news_date,source)
                all_news.append(data)  
        
        count+=100
        start_page+=1
     
        

    if(len(all_news)>0):
        localDb.get_collection(localCollectionName).insert_many(all_news)
    log_obj['Running_sequance'].append(str(len(all_news))+ " new news inserted in db.")
                       
        
if __name__ == "__main__":    
    #   -----------LocalDBMapping---------------
    try:
        key='mongodb://su-du-ad:updatedSuperDuperAdmin@18.156.208.71:27017/emrweb?authSource=admin'
#         key='mongodb://localhost:27017/'
        dbName='TEMP_EMR_NEWS_Crawler_DB'
#         dbName='WESCO'
#         collectionName='news_test'
        collectionName='WESCO'
        url='https://investors.wesco.com/news-and-events/news-releases/'
        Client=CreateDbConnection(key)
        db =  Client[dbName]
        log_collection=db['logs']
        History_newsParser(url,db,collectionName)
        log=copy.deepcopy(log_obj)
        log['Ending_time']=datetime.now()
        
        log_collection.insert_one(log)
    except:
        rep = traceback.format_exc()
        log=copy.deepcopy(log_obj)
        log_obj['Running_sequance'].append (rep)
        log['Ending_time']=datetime.now()
        log_collection.insert_one(log)
