#QPIX OUTPUT Script authored by Yarrow Madrona
import pandas as pd
import math
from glob import glob
import streamlit as st
import plotly_express as px
import datetime
from barcode import Code39
import os
import sys
from io import BytesIO
from io import StringIO
from PIL import Image
import configparser
import smtplib
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName,
    FileType, Disposition, ContentId)
from sendgrid import SendGridAPIClient
from io import StringIO
from google.cloud import storage
from dotenv import load_dotenv

#Append paths
sys.path.append('helper_functions')

#Import modules
import settings
from plate_picking import make_plate_list, generate_barcode, machine_barcode, get_table_map, convert_images_html, make_experiment_id,\
					find_submission_data, convert_qpix_wells

from utils import get_env_var, export_csv, cleanup_files
from send_emails import send_email
from gcp_utils import upload_cs_file, upload_image_file, list_cs_files, download_cs_file
from streamlit_helper_functions import convert_df

#Plate Rotations
QTREY_ROT_90 = settings.QTREY_ROT_90
QTREY_ROT_180 = settings.QTREY_ROT_180

#Directories
SUBMISSION_DIR = settings.APP_DIRECTORIES['SUBMISSION_DIR']
QPIX_OUTPUT_DIR = settings.APP_DIRECTORIES['QPIX_OUTPUT_DIR']
QPIX_OUTPUT_MERGED_DIR = settings.APP_DIRECTORIES['QPIX_OUTPUT_MERGED_DIR']
SUBMISSION_TEMPLATE_DIR = settings.APP_DIRECTORIES['SUBMISSION_TEMPLATE_DIR']
BARCODE_DIR = settings.APP_DIRECTORIES['BARCODE_DIR']
PLATE_LAYOUT_DIR = settings.APP_DIRECTORIES['PLATE_LAYOUT_DIR']

#Sample Files
SUBMISSION_TEMPLATE_FILE = settings.SAMPLE_FILES['SUBMISSION_TEMPLATE']
SUBMISSIONS_TRACKING_FILE = settings.SAMPLE_FILES['SUBMISSIONS_TRACKING_FILE']
QTREY_LABELING_IMAGE = settings.SAMPLE_FILES['QTREY_LABELING_IMAGE']

#File Extension Names
QPIX_OUTPUT_EXT = settings.FILE_NAMING['QPIX_OUTPUT_EXT']
QPIX_MERGED_EXT = settings.FILE_NAMING['QPIX_MERGED_EXT']
SUBMISSION_EXT = settings.FILE_NAMING['SUBMISSION_EXT']

#File Columns
QPIX_RAW_OUTPUT_COLUMNS = settings.FILE_COLUMNS['QPIX_RAW_OUTPUT_COLUMNS']
QTREY_SUBMISSION_OUTPUT_COLUMNS = settings.FILE_COLUMNS['QTREY_SUBMISSION_OUTPUT_COLUMNS']
QTREY_SUBMISSION_OUTPUT_COLUMNS_TO_MERGE = settings.FILE_COLUMNS['QTREY_SUBMISSION_OUTPUT_COLUMNS_TO_MERGE']
QTREY_SUBMISSION_OUTPUT_COLUMNS_USER_DOWNLOAD = settings.FILE_COLUMNS['QTREY_SUBMISSION_OUTPUT_COLUMNS_USER_DOWNLOAD']

TO_EMAILS = ('yarrowm@arcinstitute.org', 'janiceh@arcinstitute.org')
#SECRETS
if os.path.isfile('.env'):
	load_dotenv()
	SENDGRID_API_KEY = get_env_var('SENDGRID_API_KEY')
	STORAGE_BUCKET_NAME = os.getenv('STORAGE_BUCKET_NAME')
	GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS') 	

def picking_output():
    st.text("")
    st.header("QPIX OUTPUT", divider='blue')

    qpix_orientation = st.selectbox(
        "Please Select QTrey plate orientation. :red[Please do not change from the default unless you know what you are doing]",
        ("DEFAULT ORIENTATION", "ROT_90"),
        key = 'Qtray orientation')
    orientation = QTREY_ROT_180				 
    if qpix_orientation == "DEFAULT ORIENTATION":
        orientation = QTREY_ROT_90

    st.subheader("SELECTING THE QPIX OUTPUT FILE", divider='green')
    #plate_list = sorted(glob(QPIX_OUTPUT_DIR+'*qpix*output.csv'))
    plate_list = list_cs_files(STORAGE_BUCKET_NAME, 'output.csv')

    qpix_output_file = st.selectbox(
                label='Please Select qpix output file that matches your experiment id', 
                options = plate_list,
                index = 0,
                key = 'qpix_output_file',
                )
    if qpix_output_file == '00001_qpix_test_output.csv':
        qpix_output_file = None

    if qpix_output_file is not None:
        st.write('You selected:', qpix_output_file)

    upload = None
    upload_file2 = st.file_uploader(label="Or Upload your own Qpix qtrey picking output", key='qpix_output')
    if qpix_output_file is not None and upload_file2 is None:
        upload = qpix_output_file
    elif qpix_output_file is None and upload_file2 is not None:
        upload = upload_file2

    if upload is not None:
        st.write(upload)
        df_qpix_raw = download_cs_file(STORAGE_BUCKET_NAME, upload, ftype = 'string')
        df_qpix_raw = pd.read_csv(df_qpix_raw, header=11)
        st.write(df_qpix_raw.head())
        try:
            df_qpix_raw = df_qpix_raw[QPIX_RAW_OUTPUT_COLUMNS]
        except KeyError:
            st.warning ('Please upload the QPIX raw output in csv format. Columns do not look right. Columns should be: %s' %QPIX_RAW_OUTPUT_COLUMNS,
                        icon = "⚠️"
            )
            return None
        
        if len(df_qpix_raw) > 0:
            df_qpix_convert = convert_qpix_wells(df_qpix_raw, orientation)
            idx = df_qpix_convert['Source Barcode'].iloc[0].find('-')
            exp_id = df_qpix_convert['Source Barcode'].iloc[0][idx+1:idx+6]
            df_qpix_convert['Project ID'] = str(exp_id)
            st.text('Your experiment id is: %s' %exp_id)
        else:
            st.write("Looks like this file is empty")
            return None

        #Find submission file through the experiment id in the output file
        st.subheader("SELECTING THE SUBMISSION FILE", divider = 'green')
        st.text("Our gnomes 🍄🧙‍♂️ are looking for your output submission file for experiment %s" %exp_id)
        st.text("Please wait.....")

        df_submission = find_submission_data(submission_dir=SUBMISSION_DIR, exp_id = exp_id)
        if df_submission is not None:
            st.write('Success! We found the output submission file for exp id: %s' %exp_id)
            st.write("The final qpix output merged with submission file samples should appear below")
            
        #If we cannot find the submission file, ask the user to upload their own
        if df_submission is None:
            submission_file_upload = st.file_uploader(label='The submission form for experiment id: %s was not found, please upload your own'%exp_id,
                                                        key='qpix_submission')
            if submission_file_upload is not None:
                df_submission = pd.read_csv(submission_file_upload, delimiter=',', converters={'Project ID':str})
                try: 
                    df_submission = df_submission[QTREY_SUBMISSION_OUTPUT_COLUMNS]
                except KeyError:
                    st.warning ('Please upload the output submission form in csv format. Columns do not look right. Columns should be: %s' %QTREY_SUBMISSION_OUTPUT_COLUMNS,
                                icon = "⚠️"
                                )
                    return None
                df_submission = df_submission.rename(columns={'Source Well':'Human Source Well'})
        
        if df_submission is not None:	
            #Test that the barcodes are the same
            if str(df_qpix_convert['Project ID'].loc[0]) != str(df_submission['Project ID'].loc[0]):
                st.warning ("Warning: The two files do not have the same Source Agar Plate Barcode. Cannot continue",
                            icon = "⚠️"
                )
                return None
            
            df_merge = df_qpix_convert.merge(df_submission[QTREY_SUBMISSION_OUTPUT_COLUMNS_TO_MERGE], left_on = ['Human Source Well', 'Source Barcode', 'Project ID'],
                        right_on = ['Human Source Well', 'Source Agar Plate Barcode', 'Project ID'], how = 'left')
            
            if len(df_merge) == 0:
                st.warning ("Warning: The two files do not have the same barcodes. Cannot continue",
                            icon = "⚠️"
                )
                return None
            df_merge.drop_duplicates(inplace=True)
            #Replace below with a saving to GCP bucket
            #df_merge.to_csv(QPIX_OUTPUT_MERGED_DIR+'_'+exp_id+QPIX_MERGED_EXT, index=False)
            df_merge = df_merge.sort_values(by=['Destination Plate Name', 'Human Source Well'])
            download = df_merge.drop(columns = 'Qpix Source Well', axis = 1).rename(columns = {'Human Source Well':'Qtray Source Well'})
            st.write(download)

            st.download_button(
            label = "Downlaod qtrey output as CSV",
            data = convert_df(download),
            file_name = '%s_qpix_merged_output.csv' %exp_id,
            mime = "text/csv",
        )
def main():
    picking_output()

if __name__ == "__main__":
    main()