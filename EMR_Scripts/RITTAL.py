# Packages to be imported
import requests

import time

import json

from random import randint

from bs4 import BeautifulSoup

from pymongo import MongoClient

from bs4 import BeautifulSoup

import traceback

import dateparser

import datetime

from urllib.request import Request, urlopen

from scrapy import Selector

from newspaper import fulltext

# ************************************************************************
running_Sequence = []

started_on = datetime.datetime.now()

c_name = 'RITTAL' # Name of the Collection

total_crwalled_links = 0

Already_exist = 0

# *************************************************************************

# trying to connect with mongodb

try:
    file = open("/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/config.json")
    data = json.load(file)
    db_path = data[0]['Db_Path']
    client = MongoClient(db_path)

    # client = MongoClient('mongodb://su-du-ad:updatedSuperDuperAdmin@18.156.208.71:27017/emrweb?authSource=admin') # Staging DB 
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
    result = requests.get("https://www.rittal.com/com-en/News")
    response = Selector(result)
    links = response.css(".teaser-headline a ::attr(href)").getall()
    Base_Link = "https://www.rittal.com"
    final_links = [Base_Link + link for link in links if "https" not in link]
    print(final_links)
    dates = response.css(".teaser-title ::text").getall()

    db_list = []
    mydoc = collection.find()
    for x in mydoc:
        db_list.append(x['News_Weblink'])

    for i, date in zip(final_links, dates):
        if i in db_list:
            Already_exist += 1
            total_crwalled_links += 1
            print("Already Crawled")
            continue
        else:
            result1 = requests.get(i)
            response1 = Selector(result1)
            try:
                news_date = dateparser.parse(date)
            except:
                news_date = ""
            try:
                title = response1.css(".detail-intro h1::text").get()
                print(title)
            except:
                title = ""
            try:
                analysis = response1.xpath("//meta[@name='description']/@content").get()
            except:
                analysis = ""
            try:
                image = response1.css(".image-wrapper img::attr(src)").get()
                if "https" not in image:
                    image = Base_Link + image
            except:
                image = ""
            sub_category = ""
            try:
                announcement = fulltext(result1.text)
                announcement = announcement.replace('\n','<br>')
            except:
                announcement = ""
            announcement_type = "News"
            language = "en-US"
            page_source = "https://www.rittal.com/com-en/News"
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
            company_news['News_Weblink'] = i
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

# error_logs.insert_one(log)
