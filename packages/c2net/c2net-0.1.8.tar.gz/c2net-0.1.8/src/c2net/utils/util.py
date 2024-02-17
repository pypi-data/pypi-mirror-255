import os
import subprocess
import shutil
import datetime
from . import constants
def unzip_data(zipfile_path, unzipfile_path, data_download_method):
    unzip_success = False
    try:
        if zipfile_path.endswith(".tar.gz"):
            shutil.unpack_archive(zipfile_path, unzipfile_path, 'gztar')
            unzip_success = True
        elif zipfile_path.endswith(".zip"):
            shutil.unpack_archive(zipfile_path, unzipfile_path, 'zip')
            unzip_success = True
        else:
            print(f'\u274C The dataset is not in tar.gz or zip format!')
            unzip_success = False
    except Exception as e:
        print(f'\u274C Extraction failed for {zipfile_path}: {str(e)}')
        print(f'Please check the file is not encrypted or proceed with manual extraction.')
    finally:
        try:
            if data_download_method == constants.DATA_DOWNLOAD_METHOD_MOXING:
                os.remove(zipfile_path)
        except Exception as e:
            print(f'Deletion failed for {zipfile_path}: {str(e)},but this does not affect the operation of the program, you can ignore')
    return unzip_success
def is_directory_empty(path):
    """
    is directory empty
    """
    if len(os.listdir(path)) == 0:
        return True
    else:
        return False
def get_nonempty_subdirectories(directory):
    """
    get nonempty subdirectories
    """
    nonempty_subdirectories = []
    for entry in os.scandir(directory):
        if entry.is_dir():
            if any(os.scandir(entry.path)):
                nonempty_subdirectories.append(entry.name)
    return nonempty_subdirectories

def get_current_time():
    current_time = datetime.datetime.now()
    result = subprocess.run(['date', '+%Z'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timezone = result.stdout.strip()
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S") + f" {timezone}"
    return current_time_str