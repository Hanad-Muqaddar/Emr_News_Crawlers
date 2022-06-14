import pymongo
import datetime
import copy

myclient = pymongo.MongoClient("mongodb://su-du-ad:updatedSuperDuperAdmin@34.121.98.98:27017/emrweb?authSource=admin")
myclient2 = pymongo.MongoClient("mongodb://su-du-ad:updatedSuperDuperAdmin@18.156.208.71:27017/emrweb?authSource=admin")

MyDatabase = myclient["TEMP_EMR_NEWS_Crawler_Status"]
MyDatabase2 = myclient2['TEMP_EMR_NEWS_Crawler_DB']

MyCollection = MyDatabase["Crawler_Status"]
today_date = datetime.datetime.now()


def calculate_time_interval(start_time, end_time):                   
    duration = end_time - start_time                        
    duration_in_s = duration.total_seconds()
    days    = divmod(duration_in_s, 86400)
    hours   = divmod(days[1], 3600)
    minutes = divmod(hours[1], 60)
    seconds = divmod(minutes[1], 1)
    time_interval = "Time Taken: %d days, %d hours, %d minutes, %d seconds" % (days[0], hours[0], minutes[0], seconds[0])
    return time_interval

crawlerToCollectionMapping={
    "ABB":"ABB",
    "ACOME":"ACOME",
    "Acquity_Brands_Investors":"Acquity_Brands",
    "Acquity_Brands":"Acquity_Brands",
    "ADHQ":"ADHQ",
    "Atkore_International":"Atkore_International",
    "Belden_International":"Belden_International",
    "CHINT":"CHINT",
    "Danfoss":"Danfoss",
    "EATON":"EATON",
    "Ensto_Group":"Ensto_Group",
    "EUEW":"EUEW",
    "FEGIME":"FEGIME",
    "Friedhelm_Group":"Friedhelm_Group",
    "GRAYBAR_ELECTRIC":"GRAYBAR_ELECTRIC",
    "HAGER":"HAGER",
    "HITACHI_ABB":"HITACHI_ABB",
    "HONEYWELL":"HONEYWELL",
    "LEGRAND":"LEGRAND",
    "NAED":"NAED",
    "NEXANS":"NEXANS",
    "OSRAM_new":"OSRAM",
    "OSRAM":"OSRAM",
    "PANDUIT":"PANDUIT",
    "Phoenix_Contact":"Phoenix Contact",
    "Prysmian_Group":"Prysmian_Group",
    "RDM":"RDM",
    "RITTAL":"RITTAL",
    "ROCKWELL":"ROCKWELL",
    "SCHNIDER_ELECTRIC":"SCHNIDER_ELECTRIC",
    "SIEMENS_ENERGY":"SIEMENS_ENERGY",
    "SIEMENS":"SIEMENS",
    "SIGNIFY":"SIGNIFY",
    "SITECO":"SITECO",
    "SONEPAR":"SONEPAR",
    "SOUTHWIRE":"SOUTHWIRE",
    "Weidmuller":"Weidmuller",
    "WESCO":"WESCO",
    "WURTH":"WURTH",

    "AHLSELL":"AHLSELL",
    "Alexander_Burkle":"Alexander_Burkle",
    "Amazon_Business":"Amazon_Business",
    "AMO_KABEL":"AMO_KABEL",
    "AO":"AO",
    "ARE":"ARE",
    "Atkore_second_link":"Atkore_International",
    "B_E_G_Luxomat":"B.E.G",
    "Bachmann":"Bachmann_GmbH",
    "BRAVIDA":"BRAVIDA",
    "Brumberg_Leuchten":"Brumberg_Leuchten",
    "Bunzl":"Bunzl",
    "CAVERION":"CAVERION",
    "CELLPACK_BBC":"CELLPACK_BBC",
    "Cooper_Lighting":"Cooper_Lighting",
    "Deha_group":"Deha_Group",
    "Dehn_International":"DEHN",
    "Draka_Comteq":"Draka_Comteq",
    "Eaton":"EATON",
    "ELEKTROKABEL":"ELEKTROKABEL",
    "Emerson_Group":"Emerson_Group",
    "Emiloffelhardt_Gmbh":"Emiloffelhardt_GmbH",
    "ES_ELECTRO":"ES_ELECTRO",
    "EsyLux":"ESYLUX",
    "EUROPACABLE":"EUROPA_CABLE",
    "EUROPE_FIRE_SAFETY_ALLIANCE":"EUROPE_FIRE_SAFETY",
    "farnell":"Farnell",
    "Finder":"Finder",
    "Fluke":"Fulke",
    "GGK_Gmbh":"GGK_GmbH",
    "Gira_Gmbh":"Gira_Gmbh",
    "Glen_Dimplex":"Glen_Dimplex",
    "Habia":"Habia",
    "Hardy_Schmitz":"Hardy_Schmitz",
    "HARJU":"HARJU",
    "HELKAMA":"HELKAMA",
    "Hellermantyton":"HELLERMANTYTON",
    "Hikvision":"HIKVISION",
    "Hubble":"Hubbell",
    "IMELCO":"IMELCO",
    "INFRALOGIC":"INFRALOGIC",
    "IRKUTSKKABEL":"IRKUTSKKABEL",
    "ITSME":"ITSME",
    "Jung":"Jung",
    "KAJOTE":"KAJOTE",
    "KAMKABEL":"KAMKABEL",
    "Kleintools":"KLEINTOOLS",
    "Lapp_Group":"Lapp_Group",
    "Latrivenetacavi":"LATRIVENETACAVI",
    "Ledvance":"LEDVANCE",
    "LedVance1":"LEDVANCE",
    "Leviton_new":"Leviton",
    "Leviton":"LEVITON",
    "MARCHIOL_D_O_O":"MARCHIOL_D_O_O",
    "Mennekes":"MENNEKES",
    "Mercateo":"Mercateo",
    "Mersen":"MERSEN",
    "MersenCom":"MERSEN",
    "Metz_Connect":"Metz_Connect",
    "NAED_Prexx_Release":"NAED",
    "NESTOR":"NESTOR",
    "NiedaxGroup":"NIEDAX",
    "NKT":"NKT",
    "Nvent":"NVENT",
    "Obeta":"Obeta",
    "Oosterberg":"Oosterberg",
    "Opple":"OPPLE",
    "ORSTED":"ORSTED",
    "PipeLife":"PIPELIFE",
    "QMG":"QMG",
    "REKA":"REKA",
    "Rexel":"REXEL",
    "Ridi_Leuchten":"Ridi_Leuchten",
    "Ritto_GMBH":"Ritto_GmbH",
    "RS_Components":"RS_Components",
    "RYBINSKKABEL":"RYBINSKKABEL",
    "RZB":"RZB",
    "SARANSKKABEL":"SARANSKKABEL",
    "Schenider_Electric":"SCHNIDER_ELECTRIC",
    "Schuch":"Schuch",
    "SCHUURMAN":"SCHUURMAN",
    "Siedle":"Siedle",
    "SIGNIFY":"SIGNIFY",
    "Simon_Electric":"Simon_Electric",
    "Simonelectric":"SIMONELECTRIC",
    "Socoda":"Socoda",
    "Solar":"Solar",
    "SouthWire":"SOUTHWIRE",
    "Spelsberg":"SPELSBERG",
    "TEC_CON":"TEC_CON",
    "Telegartner":"Telegartner",
    "TFK_TELE_FONIKA":"TFK_TELE_FONIKA",
    "Theben_AG":"Theben_AG",
    "URMET":"URMET",
    "Wago":"WAGO",
    "Walther_Werke":"Walther_Werke",
    "WEG":"WEG",
    "Zevi_Crawler":"ZVEI",
    "Zumtobel":"Zumtobel",
    "MSC_ Industrial_Supply":"MSC_ Industrial_Supply"
}

def crawler_health_function(crawler_name, path):
    item = {}
    item["Crawler_Name"] = ""
    item['Running_DateTime'] = today_date
    item['Status'] = ""
    item['News_Count'] = ""
    item['Latest_News_Date'] = ""
    item['Last_News_Date'] = ""
    item['Error_Type'] = ""
    item['Is_Latest'] = True
    item['Time_Interval_Taken_To_Run'] = ""
    try:
        MyCollection.update_many({"Crawler_Name":crawler_name, "Is_Latest":True},{"$set":{"Is_Latest":False}})
        new_item = copy.deepcopy(item)
        new_item['Crawler_Name'] = crawler_name
        new_item['Status'] = "Running"
        returning_id = MyCollection.insert_one(new_item)
        path = path + crawler_name + ".py"
        start_time = datetime.datetime.now()
        exec(open(path).read())
        end_time = datetime.datetime.now()
        time_interval = calculate_time_interval(start_time, end_time)
        MyCollection2 = MyDatabase2[crawlerToCollectionMapping[crawler_name]]
        date_to_query = datetime.datetime(today_date.year,today_date.month,today_date.day)
        documents_count = MyCollection2.count_documents({"Crawled_on":{"$gte": date_to_query}})
        if int(documents_count) == 0:
            MyCollection.update_one({"_id": returning_id.inserted_id}, {"$set":{"Status":"Finished", "News_Count":documents_count, "Time_Interval_Taken_To_Run":time_interval}})
        else:
            data =  list(MyCollection2.aggregate([{"$match":{"Crawled_on":{"$gte": date_to_query}}},{"$sort":{"Date":-1}}]))
            endDate = data[0]['Date']
            startDate = data[-1]['Date']
            MyCollection.update_one({"_id": returning_id.inserted_id}, {"$set":{"Status":"Finished", "News_Count":documents_count, "Latest_News_Date":endDate, "Last_News_Date":startDate, "Time_Interval_Taken_To_Run":time_interval}})
    except Exception as e:
        MyCollection.update_one({"_id": returning_id.inserted_id}, {"$set":{"Status":"Error In Crawler", "Error_Type":str(e), "Time_Interval_Taken_To_Run":time_interval}})


Emr_News_Cralers_Dict = {
    "ABB" : "/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "ACOME" : "/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "Acquity_Brands_Investors":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "Acquity_Brands":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "ADHQ":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "Atkore_International":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "Belden_International":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "CHINT":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "Danfoss":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "Ensto_Group":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "EUEW":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "FEGIME":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "Friedhelm_Group":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "GRAYBAR_ELECTRIC":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "HAGER":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "HITACHI_ABB":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "HONEYWELL":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "LEGRAND":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "NAED":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "NEXANS":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "OSRAM_new":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "OSRAM":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "PANDUIT":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "Phoenix_Contact":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "Prysmian_Group":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "RDM":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "RITTAL":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "ROCKWELL":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "SCHNIDER_ELECTRIC":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "SIEMENS_ENERGY":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "SIEMENS":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "SIGNIFY":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "SITECO":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "SONEPAR":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "SOUTHWIRE":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "Weidmuller":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "WESCO":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",
    "WURTH":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/EMR_Scripts/",

    "AHLSELL":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Alexander_Burkle":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Amazon_Business":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "AMO_KABEL":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "AO":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "ARE":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Atkore_second_link":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "B_E_G_Luxomat":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Bachmann":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "BRAVIDA":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Brumberg_Leuchten":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Bunzl":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "CAVERION":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "CELLPACK_BBC":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Cooper_Lighting":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Deha_group":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Dehn_International":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Draka_Comteq":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Eaton":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "ELEKTROKABEL":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Emerson_Group":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Emiloffelhardt_GmbH":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Ledvance":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "ES_ELECTRO":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "EsyLux":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "EUROPACABLE":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "EUROPE_FIRE_SAFETY_ALLIANCE":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "farnell":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Finder":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Fluke":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "GGK_Gmbh":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Gira_Gmbh":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Glen_Dimplex":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Habia":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Hardy_Schmitz":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "HARJU":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "HELKAMA":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Hellermantyton":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Hikvision":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Hubble":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "IMELCO":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "INFRALOGIC":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "IRKUTSKKABEL":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "ITSME":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Jung":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "KAJOTE":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "KAMKABEL":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Kleintools":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Lapp_Group":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Latrivenetacavi":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "LedVance1":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Leviton_new":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Leviton":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "MARCHIOL_D_O_O":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Mennekes":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Mercateo":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Mersen":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "MersenCom":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Metz_Connect":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "NAED_Prexx_Release":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "NESTOR":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "NiedaxGroup":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "NKT":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Nvent":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Obeta":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Oosterberg":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Opple":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "ORSTED":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "PipeLife":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "QMG":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "REKA":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Rexel":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Ridi_Leuchten":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Ritto_GMBH":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "RS_Components":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "RYBINSKKABEL":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "RZB":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "SARANSKKABEL":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Schenider_Electric":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Schuch":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "SCHUURMAN":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Siedle":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "SIGNIFY":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Simon_Electric":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Simonelectric":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Socoda":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Solar":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "SouthWire":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Spelsberg":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "TEC_CON":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Telegartner":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "TFK_TELE_FONIKA":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Theben_AG":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "URMET":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Wago":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Walther_Werke":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "WEG":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Zevi_Crawler":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "Zumtobel":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/",
    "MSC_ Industrial_Supply":"/home/ubuntu/Emr-Crawlers/Emr_News_Crawlers/TestingDir/NewScripts/"
}


for key, value in Emr_News_Cralers_Dict.items():
    crawler_health_function(key, value)


