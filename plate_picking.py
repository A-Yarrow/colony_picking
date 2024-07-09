import os
from glob import glob
import math
import pandas as pd
import streamlit as st
import plotly.figure_factory as ff 
import plotly_express as px
import plotly.offline as pyo
import datetime
#import barcode
from barcode import Code39
from barcode.writer import ImageWriter
from io import BytesIO
from PIL import Image

def rowIndex(row):
	return row.name

def convert_qpix_wells(df, qtrey_rot_dict):
	df = df.rename(columns={'Source Region': 'Qpix Source Well'})
	df['Human Source Well'] = df['Qpix Source Well'].map(qtrey_rot_dict)
	df = df[['Source Barcode', 'Destination Barcode', 'Qpix Source Well', 'Human Source Well', 'Destination Well']]
	return df

#Look for the submission file with a specific experiment id
def find_submission_data(submission_dir, exp_id):	
	file_list = glob(f'{submission_dir}/{exp_id}_submission.csv')
	if len(file_list) == 1:
		df = pd.read_csv(file_list[0], converters={'Project ID':str})
		df = df.rename(columns={'Source Well':'Human Source Well'})
	elif len(file_list) != 1:
		return None
	return df

def add_buttons(submission_df, qpix_output):
	pass
	

def make_experiment_id(file_handle=None, manual_id=None):
	if manual_id == None and file_handle != None:
		with open(file_handle, 'r+') as f:
			lines = f.read().splitlines()
			print(lines)
			new_id = str(int(lines[-1])+1)
			f.write(new_id+'\n')
			exp_id = new_id.zfill(5)
		return exp_id
	elif file_handle == None and manual_id != None:
		return manual_id
	
def make_plate_list(df):

	colonies = 0
	total_colonies = []                 
	for row in df.itertuples():
		colonies += row[5] 
		total_colonies.append(colonies)
	df['total_colonies'] = total_colonies
	df['Destination Plate No.'] = df['total_colonies'].apply(lambda x: math.ceil(x/95))
	df.drop(['total_colonies'], axis=1)
	df_list = []
	plate_list = df['Destination Plate No.'].unique().tolist()
	for plate in plate_list:
		df_list.append(df[df['Destination Plate No.'] == plate])
                
	return df_list
			
# Converting links to html tags
def convert_images_html(path_to_image):
	return f'<img src={path_to_image} width = 60 >'

def machine_barcode(human_bc: str):
	image_path = 'barcode_images/'+human_bc+'.jpg'
	my_code39 = Code39(human_bc, writer=ImageWriter())
	img_bytes = BytesIO()
	my_code39.write(img_bytes)
	img = Image.open(img_bytes)
	img.save(image_path, "JPEG")
	return (image_path)


def generate_barcode(df, plate_type, exp_id):
	date_time = datetime.datetime.now()
	str_date_time = "-" + exp_id + "-" +date_time.strftime("%m%d%Y")
	barcode = df['Name'].str.split(' ').str[0].unique()[0][0]+df['Name'].str.split(' ').str[1].unique()[0][0]+'source'+str_date_time
	df['Source Barcode'] = barcode

	if plate_type == 'petri':
		df['Source Agar Plate No.'] = df.apply(rowIndex, axis=1)+1
	elif plate_type == 'qtrey':
		df['Source Agar Plate No.'] = df['Source Agar Plate Name'].str[2:]

	df['Source Agar Plate No.'] = df['Source Agar Plate No.'].astype(str)
	df['Source Agar Plate Barcode'] = (df['Source Barcode']+df['Source Agar Plate No.']).str.upper() # .apply(lambda x: Code39(x))
	df['Destination 96 Plate Barcode'] = df['Source Agar Plate Barcode'].str.replace('SOURCE', 'DEST').str.upper()+'-'+ df['Destination Plate No.'].astype(str)
	df['Destination Plate Name'] = df['Destination 96 Plate Barcode'].str[0:6]+ "-" + exp_id + "-" + df['Destination 96 Plate Barcode'].str[-1:]
	df_stamp = df.copy()
	df_stamp['Destination 96 Plate Barcode'] = df['Source Agar Plate Barcode'].str.replace('SOURCE', 'STAMP').str.upper() + '-' + df['Destination Plate No.'].astype(str)
	df_stamp['Destination Plate Name'] = df_stamp['Destination 96 Plate Barcode'].str[0:6]+ "-" + exp_id + "-" + df_stamp['Destination 96 Plate Barcode'].str[-1:]
	df = pd.concat([df, df_stamp], axis = 0, ignore_index=True)
	
	if plate_type == 'petri':
		df = df[['Name', 'Source Agar Plate Name', 'Source Agar Plate No.', 'No. Colonies', 'Source Agar Plate Barcode', 'Destination 96 Plate Barcode']]
	elif plate_type == 'qtrey':
		df = df[['Name', 'Sample Name', 'Source Agar Plate Name', 'Source Agar Plate No.','Source Well', 'No. Colonies', 'Source Agar Plate Barcode', 'Destination Plate No.', 'Destination 96 Plate Barcode', 'Destination Plate Name']]

	for i in ['Source Agar Plate Barcode', 'Destination 96 Plate Barcode']:
		d = {}
		d_image = {}
		for human_barcode in df[i].unique().tolist():
			img_path = machine_barcode(human_barcode)
			d_image[human_barcode] = img_path
			html_path = convert_images_html(img_path)
			d[human_barcode] = html_path
		df[i+'_image_path'] = df[i].map(d_image)
		df[i+'_machine'] = df[i].map(d)
	
	return df

def get_table_map(df):
	df['row'] = df['Destination Well'].apply(lambda x: x[0])
	df['col'] = df['Destination Well'].apply(lambda x: x[1:])
	df = df[['Source Barcode', 'Destination Barcode', 'row', 'col']]
	
	d = {}
	for i,j in enumerate(df['Source Barcode'].unique()):
		d[j] = float(i+1)
		df['key'] = df['Source Barcode'].map(d)
	table = pd.pivot_table(df, index = 'row', columns = 'col', values = 'key', aggfunc='median')
	table = table[['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']]
    
	#Make the Plate Map
	fig = px.imshow(table, text_auto=True)
	#Make it look nice.
	for row in [i+0.5 for i,j in enumerate(table.index.to_list())]:
		fig.add_hline(y=row, line_color = 'white')
	for col in [i+0.5 for i,j in enumerate(table.columns.to_list())]:
		fig.add_vline(x=col, line_color = 'white')
	fig = fig.update_xaxes(showgrid=False)
	fig = fig.update_yaxes(showgrid=False)
	
	return fig


