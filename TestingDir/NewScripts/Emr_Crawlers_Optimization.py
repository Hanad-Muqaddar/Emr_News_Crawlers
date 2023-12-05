from pymongo import MongoClient
from datetime import datetime

def Emr_Crawlers_Logs(Crawler_Name,WebSite,Url):
    myclient = MongoClient("mongodb://su-du-ad:updatedSuperDuperAdmin@34.121.98.98:27017/emrweb?authSource=admin")
    MyDatabase = myclient["emrweb"]
    Crawler_Logs_Database = MyDatabase["EMR_Crawlers_Optimization_Logs_testing"]
    Crawler_Logs_Database.insert_one({ "Crawler_Name": Crawler_Name ,"WebSite":WebSite ,"News_url":Url , "runningDateTime": datetime.now()})



