# Packages to be imported
import requests

import time

import json

from random import randint

from bs4 import BeautifulSoup

from pymongo import MongoClient

from bs4 import BeautifulSoup

from newspaper import fulltext

import dateparser

from selenium import webdriver

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support import expected_conditions

from selenium.webdriver.common.by import By

from urllib.parse import urlparse

import traceback

import datetime


from bson.objectid import ObjectId

from urllib.error import HTTPError

from urllib.request import Request, urlopen

from selenium.webdriver.chrome.service import Service as ChromeService

from webdriver_manager.chrome import ChromeDriverManager

# ************************************************************************
# defining variables
opts = Options()
opts.add_argument("--window-size=190,100")
opts.add_argument("--disable-automation")
opts.add_argument("--no-sandbox")
opts.add_argument('--profile-directory=Default')
opts.add_argument("start-maximized")
opts.add_argument("disable-infobars")
opts.add_argument("--lang=en")
opts.add_argument("--enable-javascript")
opts.add_argument("--enable-cookies")
opts.headless = True

running_Sequence = []

started_on = datetime.datetime.now()

c_name = 'WAGO' # Name of the Collection

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

    # running_Sequence.append('Fresh Starting News Crawler on -> ' + str(datetime.datetime.now()))

    Crwl_time = datetime.datetime.now()

else:

    last_time = last_insertion['Date']

    # running_Sequence.append('Last News Crawled on -> '+str(last_insertion['Date'].date()))

    Crwl_time = last_insertion['Date']

# ****************************************************************************

####################################################

############# Every Company Logic Here #############

####################################################

# *****************************************************************************

try:
    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opts)
    # driver.get("https://www.wago.com/global/blog")
    # try:
    #     while True:
    #         button = driver.find_element_by_xpath("//span[@class='wg-button wg-button--primary']")
    #         button.click()
    #         time.sleep(5)
    # except Exception as e:
    #     running_Sequence.append(e)
    # data = driver.find_elements_by_xpath("//div[@class='wg-blog__wrapper']//div[@class='wg-blog']//div[@class='wg-blog__tile js-wg-blog-tile-vue']")

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
    Base_url = "https://www.wago.com/wagoapi/v2/global-wago/blog/Homepage/entries?lang=en_GG&articleTypes=ContentArticleInterviewPageTemplate,ContentArticleTopicPageTemplate,ContentArticleReferencePageTemplate,ContentArticleCompanyNewsPageTemplate,ContentArticlePracticalTipsPageTemplate,ContentArticleProductNewsPageTemplate&page=0"
    Main_url = "https://www.wago.com/global"
    page = requests.get(Base_url)
    json_result = page.json()
    news_links = []

    for data in json_result['entries']:
        
        link = Main_url + data['url']
        news_links.append(link)

    print(news_links)

    db_list = []
    mydoc = collection.find()
    for x in mydoc:
        db_list.append(x['News_Weblink'])

    for i in news_links:
        
        if i in db_list:
            total_crwalled_links += 1
            Already_exist += 1
            print("Already Crawled")
            continue
        else:
            
            response = requests.get(i, headers=headers)
            data = BeautifulSoup(response.content, 'lxml')
    
            try:
                title = data.find('h1', {"class":"wg-headline"}).find('div').next_sibling.strip()
                print(title)
            except:
                title = ""
            
            announcement_type = "News"
            language = "en-us"

            try:
                image = Main_url + data.find('article').find('img').get('src')
                print(image)
            except:
                image = ""

            try:
                sub_category = data.find('meta', attrs = {"property":"og:type"}).get("content")
            except:
                sub_category = ""
            
            try:
                analysis = data.find('meta', attrs = {"name":"description"}).get("content")
            except:
                analysis = ""
            try:
                date = data.find('span', {"class":"wg-headline__date"}).get_text(strip=True)
                print(date)
                news_date = dateparser.parse(date,  settings={'DATE_ORDER': 'DMY'})
                print(news_date)
            except:
                news_date = ""

            page_source = "https://www.wago.com/global/blog"
            news_weblink = data.find('meta', attrs = {"property":"og:url"}).get("content")
            print(news_weblink)
            
            try:
                announcement = fulltext(response.content)
                announcement = announcement.replace('\n','<br>')
                print(announcement)
            except:
                announcement = ""
            
            date = datetime.datetime.now()
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
            company_news['videos']= ""
            company_news['announcement']=announcement
            company_news['historySubCategory']= sub_category
            company_news['analysis'] = analysis
            try:
                collection.insert_one(company_news)
                total_crwalled_links += 1
            except Exception as e:
                running_Sequence.append(e)

            # try:
            #     date = i.find_element_by_class_name("wg-blog__tile-date").text
            # except:
            #     date = ""
            # try:
            #     announcement_type = i.find_element_by_class_name("wg-blog__tile-flag").text
            # except:
            #     announcement_type = ""
            # try:
            #     title = i.find_element_by_class_name("wg-blog__tile-head").text
            # except:
            #     title = ""
            # try:
            #     image = i.find_element_by_tag_name("img").get_attribute("src")
            # except:
            #     image = ""
            # try:
            #     announcement = i.find_element_by_class_name("wg-blog__tile-body").text
            # except:
            #     announcement = ""
            # try:
            #     news_weblink = i.find_element_by_tag_name("a").get_attribute("href")
            # except:
            #     news_weblink = ""
            # db_list = []
            # mydoc = collection.find()
            # for x in mydoc:
            #     db_list.append(x['News_Weblink'])
            
            # if news_weblink in db_list:
            #     total_crwalled_links += 1
            #     Already_exist += 1
            #     continue
            # crawled_on_date = datetime.datetime.now()
            # url = "https://www.wago.com/global/blog"
            # company_news = {}
            # company_news['companyId'] = ''
            # company_news['location']=''
            # company_news['comment']=''
            # company_news['Date']=date
            # company_news['Crawled_on']=crawled_on_date
            # company_news['title']= title
            # company_news['Language']= 'English'
            # company_news['announcementType']= announcement_type
            # company_news['Source'] = url
            # company_news['News_Weblink'] = news_weblink
            # company_news['photo']= image
            # company_news['videos']= ''
            # company_news['announcement']= announcement
            # company_news['historySubCategory']=''
            # try:
            #     collection.insert_one(company_news)
            #     total_crwalled_links += 1
            # except Exception as e:
            #     running_Sequence.append(e)
    
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

