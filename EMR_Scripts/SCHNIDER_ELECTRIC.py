import requests
import time
import json
from random import randint
from bs4 import BeautifulSoup
from pymongo import MongoClient
import traceback
import re
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


def News_SinglePageParser(image_url,running_sequence):
    url=image_url[1]
    req = requests.get(url)
    running_sequence.append('Getting News Links')
    soup = BeautifulSoup(req.text , 'lxml')
    # allNews = soup.find_all('div', class_= 'sdl-wiztopic-press-releases_wiztopic-card')
    
    
    NewsData= {}
    NewsData['companyId'] = ''
    try:
        NewsData['location'] = soup.find('div', class_ ='sdl-wiztopic-press-release_publication-data').find_all('span')[0].get_text().strip()
    except:
        NewsData['location']='' 
    try:
        d = soup.find('div', class_ ='sdl-wiztopic-press-release_publication-data').find_all('span')[1].get_text().strip()
        NewsData['Date']=dateparser.parse(d,settings={'DATE_ORDER': 'DMY'})
    except:
        NewsData['Date']=''
    NewsData['Source'] = url
    
    try:
        title = soup.find('h1', class_ = 'se-font-title3 se-color-life-green').get_text().strip()
    except:
        title=''
    try:
        NewsData['announcement'] = soup.find('div', class_ = 'wiztopic-rich-text').get_text()
    except:
        NewsData['announcement']=''
        
    NewsData['historySubCategory']=''
    NewsData['News_Weblink'] = url
    NewsData['comment']=''
    NewsData['title']=title
    NewsData['announcementType']='News & Press Releases'
    photo = image_url[0]
    
    NewsData['photo']= photo
    NewsData['Language']= 'English'
    today=datetime.today()
    NewsData['Crawled_on']=today
                
                
    refrences=''
    
    analysis=''
    validatedObject  ={}
    validatedObject['companyId']=NewsData['companyId']
    validatedObject['Date']=photo
    validatedObject['title']=NewsData['title']
    validatedObject['announcement']=NewsData['announcement']
    validatedObject['announcementType']=NewsData['announcementType']
    
    validatedObject['photo']=photo
    validatedObject['analysis']=analysis
    validatedObject['refrences ']=refrences
    validatedObject['historySubCategory']= NewsData['historySubCategory']

    NewsData['validatedObject']=validatedObject 
    return NewsData
def Find_url(string): 
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,string)       
    return [x[0] for x in url] 

def find_img_url(urlsNews):
    gotAllNews = []
    for i in urlsNews :
        header = {
                'authority': 'www.se.com',
                'path': '/ww/en/about-us/newsroom/news/'+i,
                'scheme': 'https',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'cookie': 'SDLSESSID=C7D892B69668BD8E45F178A7F822B904; DYN_USER_ID=2159805236; DYN_USER_CONFIRM=ec53b26846982ac8fa8248b1ea6728a7; AWSELB=A9D3D3CF18851E073A4EDC85449131241AFDCA2F6C04D69B3B5321A66DA00B2AAED93127BC34A2BB111584C28C4E954CB868C81C46AEBB2E402658FD379956A44595B485609ED788B0CEC8A51C1B3B1B29A28B5EBC; PESV2_Cart_en_US=0; PESV2_Cart_B2C_en_US=0; tCdebugLib=1; TCPID=1214412241610610252536; TC_PRIVACY=0@003@2%2C4%2C3@1@1619681058637@; TC_PRIVACY_CENTER=2%2C4%2C3; _ga=GA1.3.1785555300.1619681059; _mkto_trk=id:178-GYD-668&token:_mch-se.com-1619681059322-49512; _cs_c=0; _gcl_au=1.1.1324497228.1619681060; AKA_A2=A; se_user_type=anonymous; bm_mi=A8C06C814221F6B96EC1BD38E8AC68E5~kDH/H7TSaoemKijChsznC3Qvgb5tYONGilMxCypClHvIbixwCaga8rHWA6oJhIz1jvxWTnuPyOxg2KmhlRnqb0H7O04B+2RI+MBR4uoKcyFW8GKfrOXgBgav+5gSlmvtD+oH6fCN+rpSLlrRaLv/eERXLlqLTEevQpv+Qk5tez80LycPabgmH8SWonSEyrh4Ot5eUjVRyPCX+4ZTmCqiUt4tq9soUVIyhREln374tIzqxTiD4RujQrhUIR3bBIxI0R68LJXdf5W0rsNIeI3HX/1J0prWvEHFxw9qGTj7GlrL8jy09lA6TdE5Gzf0vjW6aAg3MmFTngqqQe6tAKOjChuFV0nv802+zaXiXoUc9Q7nhNKanGzIeB16OVnr9L6ndgEizdI3mwMp3+qSEc/fhFZZD0IRg0971C1d7ydZyJP0AlLaNhrAgiW4bBLmDoCmvpUfgYKIlt4o/HhnOBe6tg==; ak_bmsc=79BCD4DDA16F7F6863EEC9E66DAE475C02179B1CCC6F000042669460DC8E5073~pl4KEmNLZ6ksNPRo9LEAKfRim7lbX2uacyGTcuywnrug8S8tDdIXqhwpe1xuARJRHZCd2tNdq50xj7L1Zbine/KAy9ku+KZViAIZ2ckZSrNsS9v8bfG8a0pY9QMneTW38TleiIl1uIxAOGSspXOO+k7ylK2FsNx2F+5uJvE9MX9sJPldeA9ttojUEg7FPOrQl4+3WuUF41xIjFm1+Doa7OaJt6r97Nd4MmhSPH7KcgFBePURzgl3Z7dpIjlKTImAF8; _gid=GA1.3.250970333.1620338252; kampyle_userid=cf77-6f2f-77ca-20b9-bcb8-5ca5-c414-98c6; mdigital_alternative_uuid=7582-a9f8-d703-76de-d4b5-cd3d-9854-ae3a; cd_user_id=17943afb103469-02790b82f7c165-d7e1739-100200-17943afb1043f7; LAST_INVITATION_VIEW=1620338385836; PESV2SESSID=zYlD9XxA2uI7SxvRi1CuhNw3.prd_PESstore01-1; _gat_statTracker=1; drift_campaign_refresh=2cb48c33-bb5b-42bb-9cc5-83180ab07e40; JabmoSP0ses.d8e0=*; drift_aid=23bab307-8885-42b6-9671-b142d662cbdc; driftt_aid=23bab307-8885-42b6-9671-b142d662cbdc; RT="z=1&dm=se.com&si=3j4ypsnxt8t&ss=kodfk1zc&sl=0&tt=0"; _cs_id=e59ef4a0-1ad2-a7c8-f435-129b905d53b3.1619681059.2.1620338498.1620338251.1.1653845059893.Lax.0; _cs_s=6.5; bm_sv=F5E2ADA01C9F6D8DFD8FA34921BB9E13~S9xs5n6LjfP1vMojaH7JnG/qCSAhYitDyquEzd4XLtw4pPixH9TvePDViXFfQfQDgBfNkf5NXbQ4owh7VAh3zGUdey0uDvkr+WchCvwgzhJ0WCJjFBRnN0rRvHD8ZakvbJabXBiP7zaz8LrfaQRqBpfW9feq9/qJbCEZYWFV/KQ=; kampyleUserSession=1620338500668; kampyleUserSessionsCount=5; kampyleSessionPageCounter=1; kampyleUserPercentile=45.65376773646612; kampylePageLoadedTimestamp=1620338500707; JabmoSP0id.d8e0=f7c41307-812a-4e7d-a3cb-69b562dbac52.1620338490.1.1620338501.1620338490.8e2971af-abc2-4043-ad3c-b3644da74980',
                'referer': 'https://www.se.com/ww/en/about-us/newsroom/news/',
                'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
                }


        tmp_url = 'https://www.se.com/ww/en/about-us/newsroom/news/'+i
        req = requests.request("GET", tmp_url, headers=header)
        soup = BeautifulSoup(req.content, 'lxml')
        mainDiv = soup.find_all('div' , class_ = 'sdl-wiztopic-press-releases_wiztopic-card se-col-lg-4 se-col-sm-6')

        for j in mainDiv:
            img_url=[]
            img=j.find('div',class_='background-image')
            im=Find_url(str(img))
            im=str(im).strip("[']")
            img_url.append(im)
            img_url.append('https://www.se.com' +(j.find('div', class_='learn-more se-font-text3-0 se-color-sky-blue').find('a').get('href')))
            gotAllNews.append(img_url)
    return gotAllNews

def History_newsParser(news_url,localDb,localCollectionName,running_sequence):
    # urlsNews = ['https://www.se.com/us/en/about-us/newsroom/news/?skip=0',
    #         'https://www.se.com/us/en/about-us/newsroom/news/?skip=9',
    #         'https://www.se.com/us/en/about-us/newsroom/news/?skip=18',
    #         'https://www.se.com/us/en/about-us/newsroom/news/?skip=27',
    #        'https://www.se.com/us/en/about-us/newsroom/news/?skip=36']
    urlsNews = ['?skip=0','?skip=9','?skip=18','?skip=27','?skip=36']            
    gotAllNews=find_img_url(urlsNews)
    all_news=[]
    count=0
    for img_url in gotAllNews:
        url=img_url[1]
        status=check_link_exists(url,localDb,localCollectionName)
        count+=1
        if(status):
            
#             print ('exist')
#             print ('*************')
            break
        else:
#             print ("Not Exist in db")
            
            data=News_SinglePageParser(img_url,running_sequence)
#             print (data['title'])
#             print ('*****************')
            all_news.append(data)
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
    c_name='SCHNIDER_ELECTRIC'
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
# error_logs.insert_one(log)
