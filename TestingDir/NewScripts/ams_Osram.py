# Packages to be imported
import requests

import time

from pymongo import MongoClient

from selenium import webdriver

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By

import traceback

import dateparser

from datetime import datetime

from newspaper import fulltext
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from scrapy import Selector

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
# defining variables

running_Sequence = []

started_on = datetime.now()

c_name = 'OSRAM' # Name of the Collection

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
try:

    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument('--profile-directory=Default')
    opts.add_argument("--lang=en")
    opts.add_argument("--enable-javascript")
    opts.add_argument("--enable-cookies")
    # opts.add_argument("--headless=new")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'}
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

    Main_url = "https://ams-osram.com"
    page_source = "https://ams-osram.com/news"
    
    driver.get(page_source)
    time.sleep(5)

    news_links = []
    N_dates = []
    links = driver.find_elements(By.XPATH, '//a[contains(@class,"news-card")]')
    for link in links:
        news_link = link.get_attribute('href')
        news_links.append(news_link)
        try:
            dat = link.find_element(By.XPATH, './/time').text
            N_dates.append(dat)
        except:
            dat = ""
            N_dates.append(dat)

    print(news_links)
    print(N_dates)
    print(len(N_dates))
    print(len(news_links))

    driver.close()

    db_list = []
    mydoc = collection.find()
    for x in mydoc:
        db_list.append(x['News_Weblink'])

    Emr_Crawlers_Logs(c_name, page_source,news_links)

    for i,d in zip(news_links,N_dates):
        if i in db_list:
            total_crwalled_links += 1
            Already_exist += 1
            print("Already Crawled")
            continue
        else: 
            result1 = requests.get(i, headers=headers)
            response1 = Selector(result1)       
            
            try:
                title = response1.xpath('//h1[@data-lfr-editable-id="title"]/text()').get()
                print(title)
            except:
                title = ""
            
            announcement_type = "News"
            language = "en-us"

            try:
                image = response1.xpath('//img[@class="image fullscreen"]/@src').get()
                print(image)
            except:
                image = ""

            try:
                Video = response1.xpath('//div[contains(@class,"video-container")]/iframe/@src').get()
                print(Video)
            except:
                Video = ""

            sub_category = ""
            
            try:
                analysis = response1.find('meta', attrs = {"property":"og:description"}).get("content")
            except:
                analysis = ""

            try:
                news_date = dateparser.parse(d,  settings={'DATE_ORDER': 'DMY'})
                print(news_date)
            except:
                news_date = ""

            
            news_weblink = i
            print(news_weblink)
            
            try:
                announcement = fulltext(response1.content)
                announcement = announcement.replace('\n','<br>')
                print(announcement)                
            except:
                announcement = ""
            
            date = datetime.now()
            # Creating a list of links already avilable in database
            
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
            company_news['videos']= Video
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
