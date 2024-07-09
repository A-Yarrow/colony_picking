#import packages
from google.cloud import storage
#import google.cloud.storage as storage
import os

# set key credentials file path
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '.secrets/arc-gec-nlpp-73a4f89a054e.json'

#define function that creates the bucket
def create_bucket(bucket_name, storage_class='STANDARD', location='us-central1'):
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    bucket.storage_class = storage_class

    bucket = storage_client.create_bucket(bucket, location=location)
    #for duel-location buckets use location_type='multi-region'
    #for dual-lcation buckets and data_locations=[region_1, region_2]

    return f'Bucket{bucket.name} created with {bucket.storage_class} in {bucket.location}'

#Invoke Function
print(create_bucket('test_domo_storage_bucket', 'STANDARD', 'us-central1'))