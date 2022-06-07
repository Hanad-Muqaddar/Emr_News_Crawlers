def creating_pipeline():
    pipeline = [
    {
      "$sort": {
         "_id": -1
      }
   },
    {
        "$limit" : 300  
    }
    ]
    return pipeline


def creating_dataframe():
    import pymongo
    import pandas as pd
    myclient = pymongo.MongoClient("mongodb://su-du-ad:updatedSuperDuperAdmin@18.156.208.71:27017/emrweb?authSource=admin")
    mydb = myclient['Logs_DB']
    news = mydb['Logs_TEMP_EMR_NEWS_Crawler_DB']
#     Calling pipeline function
    pipeline = creating_pipeline()
    results = news.aggregate(pipeline)
#   loop on results
    Crawler_Name = []
    Starting_Time = []
    Error_Details = []
    Running_Sequence = []
    Latest_News_Crawl = []
    number_of_links_crawled_lst = []
    for x in results: 
        try:
            Crawler_Name_i = x['Crawler_name']
        except:
            Crawler_Name_i = ""
        try:
            Starting_Time_i = x['Starting_time']
        except:
            Starting_Time_i = ""
        try:
            Error_Details_i = x['Error_Detail']
        except:
            Error_Details_i = ""
        try:
            if 'Crawler_Runing Sequence' not in x:
                Running_Sequence_i = x['Running_sequance']
            else:
                Running_Sequence_i = x['Crawler_Runing Sequence']
            
        except:
            Running_Sequence_i = ""
        try:
            Latest_News_Crawl_i = x['Last_news_crawl_time']
            if Latest_News_Crawl_i == "":
                Latest_News_Crawl_i = "____________"
        except:
            Latest_News_Crawl_i = ''
#         ************************************************************************
        try:
            number_of_links_crawled1 = Running_Sequence_i[-1]
        except:
            number_of_links_crawled1 = ""
        try:
            number_of_links_crawled2 = Running_Sequence_i[-2]
        except:
            number_of_links_crawled2 = ""
        number_of_links_crawled = str(number_of_links_crawled1) + str(number_of_links_crawled2)
        number_of_links_crawled_lst.append(number_of_links_crawled)
        Crawler_Name.append(str(Crawler_Name_i))
        Starting_Time.append(str(Starting_Time_i))
        Error_Details.append(str(Error_Details_i))
        Running_Sequence.append(str(Running_Sequence_i))
        Latest_News_Crawl.append(str(Latest_News_Crawl_i))
#         ************************************************************************
        p_name = pd.Series(Crawler_Name, name='Crawler_Name')
        str_time = pd.Series(Starting_Time, name='Starting_Time')
        err_det = pd.Series(Error_Details, name='Error_Details')
        r_seq = pd.Series(Running_Sequence, name='Running_Sequence')
        lat_new = pd.Series(Latest_News_Crawl, name='Latest_News_Crawl')
        number_of_l = pd.Series(number_of_links_crawled_lst, name='Number of Links Crawled')

    df = pd.concat([p_name, str_time, err_det, r_seq, lat_new, number_of_l], axis=1)
    return df

def write_data_to_sheet():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    # use creds to create a client to interact with the Google Drive API
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('/home/emr/TestingDir/NewScripts/creds.json', scope)
    client = gspread.authorize(creds)

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open("Crawlers_Info").sheet1
    df = creating_dataframe()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())


write_data_to_sheet()