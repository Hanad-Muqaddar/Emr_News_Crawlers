# Packages to be imported
import requests

import time

import json

from random import randint

from bs4 import BeautifulSoup

from pymongo import MongoClient

from bs4 import BeautifulSoup

from selenium import webdriver

# from webdriver_manager.chrome import ChromeDriver

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support import expected_conditions

from selenium.webdriver.common.by import By

from urllib.parse import urlparse

import re

import traceback

import urllib

import dateparser

from datetime import datetime

from bson.objectid import ObjectId

from urllib.error import HTTPError

from urllib.request import Request, urlopen

from newspaper import fulltext

from scrapy import Selector
import unicodedata
# ************************************************************************
# defining variables

running_Sequence = []

started_on = datetime.now()

# c_name = 'SIEMENS_Testing' # Name of the Collection
c_name = 'SIEMENS' # Name of the Collection

total_crwalled_links = 0

Already_exist = 0

# *************************************************************************

# trying to connect with mongodb

try:

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

    running_Sequence.append('Fresh Starting News Crawler on -> ' + str(datetime.now()))

    Crwl_time = datetime.now()

else:

    last_time = last_insertion['Date']

    running_Sequence.append('Last News Crawled on -> '+str(last_insertion['Date'].date()))

    Crwl_time = last_insertion['Date']

def parse_filtered_news(announcement):
    api_url = "https://admin.dev.emr-online.com/api/history/filterbody"
    # api_url = "http://192.168.60.105:3000/api/history/filterbody"
    payload = json.dumps({
                            "originalBody": announcement
                            })
    headers = {
                'Content-Type': 'application/json'
                }
    return_response = requests.request("POST", api_url, headers=headers, data=payload)
    new_data = return_response.text
    new_data = json.loads(new_data)
    status = new_data['statusCode']
    if status == 200:
        return new_data
    else:
        new_data =  ""
        return new_data

# ****************************************************************************

####################################################

############# Every Company Logic Here #############

####################################################

# *****************************************************************************
try:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}
    Main_url = "https://press.siemens.com"
    Base_url = "https://press.siemens.com/global/en/press-search"
    result = requests.get(Base_url,headers=headers)
    soup = BeautifulSoup(result.content , 'lxml')
    
    news_links = []

    links = soup.find_all("div", {"class" : re.compile('press-search-results-view-row')})
    for link in links:
        news_link = Main_url + link.find('div',{ "class" : "views-field views-field-title"}).find('a').get('href')
        if news_link not in news_links:
            news_links.append(news_link)
    # print(news_links)
    for i in news_links:
        response = requests.get(i, headers=headers)
        data = BeautifulSoup(response.content, 'lxml')
        res = Selector(response)
        try:
            title = data.find('meta',attrs = {'name':'og:title'}).get('content')
            # print(title)
        except:
            title = ""
        
        announcement_type = "Press Release"
        language = "en-us"

        try:
            image = data.find('meta',attrs = {'name':'og:image'}).get('content')
            # print(image)
        except:
            image = ""

        try:
            sub_category = data.find('meta', attrs = {"name":"og:type"}).get("content")
            # print(sub_category)
        except:
            sub_category = ""
        
        try:
            analysis = data.find('meta', attrs = {"name":"og:description"}).get("content")
            # print(analysis)
        except:
            analysis = ""
        try:            
            date = data.find('span', {"class":"Date"}).get("data-original")
            # print(date)
            news_date = dateparser.parse(date,  settings={'DATE_ORDER': 'MDY'} )
            # print(news_date)            
        except:
            news_date = ""

        page_source = "https://press.siemens.com/global/en/press-search"
        news_weblink = i
        
        try:
            annc = res.css(".c2-ct-press-release").get()
            replace1 = res.css(".nts-notifications").get()
            replace2 = res.xpath("//section[@class='MetaData Press Release container']").get()
            replace3 = res.xpath("//h1").get()
            replace4 = res.css(".mobile-summary").get()
            replace5 = res.css(".mobile-Introtext").get()
            replace6 = res.css(".MetaData").get()
            replace7 = res.css(".nts-primary-teaser-slide-box-container").get()
            replace8 = res.css(".addeventatc").get()
            replace9 = res.css(".content .hidden-sm").get()
            replace10 = res.css(".fsi-row-sm-level h1").get()
            replace11 = res.xpath("//div[@class='col col-xs-12 col-sm-12 col-md-6']").get()
            replace12 = res.css(".hasVideo").getall()
            replace14 = res.css(".nts-notifications").get()
            replace15 = res.css(".Contact").get()
            replace16 = res.css(".slick-list").get()
            replace17 = res.xpath('//section[contains(@class, "VisibleCols3")]//div[not (contains (@class, "noPic")) and contains(@class, "caption")]').getall()
            replace18 = res.xpath('//section[contains(@class, "VisibleCols1")]//div[not (contains (@class, "noPic")) and contains(@class, "caption")]').getall()
            replace30 = res.xpath('//section[contains(@class, "VisibleCols2")]//div[not (contains (@class, "noPic")) and contains(@class, "caption")]').getall()
            replace19 = res.xpath('//section[@class="container Row"]//div[@class="col-md-12"]').get()
            replace20 = res.css(".filterResults").get()
            replace21 = res.css(".footer").get()
            replace22 = res.css(".RelatedRow").get()
            replace23 = res.css(".Boilerplate").getall()
            
            for video in replace12:
                try:
                    annc = annc.replace(video, "")
                except:
                    pass
            for caption in replace17:
                try:
                    annc = annc.replace(caption, "")
                except:
                    pass
            for caption1 in replace18:
                try:
                    annc = annc.replace(caption1, "")
                except:
                    pass
            for caption2 in replace30:
                try:
                    annc = annc.replace(caption2, "")
                except:
                    pass
            for boiler in replace23:
                try:
                    annc = annc.replace(boiler, "")
                except:
                    pass
                 
            try:
                annc = annc.replace(replace1,"")
            except:
                pass
            try:
                annc = annc.replace(replace2, "")
            except:
                pass
            try:
                annc = annc.replace(replace3,"")
            except:
                pass
            try:
                annc = annc.replace(replace4,"")
            except:
                pass
            try:
                annc = annc.replace(replace5,"")
            except:
                pass
            try:
                annc = annc.replace(replace6, "")
            except:
                pass
            try:
                annc = annc.replace(replace7, "")
            except:
                pass
            try:
                annc = annc.replace(replace8,"")
            except:
                pass
            try:
                annc = annc.replace(replace9,"")
            except:
                pass
            try:
                annc = annc.replace(replace10,"")
            except:
                pass
            try:
                annc = annc.replace(replace11,"")
            except:
                pass
            try:
                annc = annc.replace(replace12,"")
            except:
                pass
            try:
                annc = annc.replace(replace14,"")
            except:
                pass
            try:
                annc = annc.replace(replace15,"")
            except:
                pass
            try:
                annc = annc.replace(replace16,"")
            except:
                pass
            # try:
            #     annc = annc.replace(replace17,"")
            # except:
            #     pass
            try:
                annc = annc.replace(replace19,"")
            except:
                pass
            try:
                annc = annc.replace(replace20,"")
            except:
                pass
            try:
                annc = annc.replace(replace21,"")
            except:
                pass
            try:
                annc = annc.replace(replace22,"")
            except:
                pass
            annc = annc.replace("<!--[isInTeaser: true][maxLength: 130][hasImage: true][shortenList:true]-->", "")
            annc = annc.replace("<!--[isInTeaser: false][maxLength: ][hasImage: false][shortenList:false]-->", "")
            annc = annc.replace("<!--[isInTeaser: false][maxLength: ][hasImage: false][shortenList:false]-->", "")
            annc = annc.replace("<!--[isInTeaser: false][maxLength: ][hasImage: true][shortenList:false]-->", "")
            annc = annc.replace("<!--[isInTeaser: false][maxLength: ][hasImage: true][shortenList:false]-->", "")
            annc = annc.replace("<!--[isInTeaser: false][maxLength: ][hasImage: true][shortenList:false]-->", "")
            annc = annc.replace("<!--[isInTeaser: false][maxLength: ][hasImage: false][shortenList:false]-->", "")
            annc = annc.replace("<article xmlns:php=\"http://php.net/xsl\"><section data-partialxcmsid=\"\"><span><!--[isInTeaser: false][maxLength: ][hasImage: false][shortenList:false]-->", "")
            
            return_data = parse_filtered_news(annc)
            annc = return_data['filteredBody']
            emr_essentail = return_data['emrEssential']
            emr_executive = return_data['emrExecutive']
            emr_lite = return_data['emrLite']
            emr_html = return_data['emrHtmlText']
        except Exception as e:
            print(e)
            annc = ""
            emr_essentail = ""
            emr_executive = ""
            emr_lite = ""
            emr_html = ""
        
        date = datetime.now()
        # Creating a list of links already avilable in database
        links_list = []
        mydoc = collection.find()
        for x in mydoc:
            links_list.append(x['News_Weblink'])

        if news_weblink in links_list:
            total_crwalled_links += 1
            Already_exist += 1
            continue
        else:
            company_news = {}
            company_news['companyId'] = ''
            company_news['location']=''
            company_news['comment']=''
            company_news['Date']= news_date
            company_news['Crawled_on']=date
            company_news['title']=title
            company_news['Language']= language
            company_news['announcementType']= announcement_type
            company_news['Source'] = page_source
            company_news['News_Weblink'] = news_weblink
            company_news['photo']= image
            company_news['videos']= ''
            company_news['announcement']=annc
            company_news['historySubCategory']= sub_category
            company_news['analysis'] = analysis
            company_news['emrExecutive'] = emr_executive
            company_news['emrEssential'] = emr_essentail
            company_news['emrLite'] = emr_lite
            company_news['News_Html'] = emr_html
            try:
                collection.insert_one(company_news)
                total_crwalled_links += 1
            except Exception as e:
                print(e)
                running_Sequence.append(e)
    
    if Already_exist >= 1:

        tmp_txt = ' , from which '+str(Already_exist) +' Links were Already Crawled '

    else:

        tmp_txt = ''

    running_Sequence.append(str(total_crwalled_links) + ' Links are crawled ' + tmp_txt)

    ended_on = datetime.now()
except:
    Error_Time =  datetime.now()

    Reported_Error = traceback.format_exc()


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

log['Browser'] = 'None'

# error_logs.insert_one(log)
