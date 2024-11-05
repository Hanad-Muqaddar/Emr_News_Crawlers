import requests

from pymongo import MongoClient

from bs4 import BeautifulSoup

import traceback

import dateparser

import datetime

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

running_Sequence = []

started_on = datetime.datetime.now()

c_name = 'MERSEN'

total_crwalled_links = 0

Already_exist = 0

# *************************************************************************


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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'}
    result = requests.get("https://www.mersen.com/en/group/news-and-events", headers=headers)
    soup = BeautifulSoup(result.content, 'lxml')
    
    news_links = []
    news = soup.find_all('div' , class_ ="views-row")
    for n in news:
        n_link = "https://www.mersen.com" + n.find('a', class_='news__body__link').get('href')
        news_links.append(n_link)
    
    db_list = []
    mydoc = collection.find()
    for x in mydoc:
        db_list.append(x['News_Weblink'])

    page_source = "https://www.mersen.us/news-media/events-news" 
    Emr_Crawlers_Logs(c_name, page_source, news_links)
    
    for j in news_links:
        if j in db_list:
            total_crwalled_links += 1
            Already_exist += 1
            print("Already Crawled")
            continue
        else:
            res = requests.get(j,headers=headers)
            soup = BeautifulSoup(res.content, 'lxml')
            try:
                title = soup.find("h1", class_="title").text
                print("\n", title)
            except:
                title = ""
            try:
                analysis = soup.find("meta", attrs={"name":"description"}).get("content")
                print(analysis)
            except:
                analysis = ''
            try:
                image = soup.find("meta", attrs={"property":"og:image"}).get("content")
                print(image)
            except:
                image = ""
            try:
                announcement_type = "News"
                print(announcement_type)
            except:
                announcement_type = ''
            try:
                announcement = soup.find('div', class_="field--name-field-paragraphs").find('div', class_='field__item').text.replace("\n", "<br/>").strip()
                print(announcement)
            except:
                announcement = ""
            
            page_source = "https://www.mersen.us/news-media/events-news"
            
            language = "en"
            
            crawled_date = datetime.datetime.now()
            
            news_weblink = j
            
            try:
                news_date = soup.find('div', class_="field--name-field-dates").find("time").text
                news_date = dateparser.parse(news_date)
                print(news_date)
            except:
                news_date = ""
            
            sub_category = ""
            
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
            company_news['News_Weblink'] = news_weblink
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
    print(Reported_Error)
    running_Sequence.append(e)

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

