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


def single_news_parser(url,source):
    hist ={}
    req1 = requests.get(url)
    news_soup = BeautifulSoup(req1.content, 'lxml')
    news_parentDiv = news_soup.find('div',class_='detail-content')
    image=news_parentDiv.find('div',class_='twelve columns m04-top-image').find('img')
    try:
        image='https://www.hagergroup.com'+image['data-original']
    except:
        image=''
    try:
        d=(news_parentDiv.find('div',class_='detail-header').find('h4').text).strip().replace('.','-')
        tmp_d = d.split('-')
        tmp_d[len(tmp_d)-1] = "20"+tmp_d[len(tmp_d)-1]
        d = "-".join(tmp_d)
        date=dateparser.parse(d,settings={'DATE_ORDER': 'DMY'})
    except:
        date=''
    try:
        title=(news_parentDiv.find('div',class_='detail-header').find('h1').text).lstrip()
    except:
        title=''
    try:
        anouncement=news_parentDiv.find('div',class_='detail-content-inner').get_text()
    except:
        anouncement=''

    hist['comment']=''

    hist['companyId'] = '300000'
    hist['Date'] = date
    
    hist['photo']= image
    hist['Language']= 'English'
    today=datetime.today()
    hist['Crawled_on']=today
                
    hist['source'] = source
    hist['News_Weblink'] = url
    hist['historySubCategory']='Media'
    hist['announcementType'] = 'Press Release'
    hist['title']=title
    hist['announcement']=anouncement
    
    refrences=''
    analysis=''
    validatedObject  ={}
    validatedObject['companyId']=hist['companyId']
    validatedObject['Date']=date
    validatedObject['title']=title
    validatedObject['announcement']=hist['announcement']
    validatedObject['announcementType']=hist['announcementType']

    validatedObject['photo']=image
    validatedObject['analysis']=analysis
    validatedObject['refrences ']=refrences
    validatedObject['historySubCategory']= hist['historySubCategory']

    hist['validatedObject']=validatedObject
    return hist
def History_newsParser(news_url,localDb,localCollectionName,running_sequence):
    req = requests.get(news_url)
    running_sequence.append('Getting News Links')
    soup = BeautifulSoup(req.content, 'lxml')
    parentDiv = soup.find('div',class_='row isotope')
    urls=[]
    all_news = []
    url_count=0
    count=0
    for div in parentDiv:
        if(count>0):
            break
        
        try:  
            url='https://www.hagergroup.com'+div.find('div',class_='list-tile-link').find('a').get('href')
            status=check_link_exists(url,localDb,localCollectionName)
          
            if(status):
                count+=1
#                 print ('exist')
#                 print ('----------------')
                break
            else:
                urls.append(url)
                url_count+=1
#                 print (url_count)
#                 print (url)
#                 print ("Not Exist in db")
                
                hist=single_news_parser(url,news_url)
                all_news.append(hist) 
#                 print ('*****************')
        except:
            pass
    return all_news     
    
last_insertion = None
last_time = ''
Already_exist = 0
total_crwalled_links = 0
try:
    
#   -----------LocalNewsCrawler---------------
    file = open("/home/emr/config.json")
    data = json.load(file)
    db_path = data[0]['Db_Path']
    key = db_path
    # key='mongodb://su-du-ad:updatedSuperDuperAdmin@18.156.208.71:27017/emrweb?authSource=admin'
    dbName='TEMP_EMR_NEWS_Crawler_DB'
    c_name='HAGER'
    url='https://www.hagergroup.com/en/media/hager-group-press-releases/1024-6023.htm?backpageid=160&backblockid=b10655674&backblockanchor=pressrelease'
    
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
