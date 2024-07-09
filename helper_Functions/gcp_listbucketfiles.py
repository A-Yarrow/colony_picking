#import packages
from google.cloud import storage
from glob import glob
#import google.cloud.storage as storage
import os

# set key credentials file path
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '.secrets/arc-gec-nlpp-73a4f89a054e.json'

def list_cs_files(bucket_name, handle):
    storage_client = storage.Client()

    file_list = storage_client.list_blobs(bucket_name)
    file_list = [file.name for file in file_list]
    file_list = [file for file in file_list if handle in file]

    return file_list

#print(list_cs_files(bucket_name='colonhy-picking-dashboard', handle='output.csv'))
