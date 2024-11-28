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
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
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
from scrapy import  Selector 
# from Emr_Crawlers_Optimization import Emr_Crawlers_Logs

# # ================================================================================
# Comment these lines when you are running locally
import importlib.util
# Specify the absolute path to Emr_Crawlers_Optimization.py
module_path = '/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/Emr_Crawlers_Optimization.py'
# Load the module using the absolute path
spec = importlib.util.spec_from_file_location('Emr_Crawlers_Optimization', module_path)
Emr_Crawlers_Optimization = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Emr_Crawlers_Optimization)
Emr_Crawlers_Logs = Emr_Crawlers_Optimization.Emr_Crawlers_Logs
# # ================================================================================

# ************************************************************************
# defining variables

running_Sequence = []

started_on = datetime.now()

c_name = 'RS_Components' # Name of the Collection

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

# ****************************************************************************

####################################################

############# Every Company Logic Here #############

####################################################

# *****************************************************************************
def parse_filtered_news(announcement):
    api_url = "https://admin.new.emr-online.com/api/history/filterbody"
    payload = json.dumps({"originalBody": announcement})
    headers = {'Content-Type': 'application/json'}
    return_response = requests.request("POST", api_url, headers=headers, data=payload)
    new_data = return_response.text
    new_data = json.loads(new_data)
    status = new_data['statusCode']
    if status == 200:
        return new_data
    else:
        new_data =  ""
        return new_data

try:
    opts = Options()
    opts.add_argument("--window-size=1080,1920")
    opts.add_argument("--disable-automation")
    opts.add_argument("--no-sandbox")
    opts.add_argument('--profile-directory=Default')
    opts.add_argument("--lang=en")
    opts.add_argument("--enable-javascript")
    opts.add_argument("--enable-cookies")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    driver.maximize_window()
    
    Main_url = "https://www.rsgroup.com" 
    Base_url = "https://www.rsgroup.com/newshub/" 
    driver.get(Base_url)
    time.sleep(5)
    
    news_links = []
    soup = BeautifulSoup(driver.page_source , 'lxml')
    section = soup.find('section', class_="page-block page-newsroom__block page-newsroom__block--news")
    links = section.find_all('a', class_='h-cover')
    for link in links:
        news_link = Main_url + link.get('href')
        if news_link not in news_links:
            news_links.append( news_link) 
    print(news_links)
    
    db_list = []
    mydoc = collection.find()
    for x in mydoc:
        db_list.append(x['News_Weblink'])

    page_source = "https://www.rsgroup.com/newshub/" 
    Emr_Crawlers_Logs(c_name, page_source, news_links)
    
    for i in news_links:
        if i in db_list:
            total_crwalled_links += 1
            Already_exist += 1
            print("Already Crawled")
            continue
        else:        
            driver.get(i)
            time.sleep(3)
            data = BeautifulSoup(driver.page_source, 'lxml')
            response1 = Selector(text=driver.page_source)
            try:
                title = data.find('h1').get_text(strip=True)
                print(title)
            except:
                title = ""
            
            announcement_type = "News"

            language = "en-us"

            try:
                image = "https://www.rsgroup.com/" + data.find('picture', attrs = {'class': 'masthead__hero'}).find('img').get('src')
            except:
                image = ""

            try:
                sub_category = data.find('meta', attrs = {"property":"og:type"}).get("content")
            except:
                sub_category = ""
            
            try:
                analysis = response1.xpath('normalize-space(//div[@class="editor"]/p[1])').get()
            except:
                analysis = ""
            try:
                date = response1.xpath('normalize-space(//span[@class="masthead-article__date"])').get()
                news_date = dateparser.parse(date,  settings={'DATE_ORDER': 'YMD'} )
            except:
                news_date = ""

            
            news_weblink = i
            
            try:
                # announcement = data.find('div', {"class":"list-item-desc"}).get_text(strip=True)
                announcement = ''.join(response1.xpath('//div[@class="editor"]/p//text()').getall())
                announcement = announcement.replace("\n", "<br/>").replace("  ", " ")
                # return_data = parse_filtered_news(announcement)
                # announcement = return_data['filteredBody']
                # emr_essentail = return_data['emrEssential']
                # emr_executive = return_data['emrExecutive']
                # emr_lite = return_data['emrLite']
                # emr_html = return_data['emrHtmlText']
            except:
                announcement = ""
                # emr_essentail = ""
                # emr_executive = ""
                # emr_lite = ""
                # emr_html = ""
            
            date = datetime.now()
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
            company_news['announcement']=announcement
            company_news['historySubCategory']= sub_category
            company_news['analysis'] = analysis
            # company_news['emrExecutive'] = emr_executive
            # company_news['emrEssential'] = emr_essentail
            # company_news['emrLite'] = emr_lite
            # company_news['News_Html'] = emr_html
            try:
                collection.insert_one(company_news)
                total_crwalled_links += 1
            except Exception as e:
                running_Sequence.append(e)
            print(company_news)
    
    if Already_exist >= 1:

        tmp_txt = ' , from which '+str(Already_exist) +' Links were Already Crawled '

    else:

        tmp_txt = ''

    running_Sequence.append(str(total_crwalled_links) + ' Links are crawled ' + tmp_txt)

    ended_on = datetime.now()

except:
    
    Error_Time =  datetime.now()

    Reported_Error = traceback.format_exc()
    
    print(Reported_Error)

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
