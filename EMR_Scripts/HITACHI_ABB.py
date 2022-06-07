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
    'Crawler_name':'HITACHI_ABB',
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

def Parser(source,localDb,localCollectionName):
    start=0
    request=requests.get(source)
    data=json.loads(request.content)
    All_news=data['results']
    scraped_news=[]
    for news in All_news:
        try:
            title=news['title'].strip()
        except:
            title=''
        try:
            url=news['url']
            if('http' not in url):
                url='https://www.hitachiabb-powergrids.com/'+url
        except:
            url=''
        if(url != ''):
            status=check_link_exists(url,localDb,localCollectionName)
            if(status):
#                 print ('exist')
                break
            else:        
                try:
                    date=dateparser.parse(news['date'])
                except:
                    date=''
                try:
                    typee=news['tagValue']
                except:
                    typee=''
                news_req=requests.get(url)
                soup1=BeautifulSoup(news_req.content,'lxml')
                try:
                    announcement=''
                    announcement+=(soup1.find('main',class_='container responsivegrid').find('div',class_='cmp-container').find('div',class_='cmp-quote').text.strip())
                    paragraphs=(soup1.find('div',id='container-40e845ead3').find_all('div',class_='text aem-GridColumn aem-GridColumn--default--12'))
                    for para in paragraphs:
                        announcement=announcement+' '+para.text.strip()
                except:
                    announcement=''
                try:
                    location=soup1.find('main',class_='container responsivegrid').find('div',class_='cmp-container').find('div',class_='cmp-newsinfo').find_all('span')[1].text.strip()
                except:
                    location=''
                all_images=[]
                try:
                    for img in soup1.find('main',class_='container responsivegrid').find('div',class_='cmp-container').find_all('img'):
                        image= (img.get('src'))
                        if('http' not in image):
                            image='https://www.hitachiabb-powergrids.com'+ image
                            if(len(image)>130):
                                all_images.append(image)
                except:
                    pass
                try:
                    video=(soup1.find('main',class_='container responsivegrid').find('div',class_='cmp-container').find('iframe').get('src'))
                    if('http' not in video ):
                        video=''
                    if('autoplay' not in video):
                        if('youtube' not in video):
                            video=''
                except:
                    try:
                        video =(soup1.find('main',class_='container responsivegrid').find('div',class_='cmp-container').find('a',class_='cmp-image__link').get('href'))
                        if('http' not in video ):
                            video=''
                        if('autoplay' not in video):
                            if('youtube' not in video):
                                video=''
                    except:
                        video=''

                NewsData= {}
                NewsData['companyId'] = ''
                NewsData['location']=location
                NewsData['comment']=''
                NewsData['Date']=date
                today=datetime.today()
                NewsData['Crawled_on']=today
                NewsData['title']=title
                NewsData['Language']= 'English'
                NewsData['announcementType']=typee

                NewsData['Source'] = source
                NewsData['News_Weblink'] = url
                NewsData['photo']= all_images
                NewsData['videos']= video

                NewsData['announcement']=announcement
                NewsData['historySubCategory']=typee

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
                scraped_news.append(NewsData)
                
        start+=1
      
  
    
    if(len(scraped_news)>0):
        localDb.get_collection(localCollectionName).insert_many(scraped_news)
    log_obj['Running_sequance'].append(str(len(scraped_news))+ " new news inserted in db.")
                       
        
if __name__ == "__main__":    
    try:
        file = open("/home/emr/config.json")
        data = json.load(file)
        db_path = data[0]['Db_Path']
        key = db_path
        # key='mongodb://su-du-ad:updatedSuperDuperAdmin@18.156.208.71:27017/emrweb?authSource=admin'
        dbName='TEMP_EMR_NEWS_Crawler_DB'
        collectionName='HITACHI_ABB'
#         key='mongodb://localhost:27017/'
#         dbName='Hitachiabb'
#         collectionName='news_test'
        url='https://www.hitachiabb-powergrids.com/content/pg/www/en/news/all-news/jcr:content/root/container/newslist.L2NvbnRlbnQvcGcvd3d3L2VuL21lZGlhL2pjcjpjb250ZW50L3Jvb3QvY29udGFpbmVyL2NvbnRhaW5lci9uZXdzbGlzdA==.list.json?page=0'
        Client=CreateDbConnection(key)
        db =  Client[dbName]
        Parser(url,db,collectionName)
        
        log_collection = Client['Logs_DB']['Logs_TEMP_EMR_NEWS_Crawler_DB']
        log=copy.deepcopy(log_obj)
        log['Ending_time']=datetime.now()
        log_collection.insert_one(log)
    except:
        log_collection = Client['Logs_DB']['Logs_TEMP_EMR_NEWS_Crawler_DB']
        rep = traceback.format_exc()
        log=copy.deepcopy(log_obj)
        log_obj['Running_sequance'].append(rep)
        log['Ending_time']=datetime.now()
        log_collection.insert_one(log)