import os
import boto3
import openpyxl
import pandas as pd
from io import BytesIO
from bson import ObjectId
from pymongo import MongoClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from openpyxl.styles import PatternFill
from datetime import datetime, timedelta
from botocore.exceptions import NoCredentialsError



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

    current_datetime = datetime.now()
    year = current_datetime.year
    month = current_datetime.month
    day = current_datetime.day

    # Create a datetime object for today's date
    today_timestamp = datetime(year, month, day)

    # Connect to MongoDB
    myclient = MongoClient("mongodb://su-du-ad:updatedSuperDuperAdmin@34.121.98.98:27017/emrweb?authSource=admin")
    MyDatabase = myclient["emrweb"]
    Histories_Database = MyDatabase["histories"]

    Companies_Name_Database = MyDatabase["companies"]

    Companies = Histories_Database.distinct("companyId.value")

    Data = []
    for company in Companies:

        Company_Name = Companies_Name_Database.find_one({"_id": company}, {"validatedObject.companyNameObject": 1 })

        Yesterday_News_In = Histories_Database.find_one({"companyId.value": company , "announcement.addedOn":{"$gte":today_timestamp-timedelta(days=1),'$lt':today_timestamp}}, {"announcement.addedOn": 1})
        
        if Yesterday_News_In is None:
            News = False 
        else:
            News = True

        Last_3_Days = Histories_Database.find_one({"companyId.value": company , "announcement.addedOn":{"$gte":today_timestamp-timedelta(days=3),'$lt':today_timestamp}}, {"announcement.addedOn": 1})
        
        if Last_3_Days is None:
            L_3_Days = False 
        else:
            L_3_Days = True

        Last_7_Days = Histories_Database.find_one({"companyId.value": company , "announcement.addedOn":{"$gte":today_timestamp-timedelta(days=7),'$lt':today_timestamp}}, {"announcement.addedOn": 1})
        
        if Last_7_Days is None:
            L_7_Days = False 
        else:
            L_7_Days = True

        Last_30_Days = Histories_Database.find_one({"companyId.value": company , "announcement.addedOn":{"$gte":today_timestamp-timedelta(days=30),'$lt':today_timestamp}}, {"announcement.addedOn": 1})
        
        if Last_30_Days is None:
            L_30_Days = False 
        else:
            L_30_Days = True

        try:
            anouncement = Histories_Database.find({"$expr": {"$eq": [{"$size": "$companyId.value"}, 1]},"companyId.value": company}, {"companyId.value": 1, "references.source.value": 1 , "announcement.addedOn": 1}).sort("announcement.addedOn", -1)[0]

        except Exception as e:
            try:
                anouncement = Histories_Database.find({"companyId.value": company}, {"companyId.value": 1, "announcement.addedOn": 1}).sort("announcement.addedOn", -1)[0]
            except Exception as e:
                print (e)


        try:
            Record = {"Company_Name": Company_Name["validatedObject"]["companyNameObject"],"Yesterday_News_In": News , "Last_3_Days": L_3_Days , "Last_7_Days": L_7_Days , "Last_30_Days": L_30_Days , "Last_Crawled":anouncement["announcement"]["addedOn"].strftime("%Y-%m-%d")}
            Data.append(Record)
            # print(Record)
        except Exception as e:
            # print(anouncement["references"])
            print(company)
            print(e)
            

    df = pd.DataFrame(Data)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        writer.save()

    # Step 2: Use openpyxl to read this in-memory file
    output.seek(0)  # Important: go back to the beginning of the BytesIO object
    wb = openpyxl.load_workbook(output)
    sheet = wb.active
    
    # Define the fill colors
    green_fill = PatternFill(start_color="00FF00", end_color="00FF00", fill_type="solid")
    red_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")

    # Applying the conditions using pandas for better performance
    # Fill 'Yesterday_News_In' and 'Last_3_Days' with green if True
    df['Yesterday_News_In_green'] = df['Yesterday_News_In'].apply(lambda x: True if x else False)
    df['Last_3_Days_green'] = df['Last_3_Days'].apply(lambda x: True if x else False)

    # Fill 'Last_30_Days' with red if 'Yesterday_News_In', 'Last_3_Days', and 'Last_7_Days' are all False
    df['Last_30_Days_red'] = df.apply(lambda row: True if not any([row['Yesterday_News_In'], row['Last_3_Days'], row['Last_7_Days']]) else False, axis=1)

    # Apply the colors in the Excel sheet
    for i, row in df.iterrows():
        excel_row = i + 2  # Adding 2 because Excel rows start at 1 and we skip the header row
        if row['Yesterday_News_In_green']:
            sheet.cell(excel_row, 2).fill = green_fill
        if row['Last_3_Days_green']:
            sheet.cell(excel_row, 3).fill = green_fill
        if row['Last_30_Days_red']:
            sheet.cell(excel_row, 5).fill = red_fill

    # Save the modified workbook
    excel_filename = f'EMR_Crawlers_Status_Sheet_Testing_{day}_{month}_{year}.xlsx'
    wb.save(excel_filename)

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
    subject='EMR Crawlers Daily status V2 Excel Sheet',
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