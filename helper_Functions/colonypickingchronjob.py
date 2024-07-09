#Combine Qpix submission form and Qpix output based on project number
#import packages
from google.cloud import storage
from glob import glob
import pandas as pd
import os

# set key credentials file path
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '.secrets/arc-gec-nlpp-73a4f89a054e.json'

def list_cs_files(bucket_name, handle):
    storage_client = storage.Client()

    file_list = storage_client.list_blobs(bucket_name)
    file_list = [file.name for file in file_list]
    file_list = [file for file in file_list if handle in file]

    return file_list



def main():
    bucket = 'colonhy-picking-dashboard' 
    output_files = list_cs_files(bucket, 'output.csv')
    submission_files = list_cs_files(bucket, 'submission.csv')
    print(submission_files)
    for submission in submission_files:
        for output in output_files:
            if submission.split('_')[0] == output.split('_')[0]: #If they have the same project ID
                print ('Combining %s with %s to produce merged file' %(submission, output))





if __name__ == "__main__":
    main()