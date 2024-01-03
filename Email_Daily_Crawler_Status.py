import os
from pymongo import MongoClient
from datetime import datetime, timedelta
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


ACCESS_KEY = 'AKIAQQUX72GKCO6BOLVP'
SECRET_KEY = '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'


def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)    
    try:
        s3.upload_file(local_file, bucket, s3_file,ExtraArgs={'ACL':'public-read'})
        s3_file_path = "https://data2images.s3.ap-southeast-1.amazonaws.com/" + s3_file
        return s3_file_path
    
    except FileNotFoundError:
        return False
    
    except NoCredentialsError:
        return False

def process_Email():
    # Connect to MongoDB
    myclient = MongoClient("mongodb://su-du-ad:updatedSuperDuperAdmin@34.121.98.98:27017/emrweb?authSource=admin")
    MyDatabase = myclient["emrweb"]
    Crawler_Logs_Database = MyDatabase["EMR_Crawlers_Optimization_Logs"]

    current_datetime = datetime.now()
    year = current_datetime.year
    month = current_datetime.month
    day = current_datetime.day

    # Create a datetime object for today's date
    today_timestamp = datetime(year, month, day)

    data =[]
    current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    Crawlers = Crawler_Logs_Database.distinct("Crawler_Name")

    for crawler in list(set(Crawlers)):        
        try:
            website  = Crawler_Logs_Database.find_one({"Crawler_Name": crawler},{"WebSite":1})
        
            Today_Urls = Crawler_Logs_Database.find_one({"Crawler_Name": crawler,"runningDateTime":{"$gte":today_timestamp,'$lte':today_timestamp+timedelta(days=1)}},
            {'News_url':1,"runningDateTime":1})
            
            Yesterday_Urls = Crawler_Logs_Database.find_one({"Crawler_Name": crawler,"runningDateTime":{"$gte":today_timestamp-timedelta(days=1),'$lt':today_timestamp}},
            {'News_url':1,"runningDateTime":1})
            
            Today_Urls = Today_Urls['News_url']
            try:
                Yesterday_Urls = Yesterday_Urls['News_url']
            except:
                Yesterday_Urls = []

            Today_Crawled = [value for value in Today_Urls if value not in Yesterday_Urls]
            
            Latest_run = Crawler_Logs_Database.find({"Crawler_Name": crawler},{"runningDateTime":1}).sort("runningDateTime", -1)[0]

            Second_Latest_run = Crawler_Logs_Database.find({"Crawler_Name": crawler},{"runningDateTime":1}).sort("runningDateTime", -1).limit(2)[1]
            
            record = {"Crawler_Name":crawler, "Website":website["WebSite"], "Latest_run":Latest_run['runningDateTime'], "Second_Last_Run":Second_Latest_run["runningDateTime"], "Today_Crawled_Links":Today_Crawled, "Today_Crawled_Links_Count":str(len(Today_Crawled))}
            data.append(record)
        except Exception as e:
            print(e)

    # Convert data list to DataFrame
    df = pd.DataFrame(data)

    # Save DataFrame to Excel file
    excel_filename = f'EMR_Crawlers_Status_Sheet_{day}_{month}_{year}.xlsx'
    df.to_excel(excel_filename, index=False)

    success = upload_to_aws(excel_filename, 'data2images', excel_filename)

    # Check if the upload was successful
    if success:
        print(success)
        print(f"File uploaded to AWS S3: {excel_filename}")
    else:
        print("File upload failed.")

    # Optional: Remove the local Excel file after uploading
    os.remove(excel_filename)

    # For Email
    message = Mail(
    from_email='info@emr-online.com',
    to_emails=['manuel.gielsdorf@emr-online.com','abdul.ghaffar@techletspk.com','salman.ansari@techletspk.com','muhammad.asad@techletspk.com'],
    subject='EMR Crawlers Daily status Excel Sheet ',
    html_content=f'<strong>Kindly Download the Excel File From this link : </strong> {success}')
    try:
        sg = SendGridAPIClient("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")
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
 
if __name__ == "__main__": 
    process_Email()