
import warnings
warnings.filterwarnings("ignore")
import psutil
import traceback
import copy
from IPython.display import clear_output
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
from dateutil.parser import *
from datetime import datetime

last_time = None
runnung_sequence = []
start_time = datetime.now()
start_CPU_Stat = str(psutil.cpu_percent())
start_RAM_Stat = str(psutil.virtual_memory())
today = datetime.now()

try:
        

    try:
        Client = MongoClient('localhost',27017)
        #liveDb = MongoClient('localhost',27017)
        liveDb = MongoClient('mongodb://su-du-ad:updatedSuperDuperAdmin@18.156.208.71:27017/emrweb?authSource=admin')
        runnung_sequence.append('Connected Sucessfully')
    except:
        runnung_sequence.append('Connection Failed')
    
    localDB=liveDb['emrHagerv2']
    evn='prod'
    if evn =='dev':
        Db = liveDb['emrdevtwo']
    else:
        Db = liveDb['emrweb']
    
    newsDb = liveDb['TEMP_EMR_NEWS_Crawler_DB']
    error_logs = liveDb['Logs_DB']['Logs_for_EMR_Mapping']
    productCollection = Db['products']
    companyCollection = Db['companies']
    stakeholderCollection = Db['stakeholders']
    customerCollection = Db['customers']
    siteCollection = Db['sites']
    historiesCollection = Db['histories']
    sourceDb=newsDb
    destinationDB =Db

    ##### Aqeel Snippet ########
    
    try:
        for l_i in error_logs.find().sort([('_id', -1)]).limit(1):
            last_time = l_i['Last_UpdateOn']
            runnung_sequence.append("Last updated on "+str(last_time))
    except:
        last_time = start_time
        runnung_sequence.append("Fresh Starting on "+str(last_time))
        # print(last_time)
    ##########################


    env = 'prod'
    if env =='dev':
        runnung_sequence.append('Connected with Dev')
        destinationDB = liveDb['emrdevtwo']
    else:
        runnung_sequence.append('Connected with Live')
        destinationDB = liveDb['emrweb']
        
    destinationCollection = destinationDB['histories']
    sourceCollection = sourceDb['ABB']
    indHistoryToBeInserted = sourceCollection.find_one({})
    allHistories = destinationCollection.find({}).sort('_id',-1)
    indHistory=''
    for i in allHistories:
        indHistory = i
        break
    runnung_sequence.append('Fields in New histories but not in Database')
    runnung_sequence.append('...........')
    for i in indHistoryToBeInserted.keys():
        if i not in indHistory:
            runnung_sequence.append(i + ' ==> value of i (indHistoryToBeInserted.keys()) not in indHistory')
    runnung_sequence.append('Fields in Existing Sites but not in New Sites')
    runnung_sequence.append('...........')
    for i in indHistory.keys():
        if i not in indHistoryToBeInserted:
            runnung_sequence.append(i + ' ==> value of i (indHistory.keys()) in indHistoryToBeInserted')

    for i in indHistory:
        if type(indHistory[i])==dict:
            indHistory[i]['value']=''
        elif type(indHistory[i])==datetime:
            indHistory[i]=today
        elif type(indHistory[i])==list:
            indHistory[i]=[]
        elif type(indHistory[i])==bool:
            continue
        else:
            indHistory[i]=''
    try:
        indHistory.pop('_id')
    except:
        pass
    try:
        indHistory.pop('__v')
    except:
        pass
    try:
        indHistory.pop('validatedObject')
    except:
        pass
    temp={}
    temp['validatedOn']=today
    temp['addedOn']=today
    temp['isValidated']=1
    temp['value']=""
    temp['addedBy']=ObjectId("5f595240ec5a1207e4810528")

    companyMapping = {
    'OSRAM':'OSRAM',
    'EATON':'Eaton',
    'EUEW':'EUEW - European Union of Electrical Wholesalers',
    'NEXANS':'Nexans',
    'REXEL':'Rexel',
    'SIGNIFY':'Signify ',
    'HONEYWELL':'Honeywell',
    'LEGRAND':'Legrand',
    'ACOME':'ACOME',
    'SCHNIDER_ELECTRIC':'Schneider Electric',
    'ABB':'ABB',
    'SONEPAR':'Sonepar',
    'SITECO':'Siteco',
    'SIEMENS':'Siemens',
    'HAGER':'Hager Group',
    'ROCKWELL':'Rockwell Automation',
    'ADHQ':' AD - Affiliated Distributor',
    'OBO':'OBO Bettermann',
    'ZVEI':'ZVEI | Germany’s Electrical Industry',
    'WURTH':'Würth',
    'GRAYBAR_ELECTRIC':'Graybar',
    'PANDUIT':'Panduit',
    'WESCO':'Wesco',
    'HITACHI_ABB':'Hitachi ABB Power Grids'}
    count=0
    done = []
    for i in newsDb.collection_names():
        #print i
        if i not in companyMapping or i in done:
            continue
        runnung_sequence.append('STARTING NEW ORGANIZATION: '+i)
        indCompany = companyCollection.find_one({'companyNameObject.value':companyMapping[i]})
        newsCollection = newsDb[i]
        allNewsFromDb = newsCollection.find({})

        existingNewsInSystem = historiesCollection.distinct('title.value',{'companyId.value':indCompany['_id']})
        for j in allNewsFromDb:
            if j['title'] in existingNewsInSystem:
                continue
            else:
                count+=1
                j['references']=[]
                tempRef = {}
                tempRef['source']=copy.deepcopy(temp)
                tempRef['source']['value']=companyMapping[i]
                tempRef['link']=copy.deepcopy(temp)
                tempRef['link']['value']=j['News_Weblink']
                j['references'].append(tempRef)
                
                tempIndNews = copy.deepcopy(indHistory)
                for newsKey in tempIndNews:
                    if newsKey in j.keys():
                        if type(tempIndNews[newsKey])==dict:
                            tempIndNews[newsKey]['value']=j[newsKey]
                        if type(tempIndNews[newsKey])==list:            
                            tempIndNews[newsKey]=j[newsKey]
                tempIndNews['announcementType']['value']=''
                tempIndNews['companyId']['value']=[indCompany['_id']]
                tempIndNews['Remark']='ADDED TODAY'
                tempIndNews['isVisible']=copy.deepcopy(temp)
                tempIndNews['isVisible']['value']=False
                tempIndNews['isDeleted']=False    
            historiesCollection.insert_one(tempIndNews)
        done.append(i)
    runnung_sequence.append(str(count)+' documents updated')
    newsWithoutValidation = historiesCollection.find({'validatedObject':{'$exists':False}})
    count = 0
    for tempIndHistory in newsWithoutValidation:
        if count%10==0:
            runnung_sequence.append(str(count) + ' ==>  count value in last section for tempIndHistory in newsWithoutValidation')
        count+=1
        validatedObject={}
        for historyKey in tempIndHistory:
            if historyKey == 'validatedObject':
                continue
            if type(tempIndHistory[historyKey])==dict:
                try:
                    validatedObject[historyKey]=tempIndHistory[historyKey]['value']
                except:
                    validatedObject[historyKey]=""
            if type(tempIndHistory[historyKey])==list:
                validatedObject[historyKey]=[]
                tempObject = {}
                for k in tempIndHistory[historyKey]:
                    for l in k:
                        if l == '_id':
                            continue
                        tempObject[l]=k[l]['value']
                    validatedObject[historyKey].append(tempObject)
        historiesCollection.update_one({'_id':tempIndHistory['_id']},{'$set':{'validatedObject':validatedObject}})
        #break
    runnung_sequence.append('Mapping Completed')
    end_time = datetime.now()
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
log['File_name'] = 'mapping_script.py'
log['File_type'] = 'Script Mapper by Salman Ansari'
log['Initial_CPU_Stat'] = start_CPU_Stat
log['Initial_RAM_Stat'] = start_RAM_Stat
log['Starting_time'] = start_time
log['Ending_time'] = Error_Time if rep == '' else end_time
log['Error_Detail'] =  Error if rep == '' else ''
log['Mapper_Runing_Sequence'] = runnung_sequence if runnung_sequence else ''
log['Last_UpdateOn'] = last_time if last_time!= None else log['Ending_time']
log['CPU_Usage'] = str(psutil.cpu_percent())
log['Total_RAM'] = str(psutil.virtual_memory().total)
log['RAM_Usage'] = str(psutil.virtual_memory().percent)
log['Avaiable_RAM_%'] = str(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total)
error_logs.insert_one(log)
