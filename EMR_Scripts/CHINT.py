# imporhttp://localhost:8888/notebooks/anaconda3/techlets/EMR-Scripts/chintglobal/chintglobal%20data.ipynb#t requests
import time
import json
import requests
from random import randint
from bs4 import BeautifulSoup
from pymongo import MongoClient
# from selenium import webdriver
# from seleniumwire import webdriver as wireWebdriver  # Import from seleniumwire
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
import re
from datetime import date, timedelta
import datetime
import dateparser
import copy
from datetime import datetime
today = datetime.now()
import traceback
log_obj={
    'Crawler_name':'ChintNewsCrawler',
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
    
def scrap_page_news(source,news_link):
    try:
        news_req=requests.get(news_link, timeout=120)
    except:
        return False
    news_soup=BeautifulSoup(news_req.content,'lxml')
    main=news_soup.find('div',class_='chint-news-detail-container')
    try:
        title=main.find('div',class_='chint-news-detail-title').text.strip()
    except:
        title=''
    try:
        date=main.find('div',class_='chint-news-detail-time').text.strip()
        date=dateparser.parse(date)
    except:
        date=''
    try:
        img=main.find('div',class_='disabled-ck-toolbar chint-news-detail ng-star-inserted').find('img').get('src')
    except:
        img=''
    try:
        paraDiv=main.find('div',class_='disabled-ck-toolbar chint-news-detail ng-star-inserted').find_all('p')
        announcement=''
        for p in paraDiv:
            if(len(p.text.strip())>1):
                announcement=announcement+' '+p.text.strip()
    except:
        announcement=''
    catagory='News Center'
    NewsData= {}
    NewsData['companyId'] = ''
    NewsData['location']='' 
    NewsData['comment']=''
    NewsData['Date']=date
    NewsData['Source'] = source
    NewsData['historySubCategory']='News Center'
    NewsData['News_Weblink'] = news_link
    NewsData['photo']= img

    NewsData['Language']= 'English'
    today=datetime.today()
    NewsData['Crawled_on']=today
    NewsData['title']=title

    NewsData['announcement']=announcement
    NewsData['announcementType']='Company News'

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



def Parser(source,localDb,localCollectionName):
    scraped_News=[]
    nWorking=True
    try:
        main_req=requests.get(source,timeout=240)
    except:
        log_obj['Running_sequance'].append('Website is not working')
        nWorking=False
    if(nWorking):
        main_soup=BeautifulSoup(main_req.content,'lxml')
        lastIndex=(main_soup.find('ul',class_='at-pagination at-pagination--normal ng-star-inserted').find_all('li'))[-2].text
        flag=False
        index=1
        while(index<=int(lastIndex)):
            if(flag):
                break
            page='https://chintglobal.com/news-center-14-page'+str(index)
            
            try:
                page_req=requests.get(page, timeout=120)
            except:
                log_obj['Running_sequance'].append('page timeOut: '+page)
                index+=1
                continue
            page_soup=BeautifulSoup(page_req.content,'lxml').find('div',class_='chint-news-center-container').find_all('div',class_='chint-news-box')
            for oneNews in page_soup:
                news_link=oneNews.find('a').get('href')
                status=check_link_exists(news_link,localDb,localCollectionName)
                if(status):
                    print ('exist')
                    flag=True
                    break
                else:
                    print ('not exist')
                    print (news_link)
                    NewsData=scrap_page_news(source,news_link)
                    if(NewsData==False):
                        pass
                        log_obj['Running_sequance'].append('News timeOut: '+news_link)
                    else:
                        scraped_News.append(NewsData)
    #                 print ('**************************')
    #                 print (NewsData)

            index+=1
        if(len(scraped_News)>0):
            localDb.get_collection(localCollectionName).insert_many(scraped_News)
        log_obj['Running_sequance'].append(str(len(scraped_News))+" new news inserted in db.")
        return scraped_News
    
    
                       
        
if __name__ == "__main__":    
    try:    
        key='mongodb://localhost:27017/'
    #         dbName='chintglobal'
    #         collectionName='news_test'
    #     key='mongodb://su-du-ad:updatedSuperDuperAdmin@18.156.208.71:27017/emrweb?authSource=admin'
        dbName='TEMP_EMR_NEWS_Crawler_DB'
        collectionName='chintglobal'
        url='https://chintglobal.com/news-center-14'
        Client=CreateDbConnection(key)
        db =  Client[dbName]
        log_collection=db['logs_test_chint']
        Parser(url,db,collectionName)
        log=copy.deepcopy(log_obj)
        log['Ending_time']=datetime.now()
        log_collection.insert_one(log)
    except:
        rep = traceback.format_exc()
        log=copy.deepcopy(log_obj)
        log_obj['Running_sequance'].append (rep)
        log['Ending_time']=datetime.now()
        log_collection.insert_one(log)
