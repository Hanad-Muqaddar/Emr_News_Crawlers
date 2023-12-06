# Packages to be imported
import requests

import time

import json

from random import randint

from bs4 import BeautifulSoup

from pymongo import MongoClient, response

from bs4 import BeautifulSoup

from selenium import webdriver

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support import expected_conditions

from selenium.webdriver.common.by import By

import re

import traceback

# import urllib

import dateparser

import datetime

from bson.objectid import ObjectId

from urllib.error import HTTPError

# from urllib.request import Request, urlopen

from scrapy import Selector

from newspaper import fulltext
import json
# from Emr_Crawlers_Optimization import Emr_Crawlers_Logs

# ================================================================================
# Comment these lines when you are running locally
import importlib.util
# Specify the absolute path to Emr_Crawlers_Optimization.py
module_path = '/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/Emr_Crawlers_Optimization.py'
# Load the module using the absolute path
spec = importlib.util.spec_from_file_location('Emr_Crawlers_Optimization', module_path)
Emr_Crawlers_Optimization = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Emr_Crawlers_Optimization)
Emr_Crawlers_Logs = Emr_Crawlers_Optimization.Emr_Crawlers_Logs
# ================================================================================

# ************************************************************************
# ************************************************************************
running_Sequence = []

started_on = datetime.datetime.now()

c_name = 'Solar' # Name of the Collection

total_crwalled_links = 0

Already_exist = 0

# *************************************************************************

# trying to connect with mongodb

try:
    # file = open("/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/config.json")
    # data = json.load(file)
    # db_path = data[0]['Db_Path']
    # client = MongoClient(db_path)

    client = MongoClient('mongodb://su-du-ad:updatedSuperDuperAdmin@18.156.208.71:27017/emrweb?authSource=admin') # Staging DB 

    running_Sequence.append('Connected to DB Server')

except:

    running_Sequence.append('Not Connected')

# *************************************************************************

client_name = 'TEMP_EMR_NEWS_Crawler_DB'

news =  client[client_name]

collection = news[c_name]

error_logs = client['Logs_DB']['Logs_TEMP_EMR_NEWS_Crawler_DB']

last_insertion = None

last_time = ''

# ****************************************************************************

try:

    for l_i in collection.find().sort('Date', -1).limit(1):

        last_insertion = l_i

except:

    last_insertion = None

if last_insertion == None:

    running_Sequence.append('Fresh Starting News Crawler on -> ' + str(datetime.datetime.now()))

    Crwl_time = datetime.datetime.now()

else:

    last_time = last_insertion['Date']

    running_Sequence.append('Last News Crawled on -> '+str(last_insertion['Date'].date()))

    Crwl_time = last_insertion['Date']

# ****************************************************************************

####################################################

############# Every Company Logic Here #############

####################################################

# *****************************************************************************

try:
    proxies_list = ['us-wa','fr','jp','au','de']
    import random
    p = random.choice(proxies_list)
    proxies = {'http': f"http://waleeProxy:Cheeta@1@de.proxymesh.com:31280",
            'https': f"http://waleeProxy:Cheeta@1@de.proxymesh.com:31280"}
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Connection': 'keep-alive',
        'RequestVerificationToken': 'cPbhP_CGvvxpZXUeKlnZD6QM2Nf_nNWnnKqX1PU5rzv3nM7vtZFANlnueAATRex8lcoCxeru7qTJJIKbPMlzID3MKQ6HxVJhVp8gKw6GCQ01:F6jEoko5JSsDknXVyIi7NerSPgLnY35c5rxEay2p_WbtkDJmT0bmsAevBoptINtrhRGI7vT1wOP7liZggool-BkvOOydmkrnZjDqgJDBR9Q1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        'Cookie': 'dtCookie=v_4_srv_4_sn_8C908CB5EE5E8CB6BF12AC3D14E0BD6D_perc_100000_ol_0_mul_1_app-3Aaf0660e728ed7fcc_1; .ASPXANONYMOUS=jiPB7dRoMwGOXU2oRVsooWNDrYaWae8lyhVizatyQRT2t0egv3Jp9KcIJrlwDb7hptVEzO8peSCfA9mHMH-YzTnEkJ1AK_vWb83tggFkzSVYPXKDfpUhb2ZPdJknAAoED0qzMEd8wbtJdJ5Z8rJtPw2; NSC_wt_qspe_qfqjxfc_iuuqt=ffffffff094e4c0345525d5f4f58455e445a4a42378b'
        }
    url = "https://www.solar.eu/api/news/"
    to_date = datetime.datetime.now()
    payload = json.dumps({
            "Language": "en",
            "FromDate": "2021-12-31T19:00:00.000Z",
            "ToDate" : str(to_date)
            })
    # response = requests.request("POST", url, verify=False, headers=headers, data=payload, proxies=proxies, timeout=20)
    response = requests.request("POST", url, headers=headers, data=payload, proxies=proxies, timeout=20, verify=False)

    data = json.loads(response.text)
    # print(data)
    db_list = []
    mydoc = collection.find()
    for x in mydoc:
        db_list.append(x['News_Weblink'])

    Web_Page = "https://www.solar.eu/investor/news/"
    Emr_Crawlers_Logs(c_name,Web_Page,data)
    
    for i in data:
        id = i['Id']
        news_web_link = f"https://www.solar.eu/investor/news/news-page/?pressId={id}&lang=en"
        print(news_web_link)
        
        if news_web_link in db_list:
            Already_exist += 1
            total_crwalled_links += 1
            print("Already Crawled")
            continue
        else:
            result1 = requests.get(news_web_link,proxies=proxies)
            response1 = Selector(result1)
            try:
                news_date = i['PublishedDateTime']
                news_date = dateparser.parse(news_date)
            except:
                news_date = ""
            try:
                title = i['Headline']
            except:
                title = ""
            try:
                analysis = i['TeaserText']
            except:
                analysis = ""
            try:
                image = response1.xpath("//meta[@property='og:image']/@content").get()
            except:
                image = ""
            sub_category = ""
            try:
                announcement = fulltext(result1.text)
                announcement = announcement.replace('\n','<br>')
            except:
                announcement = ""
            announcement_type = "News"
            language = "en"
            page_source = "https://www.solar.eu/investor/news/"
            crawled_date = datetime.datetime.now()

            company_news = {}
            company_news['companyId'] = ''
            company_news['location']=''
            company_news['comment']=''
            company_news['Date']= news_date
            company_news['Crawled_on']=crawled_date
            company_news['title']=title
            company_news['Language']= language
            company_news['announcementType']= announcement_type
            company_news['Source'] = page_source
            company_news['News_Weblink'] = news_web_link
            company_news['photo']= image
            company_news['videos']= ''
            company_news['announcement']=announcement
            company_news['historySubCategory']= sub_category
            company_news['analysis'] = analysis
            try:
                collection.insert_one(company_news)
                total_crwalled_links += 1
            except Exception as e:
                running_Sequence.append(e)
    
    if Already_exist >= 1:

        tmp_txt = ' , from which '+str(Already_exist) +' Links were Already Crawled '
    else:

        tmp_txt = ''

    running_Sequence.append(str(total_crwalled_links) + ' Links are crawled ' + tmp_txt)

    ended_on = datetime.datetime.now()
except Exception as e:
    print(e)
    Error_Time =  datetime.datetime.now()

    Reported_Error = traceback.format_exc()

    running_Sequence.append(e)


# **************************************************************************

# **************************************************************************

# **************************************************************************
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

log['Browser'] = 'Chrome'

error_logs.insert_one(log)
