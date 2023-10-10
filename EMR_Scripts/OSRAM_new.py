import requests
import time
import json
from random import randint
from bs4 import BeautifulSoup
from pymongo import MongoClient
from bs4 import BeautifulSoup
from requests import api
from selenium import webdriver
from urllib.parse import urlparse
import re
import traceback   
import pandas as pd
import time
import dateparser
from datetime import datetime,date, timedelta
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

running_Sequence = []
started_on = datetime.now()
c_name = 'OSRAM'
try:
    # file = open("/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/config.json")
    # data = json.load(file)
    # db_path = data[0]['Db_Path']
    # client = MongoClient(db_path)
    client= MongoClient('mongodb://su-du-ad:updatedSuperDuperAdmin@18.156.208.71:27017/emrweb?authSource=admin')
    running_Sequence.append('Connected to DB Server')
except:
    running_Sequence.append('Not Connected')
client_name = 'TEMP_EMR_NEWS_Crawler_DB'
news =  client[client_name]
collection = news[c_name]
error_logs = client['Logs_DB']['Logs_TEMP_EMR_NEWS_Crawler_DB']
last_insertion = None
last_time = ''
try:
    for l_i in collection.find().sort('Date', -1).limit(1):
        last_insertion = l_i
except:
    # print('Fresh Starting News Crawler')
    last_insertion = None
if last_insertion == None:
    running_Sequence.append('Fresh Starting News Crawler on -> ' + str(datetime.now()))
    Crwl_time = datetime.now()
else:
    last_time = last_insertion['Date']
    running_Sequence.append('Last News Crawled on -> '+str(last_insertion['Date'].date()))
    Crwl_time = last_insertion['Date']
total_crwalled_links = 0
Already_exist = 0

All_title_list = []
mydoc = collection.find()
for x in mydoc:
    All_title_list.append(x['title'].lower())

def parse_filtered_news(announcement):
    api_url = "https://admin.new.emr-online.com/api/history/filterbody"
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

try:
    Optimization_links = []
    ################ NEWS Release #####################################
    url = "https://9ps0m7duie-2.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%20(lite)%3B%20react%20(16.12.0)%3B%20react-instantsearch%20(5.7.0)%3B%20JS%20Helper%20(2.28.0)&x-algolia-application-id=9PS0M7DUIE&x-algolia-api-key=321a182fe8706b78ee3234b41c7b58f7"
    news_num = 10
    payload = json.dumps({
      "requests": [
        {
          "indexName": "prod_OSRAM_COM_en",
          "params": "query=&hitsPerPage="+str(news_num)+"&maxValuesPerFacet=200&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22content_type_keyword%22%2C%22dp_category%22%2C%22dp_applications%22%2C%22dp_technology%22%5D&tagFilters=&facetFilters=%5B%5B%22content_type_keyword%3ANews%22%5D%5D"
        },
        {
          "indexName": "prod_OSRAM_COM_en",
          "params": "query=&hitsPerPage="+str(news_num)+"&maxValuesPerFacet=200&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=content_type_keyword"
        }
      ]
    })
    headers = {
      'Content-Type': 'application/json'
    }
    resp = requests.request("POST", url, headers=headers, data=payload)
    newsData = resp.json()['results'][0]['hits']
    for j in newsData:
        # lowerTitle = j['dp_headline'].lower()
        Optimization_links.append(j['link'])
        l = False
        # for k in collection.find({ 'News_Weblink' : j['link']  , 'title' : lowerTitle}):
        for k in collection.find({ 'News_Weblink' : j['link']}):
            if k:
                l = True
                break
        
        if l:
            total_crwalled_links +=1
            Already_exist +=1
            print("Already Crawled")
            # print('\n'+news['Link']+'\nNews Already Exist in DB\n')        
        else:
            if j['dp_headline'] in All_title_list:
                Already_exist += 1
                total_crwalled_links += 1
                print('Title Already Exist')
                continue
            
            else:
                news = {}
                news["companyId"] = ""
                news["location"] = ""
                try:
                    resp = requests.get(j['link'])
                    sub_soup = BeautifulSoup(resp.content,'lxml')
                    response1 = Selector(resp)
                    date = date = sub_soup.find('div',class_='page-content').find('div',class_='text-wrapper').find('p',class_=False).text.strip().split('|')[0]
                    news['Date'] = dateparser.parse(date,settings={'DATE_ORDER': 'DMY'})
                except:
                    news['Date'] = datetime.now()
                try:
                    announcement = response1.xpath('//div[@class="page-content"]//div[@class="container"]').get()
                    replace1 = response1.css(".font-headline-teaser").get()
                    replace2 = response1.xpath("(//div[@class='text-wrapper']//p)[1]").get()
                    announcement = announcement.replace(replace1, "")
                    announcement = announcement.replace(replace2, "")
                    return_data = parse_filtered_news(announcement)
                    announcement = return_data['filteredBody']
                    emr_essentail = return_data['emrEssential']
                    emr_executive = return_data['emrExecutive']
                    emr_lite = return_data['emrLite']
                    emr_html = return_data['emrHtmlText']
                except:
                    announcement = ""
                    emr_essentail = ""
                    emr_executive = ""
                    emr_lite = ""
                    emr_html = ""
                
                news['title'] = j['dp_headline']
                news['announcementType'] = j['dp_category']
                news['announcement'] = announcement
                news['photo'] = j['src1_picture_stored_only']
                news['Language'] =  'English'
                news['Crawled_on'] = datetime.now()
                news['Source'] = "https://www.osram.com/cb/news/index.jsp"
                news['News_Weblink'] = j['link']
                news['historySubCategory'] = j['dp_subheadline']
                news['emrExecutive'] = emr_executive
                news['emrEssential'] = emr_essentail
                news['emrLite'] = emr_lite
                news['News_Html'] = emr_html
                validation_obj = {}
                validation_obj['companyId'] = news["companyId"]
                validation_obj['Date'] = news['Date']
                validation_obj['title'] = news['title']
                validation_obj['announcement'] = news['announcement']
                validation_obj['photo'] = news['photo']
                validation_obj['analysis'] = j['dp_text']
                validation_obj['refrences'] = ''
                validation_obj['historySubCategory'] = ''
                news['validatedObject'] = validation_obj
                
                total_crwalled_links +=1
                collection.insert_one(news)

    ################ Press Release #####################################
    # for i in range(211):
    #     url = 'https://www.osram-group.de/en/media/press-releases?page='+str(i)
    #     cookie = 'www-osram-group-de#lang=en; ASP.NET_SessionId=50yd5verhptjn1obsai3atlz; AWSALB=hGTE64M7vVwh8A8tlATVS11ULcaJMUUblFoT23lBq6xZn0JwNvrtlcbBQSfe7U2gtbHqfX0zLgY8sdvwvUOV+mm9d/a4QBBukMGDX91s/2Vw+/MO0UBrrnNHLACl; AWSALBCORS=hGTE64M7vVwh8A8tlATVS11ULcaJMUUblFoT23lBq6xZn0JwNvrtlcbBQSfe7U2gtbHqfX0zLgY8sdvwvUOV+mm9d/a4QBBukMGDX91s/2Vw+/MO0UBrrnNHLACl; __CookieConsentV200={"consent":{"necessaryCookie":true,"performanceCookies":true},"accepted":true,"euCheck":false}'
    #     headers = {
    #     'accept': 'text/html, */*; q=0.01',
    #     'accept-encoding': 'gzip, deflate, br',
    #     'accept-language': 'en-US,en;q=0.9',
    #     'cookie': cookie,
    #     'referer':'https://www.osram-group.de/en/media/press-releases',
    #     'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-fetch-dest': 'empty',
    #     'sec-fetch-mode': 'cors',
    #     'sec-fetch-site': 'same-origin',
    #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    #     'x-requested-with': 'XMLHttpRequest'}
    #     response = requests.request("GET", url, headers=headers)
    #     soup = BeautifulSoup(response.content,'lxml').find('div',class_='prContainer').find_all('div',class_='prItemWrapper row')
    #     skip_next = False
    #     for x in soup:
    #         link = "https://www.osram-group.de"+x.find('a').get('href')
    #         l = False
    #         for k in collection.find({ 'News_Weblink' : link }):
    #             if k:
    #                 l = True
    #                 skip_next = True
    #                 break
    #             else:
    #                 skip_next = False
    #         if l:
                
    #             total_crwalled_links +=1
    #             Already_exist +=1       
    #         else:
    #             news = {}
    #         news["companyId"] = ""
    #         news["location"] = ""
    #         try:
    #             resp = requests.request("GET", link, headers=headers)
    #             sub_soup = BeautifulSoup(resp.content,'lxml')
    #         except:
    #             sub_soup = None
    #         if sub_soup:
    #             try:
    #                 ann = sub_soup.find('div',class_='prContent').text.strip()
    #             except:
    #                 ann = ''
    #             try:
    #                 image = sub_soup.find('meta',attrs={'property':'og:image'}).get('content')
    #             except:
    #                 image = ''
    #             try:
    #                 date_value = dateparser.parse(sub_soup.find('meta',attrs={'itemprop':'datePublished'}).get('content')) if sub_soup.find('meta',attrs={'itemprop':'datePublished'}).get('content')!= None else ''
    #             except:
    #                 date_value = ''

    #         news['Date'] = dateparser.parse(x.get('id').replace('pr-',''),settings={'DATE_ORDER': 'DMY'}) if date_value == '' else date_value
    #         news['title'] = x.find(class_='titlePR').text.strip()
    #         news['announcementType'] = "Press Release"
    #         news['announcement'] = ann if ann != '' else x.find(class_='introPR').text[2:]
    #         news['photo'] = image
    #         news['Language'] =  'English'
    #         news['Source'] = "https://www.osram.com/cb/news/index.jsp"
    #         news['News_Weblink'] = link
    #         news['analysis'] = x.find(class_='introPR').text[2:]
    #         news['historySubCategory'] = ",".join([jj.text.strip() for jj in x.find_all('span',class_='addcomma')])
    #         news['Crawled_on'] = datetime.now()
    #         validation_obj = {}
    #         validation_obj['companyId'] = news["companyId"]
    #         validation_obj['Date'] = news['Date']
    #         validation_obj['title'] = news['title']
    #         validation_obj['announcement'] = news['announcement']
    #         validation_obj['photo'] = news['photo']
    #         validation_obj['analysis'] = news['analysis']
    #         validation_obj['refrences'] = ''
    #         validation_obj['historySubCategory'] = news['historySubCategory']
    #         news['validatedObject'] = validation_obj
    #     if skip_next == True:
    #         break

    
    Emr_Crawlers_Logs(c_name,Optimization_links)
    if Already_exist >=1:
        tmp_txt = ' , from which '+str(Already_exist) +' Links were Already Crawled '
    else:
        tmp_txt = ''

    running_Sequence.append(str(total_crwalled_links) + ' Links are crawled ' + tmp_txt)
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
log['Crawler_Runing Sequence'] = running_Sequence if running_Sequence else ''
log['Links_Skipped'] = Already_exist
log['Last_news_crawl_time'] = last_time
log['Browser'] = 'None'
error_logs.insert_one(log)
