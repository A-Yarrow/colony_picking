import os
from io import StringIO, BytesIO
from glob import glob

def get_env_var(env_var):
    """
    Check whether environmental variable exists; return if yes
    """
    if env_var in os.environ:
        return os.environ[env_var]
    else:
        print(f"No value for {env_var} in env")
        quit(1)


def export_csv(df):
  with StringIO() as buffer:
    df.to_csv(buffer, index=False)
    return buffer.getvalue()

#Cleanup files in the app before each run 
def cleanup_files(directory, extension):
  d = glob(f'{directory}/*{extension}')
  if len(d) == 0:
    print('No files matching')
    return(1)
  else: 
    for file in d:
      os.remove(file)
      
#cleanup_files('./barcode_images', '.jpg')
