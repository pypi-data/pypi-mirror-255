import os
from .moxing_env_check import upload_folder
from ..utils import constants
def upload_c2net():
    """
    This function selects the appropriate method to upload output based on the data download method specified in the environment variables.
    If the data download method is not set or is unknown, a ValueError will be raised.
    """
    data_download_method = os.getenv(constants.DATA_DOWNLOAD_METHOD)
    if data_download_method is None:
        raise ValueError(f'Failed to obtain environment variables. Please set the {constants.DATA_DOWNLOAD_METHOD} environment variables.')
    if data_download_method == constants.DATA_DOWNLOAD_METHOD_MOXING:
        return upload_output_for_moxing()
    if data_download_method == constants.DATA_DOWNLOAD_METHOD_MOUNT:
        return upload_output_for_mount()
    raise ValueError(f'Unknown data download method: {data_download_method}')

def upload_output_for_moxing():
    """
    This function handles the uploading of output for the 'moxing' data download method.
    If the local output path or output URL is not set in the environment variables, a ValueError will be raised.
    If the local output path does not exist, it will be created.
    If the output URL is not empty, the local output path will be uploaded to the output URL.
    """
    local_output_path = str(os.getenv(constants.LOCAL_OUTPUT_PATH))
    output_url = str(os.getenv(constants.OUTPUT_URL))
    if output_url is None or local_output_path is None:
        raise ValueError(f'Failed to obtain environment variables. Please set the {constants.LOCAL_OUTPUT_PATH} and {constants.OUTPUT_URL} environment variables.')
    else:
        if not os.path.exists(local_output_path):
            os.makedirs(local_output_path) 
    if output_url:             
                upload_folder(local_output_path, output_url)
    return  local_output_path   
 
def upload_output_for_mount():
    """
    This function handles the uploading of output for the 'mount' data download method.
    If the local output path is not set in the environment variables, a ValueError will be raised.
    If the local output path does not exist, it will be created.
    """
    local_output_path = str(os.getenv(constants.LOCAL_OUTPUT_PATH))
    if local_output_path is None:
        raise ValueError(f'Failed to obtain environment variables. Please set the {constants.LOCAL_OUTPUT_PATH} environment variables.')
    else:
        if not os.path.exists(local_output_path):
            os.makedirs(local_output_path) 
    return  local_output_path 