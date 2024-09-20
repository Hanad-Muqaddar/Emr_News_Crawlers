# Packages to be imported
import json
import time
import requests
import traceback
import dateparser
from pymongo import MongoClient
from datetime import datetime
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
c_name = 'MSC_ Industrial_Supply' # Name of the Collection
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
collection = news['MSC_ Industrial_Supply']
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
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'referer': 'https://www.mscdirect.com/corporate/press-releases',
        'cookie': 'visid_incap_2587862=dDXGLOVzQVO/NRIVxNP9HSGk2mYAAAAAQUIPAAAAAAAkABs0/KojmHa36mww1doU; incap_ses_959_2587862=hlnRXMjxbzuwZP/WmQ1PDSGk2mYAAAAAfAKn8w2lRykmymN5RavzGQ==; dtCookie=v_4_srv_25_sn_0AD681C3120269810B1C3C745EAB112D_perc_100000_ol_0_mul_1_app-3A4933650768ea878a_1_rcs-3Acss_0; incap_ses_1780_2587862=rMhXCLSF8wt+iFH5r9SzGDSk2mYAAAAATE6ZJSYRHLz3bj6dwjMXpA==; rxVisitor=172560491766967D9QFUH4NV3DL32KK3BD1NVEE0D1J1R; at_check=true; AMCVS_99591C8B53306B560A490D4D%40AdobeOrg=1; AMCV_99591C8B53306B560A490D4D%40AdobeOrg=-1124106680%7CMCIDTS%7C19973%7CMCMID%7C20149500609336167121227335739677269643%7CMCAAMLH-1726209718%7C6%7CMCAAMB-1726209718%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1725612118s%7CNONE%7CvVersion%7C5.2.0; WCDE_XREFCONTACTNUMBERGUEST=; cj_channel=Direct_Navigation; s_cc=true; _evga_34c0={%22uuid%22:%227d2d239ce83498f1%22}; _sfid_4952={%22anonymousId%22:%227d2d239ce83498f1%22%2C%22consents%22:[]}; gig_canary=false; gig_canary_ver=16174-3-28760070; _blka_ruab=16; _ga=GA1.1.130746520.1725604923; _fbp=fb.1.1725604922638.898435400560439276; incap_ses_246_2619917=lLhwbkEvJgMj0xD8vfdpAzik2mYAAAAAb2rWrtv97qYBKmXMm2Om+w==; _gcl_au=1.1.789181945.1725604923; incap_ses_876_2619917=esSdC0kIrETawUvSaS0oDDik2mYAAAAAv28rRkXSpMHVdIIKyHt7xQ==; gig_bootstrap_4_R0HZVTou0ajlxJ_Xco0l_w=identity_ver4; visid_incap_2619917=JA5RSns0TpC7vDbpxQlUsTek2mYAAAAAQUIPAAAAAAAiPygwj/k54prD9nP6gNo+; Mscdirect=3876067756.33588.0000; s_sq=%5B%5BB%5D%5D; reese84=3:4KLxuJ4lMOoBnJ7yVmaVEQ==:sKDn9Pe5oJC34RdRePnuJjcNEg8+93KY0J3e1mZsO8TQsr3YnG9Cxrj5fXxETBdxlNj0FAe6CmQf7ae4j/fFlN5BzHWnNQR/Fi2B3XT0C/Yjk2b0TvubPaLH7VkMgK27/C6x9Qd2n5yTZiDQZjgm1cDLDSPYf2Wr5A/kPV+A4IWt+GEOC2KTBmt9uNPBdbsLNfEdZwxsaGkVSzWXZt7UVfr/YMhTboN8RBv3y11Xb01WfOVUG7LwG3XD/DtXI+BGhBDuLLJf5HmW5p0PA44w6wVbeoBmG+sdod2NSwOI7lzzZILKP70h4NV62sVNNUiGUBCzM7lDy23ySPYZLoeetXFPVa+xDsUX3ACEQfefuM89ptOuvhJwqIxlDppdZ7MsaUtPoG5cC8sCsVQHAZva3Cdl1Ns0G/sQdoRxAM7rUwDfYkQ2coleiWnKGdsf9yjlcFmXsb8sHtvyEBCyKo7c5w==:Ud/EWP/olyJsIGGmR0uXWkH1djF31N+/3uoi3Z0JKwk=; mboxEdgeCluster=37; c4=guest; c15=msc%3Astatic%20page%3Apress-releases; s_vnum=1727722800295%26vn%3D2; s_invisit=true; incap_ses_1854_2619917=VSgeTSdloUbbKSj8OLu6GUyt2mYAAAAAp8e0RaUcLenLlLWdQ32vCQ==; nlbi_2619917=sIqDabXUxDjBEFRtduXYDQAAAADbGvrXxZdOMJvqBR8ON7SA; incap_ses_1855_2619917=BMMXBJPxj1ZkhuSht0i+GUyt2mYAAAAAs3PiwKQ/jXii0J5OI/fWdQ==; incap_ses_878_2619917=TJlFFLxajUtbMX62YkgvDEyt2mYAAAAA53W3luUTat3extU+vCwowA==; dtSa=-; _br_uid_2=uid%3D7267694008059%3Av%3D12.0%3Ats%3D1725604922233%3Ahc%3D4; _rdt_uuid=1725604922918.c0f74883-fbde-4959-93cb-f51b73e0bc3e; _uetsid=1fd14b006c1b11efab7afdc0fac6621c; _uetvid=1fd15eb06c1b11efbcf4b940e4c298a5; __blka_ts=1725609051095; fs_lua=1.1725607252122; fs_uid=#10Q6K5#b8ecf66d-a910-4d34-9fb3-0a889417df29:f5ce40e7-3ebb-4cc0-944c-90382128046f:1725604923459::4#/1757140930; s_ppvl=msc%253Astatic%2520page%253Apress-releases%2C17%2C17%2C730%2C1536%2C730%2C1536%2C864%2C1.25%2CP; s_ppv=msc%253Astatic%2520page%253Apress-releases%2C15%2C15%2C730%2C1536%2C730%2C1536%2C864%2C1.25%2CP; nlbi_2587862=RFXkXcOhH2c3X8XpZ8kABQAAAAC0J06rqUckvw24UKJQIPP+; _ga_CM5B4R0KX7=GS1.1.1725604922.1.1.1725607297.5.0.0; mbox=PC#7de07673529c4f948c2163edbe0d8093.37_0#1788852100|session#de61cd2ece6f467591c7311458b540df#1725609160; nlbi_2587862_2147483392=ywNqQcv5khrfmbV9Z8kABQAAAABwdnUS0HONXEofJQfELcZf; utag_main=v_id:0191c6117df8004c86d15df6f22c0506f003206700978$_sn:2$_se:3$_ss:0$_st:1725609102287$vapi_domain:mscdirect.com$ses_id:1725607243750%3Bexp-session$_pn:3%3Bexp-session; rxvt=1725609102392|1725604917670; dtPC=25$7298883_742h12vCTLFGRCSDFPRDHRKRPMCAUDGAQPARHUP-0e0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }
    # proxies = {'http': 'http://p5IChyPNwWS1LFUQ:wifi;gb;;;@proxy.rampageproxies.com:9166', 'https': 'http://p5IChyPNwWS1LFUQ:wifi;gb;;;@proxy.rampageproxies.com:9166'}
    proxies = {}
    Main_url = "https://www.mscdirect.com" 
    # Base_url = "https://www.mscdirect.com/corporate/press-releases" 
    Base_url = "https://www.mscdirect.com/global/api/press-releases.json" 
    result = requests.get(Base_url,headers=headers, proxies=proxies)
    data_json = result.json()
    
    total_titles = []
    total_dates = []
    total_links =[] 
    
    for year, events in data_json.items():
        for event in events:
            total_titles.append(event['linkText'])
            total_dates.append(event['date'])
            link = f"https:{event['link']}"
            total_links.append(link)
            
    print(len(total_titles))
    print(len(total_dates))
    print(len(total_links), "\n")
    
    links_list = []
    mydoc = collection.find()
    for x in mydoc:
        links_list.append(x['News_Weblink'])
    
    page_source = "https://www.mscdirect.com/corporate/press-releases"
    Emr_Crawlers_Logs(c_name, page_source, total_links)

    for i, N_Date, lin in zip(total_titles, total_dates, total_links):  
        if lin in links_list:
            total_crwalled_links += 1
            Already_exist += 1
            print("Already Crawled")
            continue
        else:      
            try:
                title = i
                print(title)
            except:
                title = ""
            
            announcement_type = "Press Release"
            language = "en-us"
            
            image = ""         
            sub_category = ""   
            analysis = ""
            try:
                news_date = dateparser.parse(N_Date)
                print(news_date)
            except:
                news_date = ""

            news_weblink = lin
            print(news_date)
            announcement = ""
            
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

error_logs.insert_one(log)