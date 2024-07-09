#import packages
from google.cloud import storage
#from oauth2client.service_account import ServiceAccountCredentials
import os
from glob import glob
from dotenv import load_dotenv
from utils import export_csv
import pandas as pd
from io import StringIO

# set key credentials file path
load_dotenv()
STORAGE_BUCKET_NAME = os.getenv('STORAGE_BUCKET_NAME')
#os.environ[GOOGLE_APPLICATION_CREDENTIALS] = '/Users/yarrowm/projects/arcgec/colony_picking/.secrets/arc-gec-nlpp-73a4f89a054e.json')
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
#Read csv file into a stringIO object and write to cloud without making a file locally
def upload_cs_file(bucket_name, file_as_string, destination_file_name):
   
    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(destination_file_name)
        blob.upload_from_string(file_as_string, content_type = 'text/csv')
        print(f'File {destination_file_name} uploaded to {bucket_name}/{destination_file_name}.')
    except Exception as e:
        print(e)  
       
def upload_image_file(bucket_name, file, destination_file_name):

    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(destination_file_name)
        blob.upload_from_filename(file, content_type = 'image/jpeg')
        #blob.make_public()
        print(f'File {destination_file_name} uploaded to {bucket_name}/{destination_file_name}.')
    except Exception as e:
        print(e)

def list_cs_files(bucket_name, handle):
    storage_client = storage.Client()

    file_list = storage_client.list_blobs(bucket_name)
    file_list = [file.name for file in file_list]
    file_list = [file for file in file_list if handle in file]

    return file_list

#define a function that dowloads a file from the bucket
def download_cs_file(bucket_name, file_name, destination_file_name = 'Downloaded_file', ftype = 'file'):
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(file_name)
    
    if ftype == 'file':
        blob.download_to_filename(destination_file_name)
        return True
    
    elif ftype == 'string':
        blob = blob.download_as_string()
        blob = blob.decode('utf-8')
        blob = StringIO(blob)
        return blob


#upload_image_file(STORAGE_BUCKET_NAME, '../barcode_images/SDDEST-00298-111120232.jpg', 'test.jpg')    
"""test_df = pd.DataFrame.from_dict({"A":["A", "B", "C"], "B":["A", "B", "C"]})
buffer = export_csv(test_df)
upload_cs_file(STORAGE_BUCKET_NAME, buffer, 'text2.txt')

for file in glob(f'qpix_output/*qpix_test_output.csv'):
    upload_cs_file('colonhy-picking-dashboard', f'{file}', f'{file}')

for file in glob(f'submission_data/*submission.csv'):
    upload_cs_file('colonhy-picking-dashboard', f'{file}', f'{file}')

for file in glob(f'barcode_images/*jpg'):
                 upload_cs_file('colonhy-picking-dashboard', f'{file}', f'{file}')

upload_cs_file('colonhy-picking-dashboard', '.secrets/arc-gec-nlpp-73a4f89a054e.json', 'arc-gec-nlpp-73a4f89a054e.json')
"""