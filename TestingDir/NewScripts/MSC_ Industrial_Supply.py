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
        'cookie': 'visid_incap_2587862=ls/R9kUERhOXr10Tvo9v/AcQ2GYAAAAAQUIPAAAAAAA3iTjD0YlNY35q1dp9YDfl; visid_incap_2619917=jjkrDsV+RxSyb0nUiF/IACAQ2GYAAAAAQUIPAAAAAACSSmb04kDWS4DDKzelLG1N; _evga_34c0={%22uuid%22:%22b05530463ef082a4%22}; _sfid_4952={%22anonymousId%22:%22b05530463ef082a4%22%2C%22consents%22:[]}; gig_bootstrap_4_R0HZVTou0ajlxJ_Xco0l_w=identity_ver4; cjConsent=MHxZfDB8Tnww; _ga=GA1.1.837672309.1725435945; _blka_ruab=136; _fbp=fb.1.1725435951792.351092964968605496; incap_ses_1556_2587862=PRh3MorhIy3QZS4o8AWYFcdMUWcAAAAAmq/Oy8Ef2om1jJac1OleGA==; reese84=3:85j6wpeQwc0eOh2wYe3stg==:qc8LPKh7WsARL2jfVbt2HxYu5vDT4KUNog5D6CD+g6Vb/cVpENusTzWfoZmBBaG0/u8P59AtdQUTZCUEJCuzb1YBFW+bvledXQbDU5z2Kezkcehv69+IHxXJg55HPOwZCSx09E2m9HhXKshBpTcv2IdM2uEmI9lzgayhSoSpmF7saLZZg7pj384zOq67vtI4m359lq3OpWUEMrJteOIuQWED2DDTxkntqoHqFcFSQAXBaW2vtpMbtV29hp1YOc8fa4sN7tbNnZJQrzkW+HJ6HVaVqBJ0w8IUKUIA7rAmz0nrK0gg+sL/RewGbohgaV3rvbgG6C1z/UuXi0w2PDnsep+vuFwLue2fsB6aVi99n5s9vP8WbgfrTxxJJXdRDWzJjPtx/tIAihesUymzjqEsh8oWkXjUkONl7aBS0wZcm03EMDU3XKkHw8fBBDjJYkLZC4fyCY+xtfOxAc+Mvccimw==:ODFhGTeUpce85C8APgDqekfEt8Bs5eFIf5FUIPo/Cf4=; dtCookie=v_4_srv_29_sn_9BE70A031FE18B04FC860E30198EB8DD_perc_100000_ol_0_mul_1_app-3A4933650768ea878a_1_rcs-3Acss_0; incap_ses_1780_2587862=ZceTNGuNHQ1ZP735vdSzGOBMUWcAAAAAszkgaicFl4APQS4rCyHCcA==; rxVisitor=1733381345174R9FB39IOTUHDH3SBMISF4LE6L28TV9LS; at_check=true; Mscdirect=3859290540.33588.0000; AMCVS_99591C8B53306B560A490D4D%40AdobeOrg=1; AMCV_99591C8B53306B560A490D4D%40AdobeOrg=179643557%7CMCIDTS%7C20063%7CMCMID%7C72749370582480045393885188829711538854%7CMCAAMLH-1733986146%7C6%7CMCAAMB-1733986146%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1733388546s%7CNONE%7CvVersion%7C5.5.0; mboxEdgeCluster=37; WCDE_DA822=B; WCDE_XREFCONTACTNUMBERGUEST=; incap_ses_408_2619917=Qvn+Xm1GWmKhshDz9IGpBeNMUWcAAAAAaqBLZU86xu40KBFuN3BEUA==; cj_channel=Direct_Navigation; nlbi_2619917=Sc//QynnuhK3MXuaduXYDQAAAACUhqYWh3x09+fgYsAGxo3T; incap_ses_1288_2619917=jdDDTap+NgIrRAK/RuXfEeNMUWcAAAAAGwpFzceU/Y6/L2FapJ5agQ==; c4=guest; c15=msc%3Astatic%20page%3Apress-releases; s_vnum=1735671600372%26vn%3D1; s_invisit=true; s_cc=true; _gcl_au=1.1.117179723.1733381350; dtSa=-; _uetsid=0756faa0b2d511efa141edbfba483f6c; _uetvid=b1c861006a9111ef8bf17984027f82c0; _rdt_uuid=1725435948678.4457db03-7d3d-4a6a-9255-d081dd421b41; _br_uid_2=uid%3D3648373341534%3Av%3D12.0%3Ats%3D1725435943183%3Ahc%3D7; __blka_ts=1733383292259; fs_lua=1.1733381492419; fs_uid=#10Q6K5#5973b913-3699-4bbd-be39-27eebab7347b:519700f2-cd44-4099-8cb8-f8d9b4bc696a:1733381349416::3#/1756971958; s_ppvl=msc%253Astatic%2520page%253Apress-releases%2C100%2C100%2C730%2C968%2C730%2C1536%2C864%2C1.25%2CP; s_ppv=msc%253Astatic%2520page%253Apress-releases%2C14%2C14%2C730%2C968%2C730%2C1536%2C864%2C1.25%2CP; s_sq=mscprod%3D%2526c.%2526a.%2526activitymap.%2526page%253Dmsc%25253Astatic%252520page%25253Apress-releases%2526link%253DPress%252520Releases%2525202024%25252011%25252F05%25252F2024%252520MSC%252520Industrial%252520Supply%252520Co.%252520to%252520Participate%252520at%252520Upcoming%252520Investor%252520Conferences%25252010%25252F24%25252F2024%252520MSC%252520Industri%2526region%253DBODY%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Dmsc%25253Astatic%252520page%25253Apress-releases%2526pidt%253D1%2526oid%253DfunctionBf%252528%252529%25257B%25257D%2526oidt%253D2%2526ot%253DDIV; incap_ses_8219_2619917=Fu3lH8OGIGiN1ZTlDcEPcqlNUWcAAAAAS/b/eOOPJ7smF/TgSm6zNA==; incap_ses_875_2619917=ItCPaQLNpAL7WOOL+58kDKpNUWcAAAAAGENtWOoXDwfO9te3lIH+2w==; nlbi_2587862=XsdIL0wli36BLJFTZ8kABQAAAACMn+0utknXyngJ44bpeC8S; _ga_CM5B4R0KX7=GS1.1.1733381349.4.1.1733381754.60.0.0; mbox=PC#a419a8a567634e2385f12186af4e8587.37_0#1796626557|session#fba960e38c154802a774d73f2c13390f#1733383617; rxvt=1733383557447|1733381345175; dtPC=29$581755739_65h-vPMRRQRKJAFVLRNPKHLQSSNFPBEUNUAKP-0e0; nlbi_2587862_2147483392=gEE/Tvc12QTwhxhBZ8kABQAAAAD/inMR7Zol+TIygR7wd/Yc; utag_main=v_id:0191bbff09430089d48c04e02cf80506f003206700978$_sn:4$_se:4%3Bexp-session$_ss:0%3Bexp-session$_st:1733383557998%3Bexp-session$vapi_domain:mscdirect.com$ses_id:1733381347946%3Bexp-session$_pn:4%3Bexp-session',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }
    # proxies = {'http': 'http://p5IChyPNwWS1LFUQ:wifi;gb;;;@proxy.rampageproxies.com:9166', 'https': 'http://p5IChyPNwWS1LFUQ:wifi;gb;;;@proxy.rampageproxies.com:9166'}
    proxies = {'http': 'http://waleeProxy:Cheeta@1@de.proxymesh.com:31280', 'https': 'http://waleeProxy:Cheeta@1@de.proxymesh.com:31280'}
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

error_logs.insert_one(log)