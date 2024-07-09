
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../secrets/arc-gec-nlpp-73a4f89a054e.json'

gauth = GoogleAuth()
gauth.LoadCredentialsFile(GOOGLE_APPLICATION_CREDENTIALS)
drive = GoogleDrive(gauth)

drive_id = '17fwAjdx_Nn3lPZkoWJkQE_KGddFCmaR_'
upload_file = '../test.txt'
gfile = drive.CreateFile({'parents':[{'treamDriveID':drive_id, 'id':drive_id}]})
gfile.Upload(param={'supportsTeamDrives': True})#instance.gfile.SetContentFile(upload_file)
#gfile.Upload()