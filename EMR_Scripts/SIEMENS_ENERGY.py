

import requests
import time
import json
from random import randint
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re
from datetime import date, timedelta
import datetime
import dateparser
import copy
from datetime import datetime
today = datetime.now()
import traceback
import sys
log_obj={
    'Crawler_name':'SIEMENS_ENERGY',
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

def Parser(mainSource,localDb,localCollectionName):
    scraped_news=[]
    source=mainSource
    links=[]
    flag=True
    while(flag):
        req=requests.get(source)
        soup=BeautifulSoup(req.content)
        news_divs=soup.find('div',class_='view-content').find_all('div',class_='press-search-results-view-row content-type-c2-ct-press-release views-row')
        for one in news_divs:
            links.append('https://press.siemens-energy.com'+one.find('a').get('href'))
        if(soup.find('ul',class_='js-pager__items pager')):
            source= ('https://press.siemens-energy.com/global/en/press-search'+soup.find('ul',class_='js-pager__items pager').find('a').get('href'))
#             print (source)
        else:
            flag=False
    source=mainSource
    for single_news_link in links:
        status=check_link_exists(single_news_link,localDb,collectionName)
        print (single_news_link)
        if(status):
#             print ('exist')
            break
        else:   
#             print ('not exist')
            response =  requests.get(single_news_link)
            try:
                mainDiv = BeautifulSoup(response.content,'lxml').find('div',class_='content')
            except:
                mainDiv=''
            if(mainDiv !=''):
                try:
                    info= (mainDiv.find('section',class_='MetaData Press Release container'))
                except:
                    info=''
                if(info != ''):

                    try:
                        typee= info.find('span',class_='txt').text.strip()
                    except:
                        typee=''
                    try:
                        date= dateparser.parse(info.find('span',class_='Date').text.strip())
                    except:
                        date=''
                    try:
                        catagory=info.find('span',class_='EditorExt').text.strip()
                    except:
                        catagory=''
                    try:
                        location=info.find('span',class_='Location').text.strip()
                    except:
                        location=''

                try:
                    paragraph= mainDiv.find('section',class_='Intro Press Release container').find('div',class_='Summary').find('ul').text.strip()
                except:
                    paragraph=''
                try:
                    for para in (mainDiv.find('section',class_='Intro Press Release container').find('div',class_='row IntroText')):
                        try:
                            paragraph=paragraph+ ' '+(para.text.strip())
                        except:
                            pass
                except:
                    pass


                try:
                    paragraph=paragraph+ ' '+mainDiv.find('section',class_='container Row').text.strip()
                except:
                    pass
                try:
                    related_links= ( mainDiv.find('section',class_='container Row VisibleCols3').find_all('ul',class_='link-list'))
                except:
                    related_links=''
                if(related_links != ''):
                    try:
                        downloads=[]
                        for li in related_links[0]:
                            d_link=li.find('a').get('href')
                            downloads.append(d_link)
                    except:
                        downloads=[]

                    try:
                        further_links=[]
                        for li in related_links[1]:
                            f_link=li.find('a').get('href')
                            if('http' not in f_link):
                                f_link='https:'+f_link

                            further_links.append(f_link)
                    except:
                        further_links=[]
                else:
                    further_links=[]
                    downloads=[]
                try:
                    images=[]
                    for section in (mainDiv.find_all('section',class_='container Row')):
                        try:
                            images.append(section.find('img').get('src'))
                        except:
                            pass
                except:
                    images=[]
                try:
                    title=mainDiv.find('h1').get_text()
                    print(title)
                except:
                    title=''
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
                NewsData['historySubCategory']=catagory
                NewsData['Source'] = source
                NewsData['News_Weblink'] = single_news_link
                NewsData['photo']= images
                NewsData['videos']= ''
                NewsData['further_links']= further_links
                NewsData['downloads']= downloads
                NewsData['announcement']=paragraph


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
    if(len(scraped_news)>0):
        localDb.get_collection(localCollectionName).insert_many(scraped_news)
    log_obj['Running_sequance'].append(str(len(scraped_news))+ " new news inserted in db.")
  
        
if __name__ == "__main__":  

    
    try:    
        # key='mongodb://localhost:27017/'
        # file = open("/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/config.json")
        # data = json.load(file)
        # db_path = data[0]['Db_Path']
        # key = db_path
        key='mongodb://su-du-ad:updatedSuperDuperAdmin@18.156.208.71:27017/emrweb?authSource=admin'
        dbName='TEMP_EMR_NEWS_Crawler_DB'
        collectionName='SIEMENS_ENERGY'
        url='https://press.siemens-energy.com/global/en/press-search?f%5B0%5D=content_type:c2_ct_press_release'

        Client=CreateDbConnection(key)
        db =  Client[dbName]
        log_collection = Client['Logs_DB']['Logs_TEMP_EMR_NEWS_Crawler_DB']
   
        Parser(url,db,collectionName)

        log=copy.deepcopy(log_obj)
        log['Ending_time']=datetime.now()
        # log_collection.insert_one(log)
    except:
        rep = traceback.format_exc()
        log=copy.deepcopy(log_obj)
        log_obj['Running_sequance'].append (rep)
        log['Ending_time']=datetime.now()
        # log_collection.insert_one(log)


# In[ ]:




