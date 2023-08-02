from pickle import FALSE
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
import json

myclient = MongoClient("mongodb://su-du-ad:updatedSuperDuperAdmin@34.121.98.98:27017/emrweb?authSource=admin")
MyDatabase = myclient["emrweb"]
status_Database = MyDatabase["Master_And_Mapping_Script_Logs"]
statusdict = { "name": "Mapping_Script", "runningDateTime": datetime.now() , "status": "Running" }
status_Id = status_Database.insert_one(statusdict)

last_time = None
runnung_sequence = []
start_time = datetime.now()
start_CPU_Stat = str(psutil.cpu_percent())
start_RAM_Stat = str(psutil.virtual_memory())
today = datetime.now()
try:
    try:
        file = open("/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/config.json")
        data = json.load(file)
        db_path = data[0]['Db_Path']
        Client = MongoClient('localhost',27017)
        #liveDb = MongoClient('localhost',27017)
        # liveDb = MongoClient('mongodb://su-du-ad:updatedSuperDuperAdmin@18.156.208.71:27017/emrweb?authSource=admin')
        liveDb = MongoClient(db_path)
        emrDB = MongoClient('mongodb://su-du-ad:updatedSuperDuperAdmin@34.121.98.98:27017/emrweb?authSource=admin')
        runnung_sequence.append('Connected Sucessfully')
    except:
        runnung_sequence.append('Connection Failed')
    
    localDB=liveDb['emrHagerv2']
    evn='prod'
    if evn =='dev':
        Db = liveDb['emrdevtwo']
    else:
        Db = emrDB['emrweb']
    
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
            last_time = l_i['Starting_time']
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
        destinationDB = emrDB['emrweb']
        
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
    'GGK_Gmbh' : ObjectId('61cd87c383206f95a9119c2b'),
    'Ritto_GmbH' : ObjectId('61dd600158d11ab9802d847f'),
    'RS_Components' : ObjectId("618bbcdd215e120cf9b6063c"),
    'RZB' : ObjectId("61cc49890e9e5244a6b493ed"),
    'Schuch' : ObjectId("61cc5daa83206f95a9113a15"),
    'Siedle' : ObjectId("60cb34c105a5122ebf153198"),
    'Solar' : ObjectId("60fe9c0aa56716b7aebcf031"),
    'Telegartner' : ObjectId("61ce9eb683ff8a2ac7eb1766"),
    'Theben_AG' : ObjectId("61ced44d83ff8a2ac7eb2e73"),
    'URMET' : ObjectId("600ed3b52852a01e483e3bd7"),
    'Walther_Werke' : ObjectId("61cf04e3e465e24bca590fb9"),
    'NKT' : ObjectId("6222059f5241f6bddcd8aaaa"),
    'Habia' : ObjectId("62220ccb5241f6bddcd901b9"),
    'REKA' : ObjectId("6225af9e5241f6bddcddefcf"),
    'HELKAMA' : ObjectId("6225ba995241f6bddcde0a5c"),
    'KAJOTE' : ObjectId("6225d1515241f6bddcde24a3"),
    'NESTOR' : ObjectId("6225d4835241f6bddcde2c64"),
    'TFK_TELE_FONIKA' : ObjectId("6225da625241f6bddcde3547"),
    'ELEKTROKABEL' : ObjectId("6225dd035241f6bddcde3b2a"),
    'KAMKABEL' : ObjectId("6225e1545241f6bddcde4155"),
    'IRKUTSKKABEL' : ObjectId("6225e6595241f6bddcde5ae7"),
    'Socoda' : ObjectId("623312ea4bb2fdf46638e231"),
    'CELLPACK_BBC' : ObjectId("623314104bb2fdf46638e2a1"),
    'MARCHIOL_D_O_O' : ObjectId("6233178b4bb2fdf46638efea"),
    'SARANSKKABEL' : ObjectId("6225e7aa5241f6bddcde6040"),
    'RYBINSKKABEL' : ObjectId("6225e7ec5241f6bddcde61c4"),
    'INFRALOGIC' : ObjectId("6225e8785241f6bddcde6363"),
    'TEC_CON' : ObjectId("6225e8b05241f6bddcde64e7"),
    'SCHUURMAN' : ObjectId("6225e8e65241f6bddcde666b"),
    'AMO_KABEL' : ObjectId("623480b34bb2fdf46639d797"),
    'CAVERION' : ObjectId("6225e99c5241f6bddcde6825"),
    'ARE' : ObjectId("6225e9c45241f6bddcde69a9"),
    'ES_ELECTRO' : ObjectId("6234823b4bb2fdf46639f5fb"),
    'QMG' : ObjectId("623482e24bb2fdf46639f8bc"),
    'AHLSELL' : ObjectId("623483dc4bb2fdf46639fc2b"),
    'HARJU' : ObjectId("623483fb4bb2fdf46639fd1c"),
    'BRAVIDA' : ObjectId("623484504bb2fdf4663a004b"),
    'EUROPA_CABLE' : ObjectId("623484324bb2fdf46639fec2"),
    'EUROPE_FIRE_SAFETY' : ObjectId("623484174bb2fdf46639fdd9"),
    'ORSTED' : ObjectId("623485b44bb2fdf4663a00d4"),
    'Phoenix Contact' : ObjectId("60c9ae6793a9401abe47dd4c"),
    'MSC_ Industrial_Supply' : ObjectId("61715d10c91d8776ded7c2bf"),
    'Atkore_International' : ObjectId("60be0da5c35e8a6bcd13b54a"),
    'Simon_Electric' : ObjectId("60cc323cf55392bb06c91ce4"),
    'WAGO' : ObjectId("62fe31c12f68dbba24590996"),
    'AO' : ObjectId("623484224bb2fdf46639fe56"),
    'BECKHOFF' : ObjectId("637f23887498254fca079ef1"),
    'HARTING' : ObjectId("63806b387498254fca0a2668"),
    'WIELAND' : ObjectId("6385e2057498254fca103a77"),
    'BOSCH' : ObjectId("637ddc21fdef1ae80ee79c3d"),
    'WIELAND_ELECTRIC' : ObjectId("63a1b7537498254fca6437fd"),
    # '' : ObjectId(""),
    # '' : ObjectId(""),
    # '' : ObjectId(""),
    # '' : ObjectId(""),
    'Alexander_Burkle' : ObjectId('61cc5db183206f95a9113a5e'),
    'Amazon_Business' : ObjectId('618398ad4ddd028ed14aae97'),
    'Bachmann_GmbH' : ObjectId('61cc00700e9e5244a6b46f3e'),
    'Brumberg_Leuchten' : ObjectId('61cc52f80e9e5244a6b5418d'),
    'Bunzl' : ObjectId('61cee20f83ff8a2ac7eb3c7a'),
    'Cooper_Lighting' : ObjectId('61dd238bf35e0cb05308adee'),
    'Deha_Group' : ObjectId('61ceac8b83ff8a2ac7eb2254'),
    'Draka_Comteq' : ObjectId('61cd61b983206f95a9117daf'),
    'Emerson_Group' : ObjectId('60bf57ad82ccebf552ac09b5'),
    'Emiloffelhardt_GmbH' : ObjectId('61cd809683206f95a9119a48'),
    'Farnell' : ObjectId('6183995f4ddd028ed14aaf2f'),
    'Finder' : ObjectId('61cd61bc83206f95a9117e03'),
    'Fulke' : ObjectId('61cc497f0e9e5244a6b493a3'),
    'Gira_Gmbh' : ObjectId('61cc365c0e9e5244a6b479e3'),
    'Glen_Dimplex' : ObjectId('61cd4f5183206f95a91146af'),
    'Hardy_Schmitz' : ObjectId('61cdacf383206f95a911ba2f'),
    'ITSME' : ObjectId('61cdb34a83206f95a911be95'),
    'Jung' : ObjectId('5ff1c58d2852a0230444c6a4'),
    'Lapp_Group' : ObjectId('61ceef3883ff8a2ac7eb3d9f'),
    'Mercateo' : ObjectId('61cef3bd83ff8a2ac7eb3ecd'),
    'Metz_Connect' : ObjectId('61cd371583206f95a9113c2e'),
    'Obeta' : ObjectId('61ceb4e783ff8a2ac7eb2698'),
    'Oosterberg' : ObjectId('61cc372f0e9e5244a6b47b81'),
    'Ridi_Leuchten':ObjectId('61ceafd383ff8a2ac7eb24f7'),
    'ZVEI':ObjectId('5fae78262852a032c08c057d'),
    'OSRAM':ObjectId('5fc133e62852a01424dfa00b'),
    'PANDUIT':ObjectId('6038e1ce2852a030c08eee02'),
    'EATON':ObjectId('5fc7ae2e2852a095e0926303'),
    'EUEW':ObjectId('5f92ddf12852a02c74fcd455'),
    'NEXANS':ObjectId('5fc7b6582852a095e092637a'),
    'REXEL':ObjectId('5fc470232852a00420e0e4fc'),
    'SIGNIFY':ObjectId('5fc483642852a00420e0eb83'),
    'WURTH':ObjectId('5fc7a7a32852a095e092602e'),
    'CHINT':ObjectId('603cd1662852a0267c6c5774'),
    'HONEYWELL':ObjectId('5fc47e362852a00420e0e918'),
    'LEGRAND':ObjectId('5faccecf2852a01f309b5a46'),
    'SIEMENS_ENERGY':ObjectId('603ccb7d2852a0267c6c5771'),
    'ACOME':ObjectId('5fc440052852a045c0190c5c'),
    'GRAYBAR_ELECTRIC':ObjectId('602ba2252852a02c50c8846e'),
    'SCHNIDER_ELECTRIC':ObjectId('5fc12b812852a01424df9878'),
    'ABB':ObjectId('5fc47f8e2852a00420e0e9b3'),
    'SONEPAR':ObjectId('5f92e1d32852a02c74fcd781'),
    'HITACHI_ABB':ObjectId('603cbe0a2852a0267c6c576e'),
    'SITECO':ObjectId('5fc442172852a045c0190cef'),
    'SIEMENS':ObjectId('5fc46c982852a00420e0dece'),
    'HAGER':ObjectId('5fc768862852a0799860b790'),
    'ROCKWELL':ObjectId('5fc471952852a00420e0e5e8'),
    'ADHQ':ObjectId('5f92e03f2852a02c74fcd48c'),
    'OBO':ObjectId('5fc44ff12852a00420e0c984'),
    'WESCO':ObjectId('603c9b9b2852a0267c6c576b'),
    'IMELCO':ObjectId('60ae347f2852a02020c3f90a'),
    'RITTAL':ObjectId('60cb2dc7a893cf02bebede2d'),
    'FEGIME':ObjectId('60b62ef32852a01f70fef6a6'),
    'NAED': ObjectId('60b6365c2852a01f70fef71c'),
    'Acquity_Brands':ObjectId('60be08d1c35e8a6bcd13b4e3'),
    'Belden_International':ObjectId('60b768922852a0211c48ae6e'),
    'Ensto_Group':ObjectId('60c05a68a43cfab070399f52'),
    'Friedhelm_Group':ObjectId('60cb2dc7a893cf02bebede2d'),
    'Prysmian_Group':ObjectId('60c0912729b98d1706a03fe5'),
    'RDM':ObjectId('60cafd8ed268b7550a33706d'),
    'B.E.G' : ObjectId("60bf1935fe95c7abec0a8349"),
    'DEHN' : ObjectId("60bf4f96f200197956d99eaa"),
    'HELLERMANTYTON' : ObjectId('60c0a017b838222ac75f1a1d'),
    'HIKVISION' : ObjectId('60c1c97e090e7f53be20a420'),
    'KLEINTOOLS' : ObjectId('60c1fa94a384d9b930dad4e8'),
    'LATRIVENETACAVI' : ObjectId('60c2ff1f6d76231e92818df5'),
    'LEDVANCE' : ObjectId('60c33bceb34bedfec32b8766'),
    'LEVITON':ObjectId('60c7448a7843e39ac05fba3f'),
    'MENNEKES' : ObjectId('60c74a161da17cac989803c4'),
    'MERSEN' : ObjectId('60c751a470c3974b3e653efd'),
    'NIEDAX' : ObjectId('60c83e2041b45135a23f0f92'),
    'OPPLE' : ObjectId('60c99ed8417bd3969c3af4ea'),
    'PIPELIFE' : ObjectId('60c9eec086a40a41d16642df'),
    'SIMONELECTRIC' : ObjectId('60cc323cf55392bb06c91ce4'),
    'SPELSBERG' : ObjectId('60cc414b86eb480203e3b09d'),
    'Zumtobel' : ObjectId('60d06d894a6b6c8c559001f6'),
    'NVENT' : ObjectId('60c892d8982e3c2cad3b55ac'),
    'Danfoss' : ObjectId('60cc8a5810c6204a99d4f0ae'),
    'ESYLUX' : ObjectId('60c07a5f96bad1f1db95e758'),
    'GRAINGER' : ObjectId('603cddab2852a0267c6c5777'),
    'WEG' : ObjectId("617a43d1254c46559ccde026"),
    'SOUTHWIRE' :ObjectId('618a44cc2aa941a7225c5ff2'),
    'Hubbell': ObjectId("6087dff16cbd41ac14ad52d0"), 
    'Weidmuller' : ObjectId("61ceaad983ff8a2ac7eb1fa0"),
    "TriluxGmbH" : ObjectId("61cef57383ff8a2ac7eb3f8e"),
    }
    count=0
    done = []
    new_News_Links = []
    for i in newsDb.collection_names():
        if i not in companyMapping or i in done:
            continue
        runnung_sequence.append('STARTING NEW ORGANIZATION: '+i)
        print ('STARTING NEW ORGANIZATION: '+i)
        indCompany = companyCollection.find_one({'_id':companyMapping[i]})

        newsCollection = newsDb[i]
        allNewsFromDb = newsCollection.find({})

        existingNewsInSystem = historiesCollection.distinct('references.link.value',{'companyId.value':indCompany['_id']})
        for j in allNewsFromDb:
        
            if j['News_Weblink'] in existingNewsInSystem:
                continue
            else:
                count+=1
                j['references']=[]
                tempRef = {}
                tempRef['source']=copy.deepcopy(temp)
                tempRef['source']['value']=indCompany['companyNameObject']['value']
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
                tempIndNews['Remark']='ADDED TODAY'+str(today.date())
                tempIndNews['isVisible']=copy.deepcopy(temp)
                tempIndNews['isVisible']['value']=False
                tempIndNews['isDeleted']=False
                tempIndNews['thumbnailCreated'] = False
                tempIndNews['photoCreated'] = False
                tempIndNews['errorOnPhoto'] = False
                
                new_News_Links.append(j['News_Weblink'])
            historiesCollection.insert_one(tempIndNews)

        New_News_List = historiesCollection.find({"references.link.value":{"$in":new_News_Links}})
        for n in New_News_List:
            N_Date = n["Date"]["value"]
            C_Date = n["Date"]["created_at"]
            print("\n\n Crawled Date")
            print(f"\n, {N_Date} ******************************")
            print("Crawled Date")
            print(f"\n, {C_Date} ******************************")
            if N_Date:
                print("if mein a gya hn ")
                continue
                
            else:
                print("else mein a gya hn ")
                historiesCollection.update_one({"references.link.value": n["references"]["link"]["value"] }, { "$set": { "Date.value": C_Date } })

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
# error_logs.insert_one(log)
status_Database.update_one({"_id": status_Id.inserted_id , "name": "Mapping_Script"}, { "$set": { "status": "Script Completed" } })
