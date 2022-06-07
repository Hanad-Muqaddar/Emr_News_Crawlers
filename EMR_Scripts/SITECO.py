import requests
import time
import json
from random import randint
from bs4 import BeautifulSoup
from pymongo import MongoClient
import traceback

from datetime import date, timedelta
from datetime import datetime
import dateparser
import copy
today = datetime.now()
running_sequence = []
started_on = datetime.now()

def CreateDbConnection(key,running_sequence):
    try:
        client= MongoClient(key)
        running_sequence.append('Connected to Server')
    except:
        running_sequence.append('Not Connected')
    return client

def check_link_exists(url,db,collection):
    ch=db.get_collection(collection).find({'News_Weblink':url})
    check=[]
    for x in ch:
        check.append(x)
    if(len(check)<=0):
        return False
    else:
        return True


def News_SinglePageParser(url,running_sequence):
    req = requests.get(url,verify=False)
    running_sequence.append('Getting News Link')
#     req = requests.get(url)
#     print ('1')
    soup = BeautifulSoup(req.content, 'lxml')
    NewsData ={}
    NewsData['companyId'] = '200000'
    NewsData['Date'] = ''
    NewsData['location']=''
    NewsData['announcementType'] = 'News'
    NewsData['Source'] = url
    NewsData['News_Weblink'] = url 
    try:
        NewsData['title'] = soup.find('figcaption', class_= 'slideshow__slide-overlay').get_text().strip()
    except:
        NewsData['title']=''
    try: 
        NewsData['announcement'] = soup.find('div', class_ = 'textmedia__text' ).get_text()
    except :
        NewsData['announcement'] = ''
        
    try:
        photo = 'https://www.siteco.com' + soup.find('img', class_ = 'slideshow__slide-image').get('src')
    except:
        photo=''
    NewsData['historySubCategory']=''
    refrences=''
    analysis=''
    # date_time=datetime.today()
    NewsData['photo']= photo
    NewsData['Language']= 'English'
    today=datetime.today()
    NewsData['Crawled_on']=today
    validatedObject  ={}
    validatedObject['companyId']=NewsData['companyId']
    validatedObject['Date']=NewsData['Date']
    validatedObject['title']=NewsData['title'] 
    validatedObject['announcement']=NewsData['announcement']
    validatedObject['announcementType']=NewsData['announcementType']
    
    validatedObject['photo']=photo
    validatedObject['analysis']=analysis
    validatedObject['refrences ']=refrences
    validatedObject['historySubCategory']= NewsData['historySubCategory']

    NewsData['validatedObject']=validatedObject
    return NewsData
def History_newsParser(news_url,localDb,localCollectionName,running_sequence):
    req = requests.get(url,verify=False)
#     req = requests.get(url)
    soup = BeautifulSoup(req.content, 'lxml')
    running_sequence.append('Getting News Link')
    NewsPageUrls = []
    all_news = []
    div =  soup.find('div',class_='main-content').find_all('div', class_ = 'block' )
    count=0
    for single in div:
        if(single.find('div',class_='row')):
            if(count>0):
                break
            for i in single:
                try:
                    new_url='https://www.siteco.com' + i.find('a', class_ =  'internal-link').get('href')
                    NewsPageUrls.append(new_url)
                    status=check_link_exists(new_url,db,collection)
                    if(status):
                        count+=1
#                         print ('exist')
#                         print ('*************')
                        break
                    else:
#                         print ("Not Exist in db")
                        data=News_SinglePageParser(new_url,running_sequence)
#                         print (data['title'])
#                         print ('*****************')
                        all_news.append(data) 
                except:
                    pass
        
        else:
            pass
    print(all_news)
    return all_news     
    
last_insertion = None
last_time = ''
Already_exist = 0
total_crwalled_links = 0
try:
    
#   -----------LocalNewsCrawler---------------
    file = open("/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/config.json")
    data = json.load(file)
    db_path = data[0]['Db_Path']
    key = db_path
    # key='mongodb://su-du-ad:updatedSuperDuperAdmin@18.156.208.71:27017/emrweb?authSource=admin'
    dbName='TEMP_EMR_NEWS_Crawler_DB'
    c_name='SITECO'
    url='https://www.siteco.com/en/company/news'
    
    Client=CreateDbConnection(key,running_sequence)
    db =  Client[dbName]
    collection = db[c_name]
    error_logs = Client['Logs_DB']['Logs_TEMP_EMR_NEWS_Crawler_DB']
    try:
        for l_i in collection.find().sort('Date', -1).limit(1):
            last_insertion = l_i
    except:
        # print('Fresh Starting News Crawler')
        last_insertion = None
    if last_insertion == None:
        running_sequence.append('Fresh Starting News Crawler on -> ' + str(datetime.now()))
        Crwl_time = datetime.now()
    else:
        last_time = last_insertion['Date']

    news_list = History_newsParser(url,db,c_name,running_sequence)
    
    for i in news_list:
        weblink = i['News_Weblink']
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
            i['Crawled_on'] = datetime.now()
            total_crwalled_links +=1
            collection.insert_one(i)
    if Already_exist >=1:
        tmp_txt = ' , from which '+str(Already_exist) +' Links were Already Crawled '
    else:
        tmp_txt = ''

    running_sequence.append(str(total_crwalled_links) + ' Links are crawled ' + tmp_txt)
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
log['Crawler_Runing Sequence'] = running_sequence if running_sequence else ''
log['Links_Skipped'] = Already_exist
log['Last_news_crawl_time'] = last_time
log['Browser'] = 'None'
error_logs.insert_one(log)
