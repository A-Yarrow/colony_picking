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
					find_submission_data

from utils import get_env_var, export_csv, cleanup_files
from send_emails import send_email
from gcp_utils import upload_cs_file, upload_image_file, list_cs_files
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


st.title("Colony Picking Dashboard.")

def main():
	#Clean up old images
	extension = '.jpg'
	directory = BARCODE_DIR
	cleanup = cleanup_files(directory = directory, extension = extension)
	if cleanup is not None:
		print('Cannot find any %s files in %s' %(extension,directory))

	qpix_template_df = pd.read_csv(SUBMISSION_TEMPLATE_DIR+SUBMISSION_TEMPLATE_FILE, sep=',')
	qpix_template = st.sidebar.download_button(label = "Download 48-well Qtrey Submission Form",
			  data = convert_df(qpix_template_df),
			  file_name = SUBMISSION_TEMPLATE_FILE,
			  mime = "text/csv", 
		)
	#if qpix_template is not None:
	st.header('QPIX INPUT')	
	option = st.selectbox(
	label = "Please select whether picking from petri plates or 48-well Qtreys :sunglasses:",
	options = ('Petri Plates', '48-well Qtray'),
	index=None)
	st.write('You selected:', option)
	st.write('')

	buffer_options = st.selectbox('Choose a buffer', ['Tris pH 8.5', 'Water'])	
	if buffer_options:
		st.write("You selected:", buffer_options)

	plasmid_options = st.selectbox('Do You want Plasmid Preps?', ['Yes', 'No'])	
	if plasmid_options:
		st.write("You selected:", plasmid_options)	

	if option == 'Petri Plates':
		upload_file = st.file_uploader(label="Please Upload Petri dish colony picking submission form")
		if upload_file is not None:
			df = pd.read_csv(upload_file, delimiter=',')
			df_list = make_plate_list(df)
			for dframe in df_list:
				df2 = generate_barcode(dframe, plate_type = 'petri', exp_id = '00000')
				st.write(df2)
			st.download_button(
                        label = "Download as CSV",
                        data = convert_df(df2),
                        file_name = 'petri_plate_input.csv',
                        mime = "text/csv",
                        )

		upload_file2 = st.file_uploader(label="Please Upload QPIX output", key=2)
		if upload_file2 is not None:
			df_fig = pd.read_csv(upload_file2, header=11)
			fig = get_table_map(df_fig)
			st.plotly_chart(fig, use_container_width=True)                   	

	elif option == '48-well Qtray':
		st.subheader(body = ':red[Please Label your Qtray according to the following template]',
			     divider = "blue"
			    )
		st.subheader(body = "Qtrey is shown as viewed from above the agar bed looking down at the agar")

		st.text(body = "Inform us if you have an alternate labeling scheme")
		st.image(image = SUBMISSION_TEMPLATE_DIR+QTREY_LABELING_IMAGE, 
			caption = "Default Qtray Labeling", 
			width = 400,
			)
		columns = ['Name', 'Sample Name', 'Source Agar Plate Name', 'Source Well', 'No. Colonies']
		upload_file = st.file_uploader(label="Please Upload 48-well Qtray colony picking submission form")
		
		if upload_file is not None:
			df = pd.read_csv(upload_file, delimiter=",")
			st.write(df.head())
			try:
				df = df[columns]
			except KeyError:
				st.warning ("Please upload the submission form in csv format. Columns do not look right",
							icon = "⚠️"
				)
				st.write('csv should have the following column name:%s' %columns)

				return None

			#Get rid of any problem stings
			df['Sample Name'] = df['Sample Name'].str.replace('/', '-').str.replace(' ', '')
			df['Source Agar Plate Name'] = df['Source Agar Plate Name'].str.replace('/', '-').str.replace(' ', '')
			#If the file looks ok make a new experiment ID

			experiment_id = None
			experiment_id_option = st.selectbox(
				"Please select source of experiment id:",
				("Copied from Benchling", "Auto Generate"),
				index=None,
				placeholder="Select source of experiment id",
			)
			st.write('You slected:', experiment_id_option)
			if experiment_id_option == "Auto Generate":
				experiment_id = make_experiment_id(SUBMISSION_DIR+SUBMISSIONS_TRACKING_FILE)
			elif experiment_id_option == "Copied from Benchling":
				experiment_id = st.text_input(label="Enter Benchling Experiment ID")
				
			df_list = make_plate_list(df)
			#st.write(df_list)
			df_plate_list = []

			if experiment_id != None:
				for dframe in df_list:
					df2 = generate_barcode(dframe, plate_type = 'qtrey', exp_id = experiment_id)
					df_plate_list.append(df2)
		
				df_plates = pd.concat(df_plate_list, ignore_index=True)
				#df_plates = df_plates.sort_values(by=['Destination Plate Name'])
				df_plates['Buffer'] = buffer_options
				df_plates['Plasmids?'] = plasmid_options
				df_plates['Project ID'] = str(experiment_id)
				df_plates = df_plates[QTREY_SUBMISSION_OUTPUT_COLUMNS]
				df_plates = df_plates.sort_values(by=['Destination Plate Name'])
				print(df_plates)
			
			
				#df_plates.to_csv('test_submission.csv', index=False)
				#Submission button
				if st.button(label = 'SUBMIT SAMPLES'):
					#Send Samples to GCP storage
					df_as_string = export_csv(df_plates)
					bucket_name = STORAGE_BUCKET_NAME
					destination_file_name = experiment_id+SUBMISSION_EXT
					upload_cs_file(bucket_name = bucket_name, file_as_string = df_as_string,
							destination_file_name = destination_file_name)
					st.write('Thank you for your submission')
							
					#Send emails
					from_email = "GETC_ColonyPickingDashboard@arcinstitute.org"
					link = ('https://storage.googleapis.com/{bucket}/{file}').format(bucket=STORAGE_BUCKET_NAME, file=destination_file_name)
					to_emails = [('yarrowm@arcinstitute.org', 'Yarrow'),
					('janiceh@arcinstitute.org', 'Janice')]
					subject = 'New Qpix Submission'
					body = 'Thank You for submitting a Colony Picking Submission form. Your Project ID is %s Here is a link to the submission form %s' %(experiment_id, link)
					send_email(from_email, to_emails, subject, body)
			
					st.subheader('', divider = 'blue')
					#df_plates_html = df_plates.to_html(escape=False, formatters = {'Source Agar Plate Barcode_image_path':convert_images_html})
			
					df_plates_view = df_plates[QTREY_SUBMISSION_OUTPUT_COLUMNS_USER_DOWNLOAD]
					df_plates_view = df_plates_view.sort_values('Destination Plate No.')
					st.write(df_plates_view)
					#st.markdown(df2_html, unsafe_allow_html=True)
					st.download_button(
					label = "Download qtrey input as CSV",
					data = convert_df(df_plates_view),
					file_name = f'{experiment_id}{SUBMISSION_EXT}',
					mime = "text/csv",
					)

					#Plate Barcodes
					unique_source_barcodes = df_plates['Source Agar Plate Barcode_image_path'].unique().tolist()
					unique_destination_barcodes = df_plates['Destination 96 Plate Barcode_image_path'].unique().tolist()
			
					for i,j in enumerate(unique_source_barcodes):
						st.image(j, caption='Source Agar Plate Barcode')
						with open(j, "rb") as file:
							btn = st.download_button(
									'Download source plate barcode',
									data=file,
									file_name='Source Barcode+%s'%(i), 
									key=j+str(i), 
									mime="image/jpeg")
			
			
					for i,j in enumerate(unique_destination_barcodes):
						st.image(j, caption='Destination Plate Barcode')
						with open(j, "rb") as file:
							btn2 = st.download_button(
									'Download destination plate barcode',
									data=file,
									file_name='Destination Barcode_%s'%(i),
									key=j+str(i),
									mime="image/jpeg")
		
				#Send images to google cloud
				for file in glob(f'barcode_images/*.jpg'):
					upload_image_file('colonhy-picking-dashboard', f'{file}', f'%s_{file}'%experiment_id)

			
if __name__ == "__main__":
    main()
