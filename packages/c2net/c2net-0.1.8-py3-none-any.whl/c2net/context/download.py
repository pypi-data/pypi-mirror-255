import os
import glob
from .moxing_env_check import code_to_env, dataset_to_env, pretrain_to_env
from ..utils.util import unzip_data, is_directory_empty, get_nonempty_subdirectories, get_current_time
from ..utils import constants

def prepare_code():
    """
    This function prepares the code based on the data download method specified in the environment variables.
    If the data download method is not set or is unknown, a ValueError will be raised.
    """
    data_download_method = os.getenv(constants.DATA_DOWNLOAD_METHOD)
    if data_download_method is None:
        raise ValueError(f'\u274C Failed to obtain environment variables. Please set the {constants.DATA_DOWNLOAD_METHOD} environment variables.')
    if data_download_method == constants.DATA_DOWNLOAD_METHOD_MOXING:
        return prepare_code_for_moxing(data_download_method)
    if data_download_method == constants.DATA_DOWNLOAD_METHOD_MOUNT:
        return prepare_code_for_mount(data_download_method)
    raise ValueError(f'\u274C Unknown data download method: {data_download_method}')

def prepare_dataset():
    """
    This function prepares the dataset based on the data download method specified in the environment variables.
    If the data download method is not set or is unknown, a ValueError will be raised.
    """
    data_download_method = os.getenv(constants.DATA_DOWNLOAD_METHOD)
    if data_download_method is None:
        raise ValueError(f'\u274C Failed to obtain environment variables. Please set the {constants.DATA_DOWNLOAD_METHOD} environment variables.')
    if data_download_method == constants.DATA_DOWNLOAD_METHOD_MOXING:
        return prepare_dataset_for_moxing(data_download_method)
    if data_download_method == constants.DATA_DOWNLOAD_METHOD_MOUNT:
        return prepare_dataset_for_mount(data_download_method)
    raise ValueError(f'\u274C Unknown data download method: {data_download_method}')

def prepare_pretrain_model():
    """
    This function prepares the pre-trained model based on the data download method specified in the environment variables.
    If the data download method is not set or is unknown, a ValueError will be raised.
    """
    data_download_method = os.getenv(constants.DATA_DOWNLOAD_METHOD)
    if data_download_method is None:
        raise ValueError(f'\u274C Failed to obtain environment variables. Please set the {constants.DATA_DOWNLOAD_METHOD} environment variables.')
    if data_download_method == constants.DATA_DOWNLOAD_METHOD_MOXING:
        return prepare_pretrain_model_for_moxing(data_download_method)
    if data_download_method == constants.DATA_DOWNLOAD_METHOD_MOUNT:
        return prepare_pretrain_model_for_mount(data_download_method)
    raise ValueError(f'\u274C Unknown data download method: {data_download_method}')

def prepare_output_path():
    """
    This function prepares the output path based on the local output path specified in the environment variables.
    If the local output path is not set, a ValueError will be raised.
    """
    local_output_path = os.getenv(constants.LOCAL_OUTPUT_PATH)
    if local_output_path is None:
            raise ValueError(f'\u274C Failed to obtain environment variables. Please set the {constants.LOCAL_OUTPUT_PATH} environment variables.')
    else:	
        if not os.path.exists(local_output_path):	
            os.makedirs(local_output_path)   
    print(f'please set c2net_context.output_path as the output location')
    return local_output_path

def prepare_code_for_moxing(data_download_method):
    """
    This function prepares the code for the 'moxing' data download method.
    It gets the code URL and local code path from the environment variables.
    If the local code path is not set, a ValueError will be raised.
    If the local code path does not exist, it will be created.
    If the code URL is not empty, the code will be downloaded to the local code path.
    """
    code_url = os.getenv(constants.CODE_URL)
    local_code_path= os.getenv(constants.LOCAL_CODE_PATH)
    code_need_unzip= os.getenv(constants.CODE_NEED_UNZIP, constants.CODE_NEED_UNZIP_FALSE)
    if local_code_path is None:
        raise ValueError(f'\u274C Failed to obtain environment variables. Please set the {constants.LOCAL_CODE_PATH} environment variables.')
    else:
        if not os.path.exists(local_code_path):
            os.makedirs(local_code_path) 
    code_cache_file_path = os.path.join(local_code_path, ".code_cache_file")
    if not os.path.exists(code_cache_file_path):            
        if code_url != "":
            code_to_env(code_url, local_code_path, code_need_unzip, data_download_method)
    else:
        print(f'Detected .code_cache_file already exists, code has been prepared!')            
    return local_code_path

def prepare_dataset_for_moxing(data_download_method):
    """
    This function prepares the dataset for the 'moxing' data download method.
    It gets the dataset URL and local dataset path from the environment variables.
    If the dataset URL or local dataset path is not set, a ValueError will be raised.
    If the local dataset path does not exist, it will be created.
    If the dataset URL is not empty, the dataset will be downloaded to the local dataset path.
    """
    dataset_url = os.getenv(constants.DATASET_URL)
    local_dataset_path = os.getenv(constants.LOCAL_DATASET_PATH)
    dataset_need_unzip= os.getenv(constants.DATASET_NEED_UNZIP, constants.DATASET_NEED_UNZIP_FALSE)

    if dataset_url is None or local_dataset_path is None:
        raise ValueError(f'\u274C Failed to obtain environment variables.Please set the {constants.DATASET_URL} and {constants.LOCAL_DATASET_PATH} environment variables')
    else:
        if not os.path.exists(local_dataset_path):
            os.makedirs(local_dataset_path)
    dataset_cache_file_path = os.path.join(local_dataset_path, ".dataset_cache_file")
    if not os.path.exists(dataset_cache_file_path):  
        if dataset_url == '[]' or not dataset_url:  
            print(f'No dataset selected')  
        else:
            dataset_to_env(dataset_url, local_dataset_path, dataset_need_unzip, data_download_method)   
    else:
        print(f'Detected .dataset_cache_file already exists, dataset has been prepared!')   
    return local_dataset_path

def prepare_pretrain_model_for_moxing(data_download_method):
    """
    This function prepares the pre-trained model for the 'moxing' data download method.
    It gets the pre-trained model URL and local pre-trained model path from the environment variables.
    If the pre-trained model URL or local pre-trained model path is not set, a ValueError will be raised.
    If the local pre-trained model path does not exist, it will be created.
    If the pre-trained model URL is not empty, the pre-trained model will be downloaded to the local pre-trained model path.
    """
    pretrain_model_url = os.getenv(constants.PRETRAIN_MODEL_URL)
    local_pretrain_model_path= os.getenv(constants.LOCAL_PRETRAIN_MODEL_PATH)
    pretrain_model_need_unzip= os.getenv(constants.PRETRAIN_MODEL_NEED_UNZIP, constants.PRETRAIN_MODEL_NEED_UNZIP_FALSE)
    if pretrain_model_url is None or local_pretrain_model_path is None:
        raise ValueError(f'\u274C Failed to obtain environment variables. Please set the {constants.PRETRAIN_MODEL_URL} and {constants.LOCAL_PRETRAIN_MODEL_PATH} environment variables.')
    else:
        if not os.path.exists(local_pretrain_model_path):
            os.makedirs(local_pretrain_model_path) 
    pretrainmodel_cache_file_path = os.path.join(local_pretrain_model_path, ".pretrainmodel_cache_file")
    if not os.path.exists(pretrainmodel_cache_file_path):  
        if pretrain_model_url == '[]' or not pretrain_model_url:             
            print(f'No pretrainmodel selected')
        else:
            pretrain_to_env(pretrain_model_url, local_pretrain_model_path, pretrain_model_need_unzip, data_download_method)        
    else:
        print(f'Detected .pretrainmodel_cache_file already exists, pretrainmodel has been prepared!')   
    return local_pretrain_model_path   

def prepare_code_for_mount(data_download_method):
    """
    This function prepares the code for the 'mount' data download method.
    It gets the local code path and code unzip need from the environment variables.
    If the local code path is not set, a ValueError will be raised.
    If the local code path does not exist, it will be created.
    If the code directory is not empty, it is considered that the mount is successful.
    If the code needs to be unzipped, it will unzip the .zip or .tar.gz files in the code directory.
    """
    unzip_success = False
    local_code_path= os.getenv(constants.LOCAL_CODE_PATH)
    code_need_unzip = os.getenv(constants.CODE_NEED_UNZIP, constants.CODE_NEED_UNZIP_FALSE)
    if local_code_path is None:
        raise ValueError(f'\u274C Failed to obtain environment variables. Please set the {constants.LOCAL_CODE_PATH} environment variables.')
    else:
        if not os.path.exists(local_code_path):
            os.makedirs(local_code_path) 
    if is_directory_empty(local_code_path) == False:
        mount_success = True
    else:
        mount_success = False  
    code_cache_file_path = os.path.join(local_code_path, ".code_cache_file")
    if not os.path.exists(code_cache_file_path):
        all_code_copied = True
        if code_need_unzip == constants.CODE_NEED_UNZIP_TRUE:
            try:
                path = os.path.join(local_code_path, "*")
                for filename in glob.glob(path):
                    if filename.endswith('master.zip'):
                        print(f'Start preparing the code ...')
                        unzip_success = unzip_data(filename, local_code_path, data_download_method)
                        if mount_success & unzip_success:
                            print(f'\u2705 Completed preparing the code')
            except Exception as e:
                print(f'\u274C Failed Prepare Code : {str(e)}')
                all_code_copied = False
        else:
            if mount_success:
                print(f'Start preparing the code ...')
                print(f'\u2705 Completed preparing the code')
        if all_code_copied:
            current_time_str = get_current_time()
            file_content = 'This is a code cache file used to indicate that the code preparation is complete. Please do not delete this file. Unless you want to overwrite the code or fetch the code again. Execution time: ' + current_time_str
            with open(code_cache_file_path, 'w') as f:
                f.write(file_content)
    else:
        print(f'Detected .code_cache_file already exists, code has been prepared!') 
    return local_code_path

def prepare_dataset_for_mount(data_download_method):
    """
    This function prepares the dataset for the 'mount' data download method.
    It gets the local dataset path and dataset unzip need from the environment variables.
    If the local dataset path is not set, a ValueError will be raised.
    """
    unzip_success = False
    local_dataset_path = os.getenv(constants.LOCAL_DATASET_PATH)
    dataset_need_unzip = os.getenv(constants.DATASET_NEED_UNZIP, constants.DATASET_NEED_UNZIP_FALSE)
    if local_dataset_path is None :
        raise ValueError(f'\u274C Failed to obtain environment variables. Please set the {constants.LOCAL_DATASET_PATH} environment variables.')
    else:
        if not os.path.exists(local_dataset_path):
            os.makedirs(local_dataset_path)
    if is_directory_empty(local_dataset_path) == False:
        mount_success = True
    else:
        mount_success = False        

    dataset_cache_file_path = os.path.join(local_dataset_path, ".dataset_cache_file")
    if not os.path.exists(dataset_cache_file_path):      
        all_datasets_copied = True  
        if dataset_need_unzip == constants.DATASET_NEED_UNZIP_TRUE:
            try:
                file_list = os.listdir(local_dataset_path)
                for filename in file_list:
                    if filename.endswith('.tar.gz'):
                        folder_name = os.path.splitext(os.path.splitext(os.path.basename(filename))[0])[0]
                        unzipfile_path = local_dataset_path + "/" + folder_name
                        print(f'Start preparing the dataset {folder_name} ...')
                        unzip_success = unzip_data(os.path.join(local_dataset_path, filename), unzipfile_path, data_download_method)
                        if mount_success & unzip_success:
                            print(f'\u2705 Completed preparing the dataset {folder_name}')
                    elif filename.endswith('.zip'):
                        folder_name = os.path.splitext(os.path.basename(filename))[0]
                        unzipfile_path = local_dataset_path + "/" + folder_name
                        print(f'Start preparing the dataset {folder_name} ...')
                        unzip_success = unzip_data(os.path.join(local_dataset_path, filename), unzipfile_path, data_download_method)
                        if mount_success & unzip_success:
                            print(f'\u2705 Completed preparing the dataset {folder_name}')
            except Exception as e:
                print(f'\u274C Failed Prepare Dataset: {str(e)}')
                all_datasets_copied = False
        else:
            if mount_success:
                nonempty_subdirectories_list = get_nonempty_subdirectories(local_dataset_path)
                for subdirectory in nonempty_subdirectories_list:
                    print(f'\u2705 Completed preparing the dataset {subdirectory}')
        if all_datasets_copied:
            current_time_str = get_current_time()
            file_content = 'This is a dataset cache file used to indicate that the dataset preparation is complete. Please do not delete this file. Unless you want to overwrite the dataset or fetch the dataset again. Execution time: ' + current_time_str
            with open(dataset_cache_file_path, 'w') as f:
                f.write(file_content)
    else:
        print(f'Detected .dataset_cache_file already exists, dataset has been prepared!')
    return local_dataset_path    

def prepare_pretrain_model_for_mount(data_download_method):
    """
    This function prepares the pre-trained model for the 'mount' data download method.
    It gets the local pre-trained model path and pre-trained model unzip need from the environment variables.
    If the local pre-trained model path is not set, a ValueError will be raised.
    If the local pre-trained model path does not exist, it will be created.
    If the pre-trained model directory is not empty, it is considered that the mount is successful.
    If the pre-trained model needs to be unzipped, it will unzip the .zip or .tar.gz files in the pre-trained model directory.
    """
    unzip_success = False
    local_pretrain_model_path= os.getenv(constants.LOCAL_PRETRAIN_MODEL_PATH)
    pretrain_model_need_unzip = os.getenv(constants.PRETRAIN_MODEL_NEED_UNZIP, constants.PRETRAIN_MODEL_NEED_UNZIP_FALSE)
    if local_pretrain_model_path is None:
        raise ValueError(f'\u274C Failed to obtain environment variables. Please set the {constants.LOCAL_PRETRAIN_MODEL_PATH} environment variables.')
    else:
        if not os.path.exists(local_pretrain_model_path):
            os.makedirs(local_pretrain_model_path) 
    if is_directory_empty(local_pretrain_model_path) == False:
        mount_success = True
    else:
        mount_success = False 
    pretrainmodel_cache_file_path = os.path.join(local_pretrain_model_path, ".pretrainmodel_cache_file")
    if not os.path.exists(pretrainmodel_cache_file_path):     
        all_pretrainmodels_copied = True
        if pretrain_model_need_unzip == constants.PRETRAIN_MODEL_NEED_UNZIP_TRUE:
            try:
                file_list = os.listdir(local_pretrain_model_path)
                for filename in file_list:
                    if filename.endswith('.tar.gz'):
                        folder_name = os.path.splitext(os.path.splitext(os.path.basename(filename))[0])[0]
                        unzipfile_path = local_pretrain_model_path + "/" + folder_name
                        print(f'Start preparing the pretrainmodel {folder_name} ...')
                        unzip_success = unzip_data(os.path.splitext(local_pretrain_model_path,filename), unzipfile_path, data_download_method)
                        if mount_success & unzip_success:
                            print(f'\u2705 Completed preparing the pretrainmodel:{folder_name}')
                    elif filename.endswith('.zip'):
                        folder_name = os.path.splitext(os.path.basename(filename))[0]
                        unzipfile_path = local_pretrain_model_path + "/" + folder_name
                        print(f'Start preparing the pretrainmodel {folder_name} ...')
                        unzip_success = unzip_data(os.path.splitext(local_pretrain_model_path,filename), unzipfile_path, data_download_method)
                        if mount_success & unzip_success:
                            print(f'\u2705 Completed preparing the pretrainmodel:{folder_name}')
            except Exception as e:
                print(f'\u274C Failed Prepare Pretrainmodel: {str(e)}')
                all_pretrainmodels_copied = False
        else:
            if mount_success:
                nonempty_subdirectories_list = get_nonempty_subdirectories(local_pretrain_model_path)
                for subdirectory in nonempty_subdirectories_list:
                    print(f'Start preparing the pretrainmodel {subdirectory} ...')
                    print(f'\u2705 Completed preparing the pretrainmodel {subdirectory}')
        if all_pretrainmodels_copied:
            current_time_str = get_current_time()
            file_content = 'This is a pretrainmodel cache file used to indicate that the pretrainmodel preparation is complete. Please do not delete this file. Unless you want to overwrite the pretrainmodel or fetch the pretrainmodel again. Execution time: ' + current_time_str
            with open(pretrainmodel_cache_file_path, 'w') as f:
                f.write(file_content)
    else:
        print(f'Detected .pretrainmodel_cache_file already exists, pretrainmodel has been prepared!')
    return local_pretrain_model_path
