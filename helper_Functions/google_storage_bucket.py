import sys
from google.cloud import storage

def get_bucket(bucket_name):
    storage_client = storage.Client.from_service_account_json(
        'my_credentials_file.json')

    # Make an authenticated API request
    buckets = list(storage_client.list_buckets())
    
    found = False
    for bucket in buckets:
        if bucket_name in bucket.name:
            found = True
            break

    if not found:
        print("Error: bucket not found")
        sys.exit(1)

    print(bucket)

    return bucket

def upload_file(bucket, fname):
    destination_blob_name = fname
    source_file_name = fname

    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )

if __name__ == "__main__":
    bucket = get_bucket('MyBucket')
    upload_file(bucket, 'testfile')