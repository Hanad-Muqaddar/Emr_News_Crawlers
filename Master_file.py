from readline import insert_text
import pymongo
import datetime
import copy
from bson.objectid import ObjectId

myclient = pymongo.MongoClient("mongodb://su-du-ad:updatedSuperDuperAdmin@34.121.98.98:27017/emrweb?authSource=admin")
MyDatabase = myclient["TEMP_EMR_NEWS_Crawler_Status"]
MyCollection = MyDatabase["Crawler_Status"]
today_date = datetime.datetime.now()

item = {}
item["Crawler_Name"] = ""
item['Running_DateTime'] = today_date
item['Status'] = ""

try:
    new_item = copy.deepcopy(item)
    new_item['Crawler_Name'] = "ABB"
    new_item['Status'] = "Running"
    returning_id = MyCollection.insert_one(new_item)
    exec(open('C:/Users/Lenovo/Desktop/Data BackUp Hanad/techlets/Hanad_Muqaddar_New/Emr_Crawlers_Batching_Scripts/EMR_Scripts/ABB.py').read())
    MyCollection.update_one({"_id": returning_id.inserted_id}, {"$set":{"Status":"Finished"}})
except Exception as e:
    MyCollection.update_one({"_id": returning_id.inserted_id}, {"$set":{"Status":"Error In Crawler", "Which_Error" : e}})
    