#import packages
from google.cloud import storage
from glob import glob
#import google.cloud.storage as storage
import os

# set key credentials file path
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '.secrets/arc-gec-nlpp-73a4f89a054e.json'

#define a function that dowloads a file from the bucket
def download_cs_file(bucket_name, file_name, destination_file_name):
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(file_name)
    blob.download_to_filename(destination_file_name)

    return True

#download_cs_file('colonhy-picking-dashboard', f'arc-gec-nlpp-73a4f89a054e.json', f'arc-gec-nlpp-73a4f89a054e.json')

