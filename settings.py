#Settings for Colony Picking App

#DIRECTORIES
APP_DIRECTORIES = {'SUBMISSION_DIR':'./submission_data/',
                   'QPIX_OUTPUT_DIR':'./qpix_output',
                   'QPIX_OUTPUT_MERGED_DIR':'./qpix_output/merged',
                   'SUBMISSION_TEMPLATE_DIR':'./submission_templates/',
                   'BARCODE_DIR':'./barcode_images/',
                   'PLATE_LAYOUT_DIR':'./plate_layouts/',
                   }

#Sample Files
SAMPLE_FILES = {'SUBMISSION_TEMPLATE':'48_well_Qtrey_submission_template.csv',
                'QTREY_LABELING_IMAGE':'qtrey_labeling.png',
                'SUBMISSIONS_TRACKING_FILE':'submissions.txt'
                }

FILE_NAMING = {'QPIX_OUTPUT_EXT':'_qpix_output.csv',
               'QPIX_MERGED_EXT':'_qpix_merged.csv',
               'SUBMISSION_EXT':'_submission.csv'
               }

FILE_COLUMNS = {'QPIX_RAW_OUTPUT_COLUMNS':
                ['Source Barcode', 'Source Region', 'Feature Position X', 
                'Feature Position Y', 'Destination Barcode', 'Destination Well'
                ],
                'QTREY_SUBMISSION_OUTPUT_COLUMNS':
                ['Project ID', 'Name', 'Sample Name', 'Source Agar Plate Name',
                'Source Agar Plate No.',
                'Destination Plate No.', 'Source Well', 'No. Colonies', 'Source Agar Plate Barcode', 
                'Source Agar Plate Barcode_image_path', 'Destination 96 Plate Barcode', 
                'Destination 96 Plate Barcode_image_path', 'Destination Plate Name',
                'Buffer', 'Plasmids?'
                ],
                'QTREY_SUBMISSION_OUTPUT_COLUMNS_TO_MERGE':
                ['Project ID', 'Sample Name', 'Source Agar Plate Barcode', 
                'Human Source Well', 'Destination Plate Name'
                ],
                'QTREY_SUBMISSION_OUTPUT_COLUMNS_USER_DOWNLOAD':
                ['Project ID', 'Name', 'Sample Name', 'Source Agar Plate Name', 
                'Source Agar Plate No.', 'Destination Plate No.',
		        'Source Well', 'No. Colonies', 'Source Agar Plate Barcode', 
                'Destination 96 Plate Barcode', 'Destination Plate Name', 
                'Buffer', 'Plasmids?'
                ]
                }
                


#PLATE TRANSFORMATIONS
QTREY_ROT_90 = {'A1': 'A1','B1': 'A2','C1': 'A3','D1': 'A4','E1': 'A5','F1': 'A6',
             'A2': 'B1', 'B2': 'B2', 'C2': 'B3', 'D2': 'B4', 'E2': 'B5', 'F2': 'B6',
             'A3': 'C1', 'B3': 'C2', 'C3': 'C3', 'D3': 'C4', 'E3': 'C5', 'F3': 'C6',
             'A4': 'D1', 'B4': 'D2', 'C4': 'D3', 'D4': 'D4', 'E4': 'D5', 'F4': 'D6',
             'A5': 'E1', 'B5': 'E2', 'C5': 'E3', 'D5': 'E4', 'E5': 'E5', 'F5': 'E6',
             'A6': 'F1', 'B6': 'F2', 'C6': 'F3', 'D6': 'F4', 'E6': 'F5', 'F6': 'F6',
             'A7': 'G1', 'B7': 'G2', 'C7': 'G3', 'D7': 'G4', 'E7': 'G5', 'F7': 'G6',
             'A8': 'H1', 'B8': 'H2', 'C8': 'H3', 'D8': 'H4', 'E8': 'H5', 'F8': 'H6'}

QTREY_ROT_180 =  {'A1': 'H1', 'B1': 'H2', 'C1': 'H3', 'D1': 'H4', 'E1': 'H5', 'F1': 'H6',
                'A2': 'G1', 'B2': 'G2', 'C2': 'G3', 'D2': 'G4', 'E2': 'G5', 'F2': 'G6',
                'A3': 'F1', 'B3': 'F2', 'C3': 'F3', 'D3': 'F4', 'E3': 'F5', 'F3': 'F6',
                'A4': 'E1', 'B4': 'E2', 'C4': 'E3', 'D4': 'E4', 'E4': 'E5', 'F4': 'E6',
                'A5': 'D1', 'B5': 'D2', 'C5': 'D3', 'D5': 'D4', 'E5': 'D5', 'F5': 'D6',
                'A6': 'C1', 'B6': 'C2', 'C6': 'C3', 'D6': 'C4', 'E6': 'C5', 'F6': 'C6',
                'A7': 'B1', 'B7': 'B2', 'C7': 'B3', 'D7': 'B4', 'E7': 'B5', 'F7': 'B6',
                'A8': 'A1', 'B8': 'A2', 'C8': 'A3', 'D8': 'A4', 'E8': 'A5', 'F8': 'A6'}


