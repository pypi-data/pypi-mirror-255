import os
import json
import moxing as mox
from ..utils import constants
from ..utils.util import unzip_data, get_current_time

def moxing_code_to_env(code_url, code_dir, unzip_required,data_download_method):    
    """
    copy code to training image
    """
    unzip_success = False
    moxing_success = False
    if unzip_required == constants.DATASET_NEED_UNZIP_TRUE:
        try:
            codefile_path = os.path.join(code_dir, os.path.basename(code_url))
            mox.file.copy(code_url, codefile_path) 
            moxing_success = True
            if not os.path.exists(code_dir):
                os.makedirs(code_dir)
            print(f'Start preparing the code ...')
            unzip_success = unzip_data(codefile_path, code_dir,data_download_method)
        except Exception as e:
            print(f'\u274C moxing download {code_url} to {code_dir} failed: {str(e)}')
            moxing_success = False
    else:
        unzip_success = True
        try:
            print(f'Start preparing the code ...')
            mox.file.copy_parallel(code_url, code_dir)
            moxing_success = True
        except Exception as e:
            print(f'\u274C moxing download {code_url} to {code_dir} failed: {str(e)}')
            moxing_success = False
    if moxing_success & unzip_success:
        print(f'\u2705 Completed preparing the code')
        code_cache_file_path = os.path.join(code_dir, ".code_cache_file")
        if not os.path.exists(code_cache_file_path):
            current_time_str = get_current_time()
            file_content = 'This is a code cache file used to indicate that the code preparation is complete. Please do not delete this file.Unless you want to overwrite the code or fetch the code again. Execution time: ' + current_time_str
            with open(code_cache_file_path, 'w') as f:
                    f.write(file_content)

    return

def moxing_dataset_to_env(multi_data_url, data_dir, unzip_required, data_download_method):    
    """
    copy dataset to training image
    """
    multi_data_json = json.loads(multi_data_url)
    all_datasets_copied = True 
    for i in range(len(multi_data_json)):
        unzip_success = False
        moxing_success = False
        datasetfile_path = os.path.join(data_dir, multi_data_json[i]["dataset_name"])
        zipfilename = multi_data_json[i]["dataset_name"]
        if unzip_required == constants.DATASET_NEED_UNZIP_TRUE:
            try:
                if zipfilename.endswith('.tar.gz'):
                    filename = os.path.splitext(os.path.splitext(multi_data_json[i]["dataset_name"])[0])[0]
                    print(f'Start preparing the dataset {filename} ...')
                    mox.file.copy(multi_data_json[i]["dataset_url"], datasetfile_path) 
                    moxing_success = True
                    unzipfile_path = data_dir + "/" + filename
                    if not os.path.exists(unzipfile_path):
                        os.makedirs(unzipfile_path)
                    unzip_success = unzip_data(datasetfile_path, unzipfile_path,data_download_method)

                elif zipfilename.endswith('.zip'):
                    filename = os.path.splitext(multi_data_json[i]["dataset_name"])[0]
                    print(f'Start preparing the dataset {filename} ...')
                    mox.file.copy(multi_data_json[i]["dataset_url"], datasetfile_path) 
                    moxing_success = True
                    unzipfile_path = data_dir + "/" + filename
                    if not os.path.exists(unzipfile_path):
                        os.makedirs(unzipfile_path)
                    unzip_success = unzip_data(datasetfile_path, unzipfile_path,data_download_method)
            except Exception as e:
                print(f'\u274C moxing download {multi_data_json[i]["dataset_url"]} to {datasetfile_path} failed: {str(e)}')
                moxing_success = False
                all_datasets_copied = False
            if moxing_success & unzip_success:
                if zipfilename.endswith('.tar.gz'):
                    print(f'\u2705 Completed preparing the dataset {os.path.splitext(os.path.splitext(multi_data_json[i]["dataset_name"])[0])[0]}')
                elif zipfilename.endswith('.zip'):
                    print(f'\u2705 Completed preparing the dataset {os.path.splitext(multi_data_json[i]["dataset_name"])[0]}')
        else:
            unzip_success = True
            try:
                print(f'Start preparing the dataset {os.path.splitext(multi_data_json[i]["dataset_name"])[0]} ...')
                mox.file.copy_parallel(multi_data_json[i]["dataset_url"], datasetfile_path)
                moxing_success = True
            except Exception as e:
                print(f'\u274C moxing download {multi_data_json[i]["dataset_url"]} to {datasetfile_path} failed: {str(e)}')
                moxing_success = False
                all_datasets_copied = False
            if moxing_success & unzip_success:
                print(f'\u2705 Completed preparing the dataset {os.path.splitext(multi_data_json[i]["dataset_name"])[0]}')

    if all_datasets_copied:
        dataset_cache_file_path = os.path.join(data_dir, ".dataset_cache_file")
        if not os.path.exists(dataset_cache_file_path):
            current_time_str = get_current_time()
            file_content = 'This is a dataset cache file used to indicate that the dataset preparation is complete. Please do not delete this file. Unless you want to overwrite the dataset or fetch the dataset again. Execution time: ' + current_time_str
            with open(dataset_cache_file_path, "w") as f:
                f.write(file_content)
    return

def moxing_pretrain_to_env(pretrain_url, pretrain_dir, unzip_required,data_download_method):
    """
    copy pretrain to training image
    """
    unzip_success = False
    moxing_success = False
    pretrain_url_json = json.loads(pretrain_url)  
    all_models_copied = True 
    for i in range(len(pretrain_url_json)):
        modelfile_path = pretrain_dir + "/" + pretrain_url_json[i]["model_name"]
        zipfilename = pretrain_url_json[i]["model_name"]
        if unzip_required == constants.DATASET_NEED_UNZIP_TRUE:
            try:
                if zipfilename.endswith('.tar.gz'):
                    filename = os.path.splitext(os.path.splitext(pretrain_url_json[i]["model_name"])[0])[0]
                    print(f'Start preparing the pretrainmodel {filename} ...')
                    mox.file.copy(pretrain_url_json[i]["model_url"], modelfile_path) 
                    moxing_success = True
                    filename = os.path.splitext(os.path.splitext(pretrain_url_json[i]["model_name"])[0])[0]
                    unzipfile_path = pretrain_dir + "/" + filename
                    if not os.path.exists(unzipfile_path):
                        os.makedirs(unzipfile_path)
                    unzip_success = unzip_data(modelfile_path, unzipfile_path,data_download_method)
                elif zipfilename.endswith('.zip'):
                    filename = os.path.splitext(pretrain_url_json[i]["model_name"])[0]
                    print(f'Start preparing the pretrainmodel {filename} ...')
                    mox.file.copy(pretrain_url_json[i]["model_url"], modelfile_path) 
                    moxing_success = True
                    unzipfile_path = pretrain_dir + "/" + filename
                    if not os.path.exists(unzipfile_path):
                        os.makedirs(unzipfile_path)
                    unzip_success = unzip_data(modelfile_path, unzipfile_path,data_download_method)
            except Exception as e:
                print(f'\u274C moxing download {pretrain_url_json[i]["model_url"]} to {modelfile_path} failed: {str(e)}')
                moxing_success = False
                all_models_copied = False
            if moxing_success & unzip_success:
                if zipfilename.endswith('.tar.gz'):
                    print(f'\u2705 Completed preparing the pretrainmodel {os.path.splitext(os.path.splitext(pretrain_url_json[i]["model_name"])[0])[0]}')
                elif zipfilename.endswith('.zip'):
                    print(f'\u2705 Completed preparing the pretrainmodel {os.path.splitext(pretrain_url_json[i]["model_name"])[0]}')
        else:
            unzip_success = True
            try:
                print(f'Start preparing the pretrainmodel {os.path.splitext(pretrain_url_json[i]["model_name"])[0]} ...')
                mox.file.copy_parallel(pretrain_url_json[i]["model_url"], modelfile_path) 
                moxing_success = True
            except Exception as e:
                print(f'\u274C moxing download {pretrain_url_json[i]["model_url"]} to {modelfile_path} failed: {str(e)}')
                moxing_success = False
                all_models_copied = False
            if moxing_success & unzip_success:
                print(f'\u2705 Completed preparing the pretrainmodel {os.path.splitext(pretrain_url_json[i]["model_name"])[0]}')
    if all_models_copied:
        pretrainmodel_cache_file_path = os.path.join(pretrain_dir, ".pretrainmodel_cache_file")
        if not os.path.exists(pretrainmodel_cache_file_path):
            current_time_str = get_current_time()
            file_content = 'This is a pretrainmodel cache file used to indicate that the pretrainmodel preparation is complete. Please do not delete this file.Unless you want to overwrite the pretrainmodel or fetch the pretrainmodel again. ' + current_time_str
            with open(pretrainmodel_cache_file_path, "w") as f:
                f.write(file_content)
        return        

def obs_copy_file(obs_file_url, file_url):
    """
    cope file from obs to obs, or cope file from obs to env, or cope file from env to obs
    """
    try:
        mox.file.copy(obs_file_url, file_url)
        print(f'\u2705 Completed Download {obs_file_url} to {file_url}')
    except Exception as e:
        print(f'\u274C moxing download {obs_file_url} to {file_url} failed: {str(e)}')
    return    
    
def obs_copy_folder(folder_dir, obs_folder_url):
    """
    copy folder from obs to obs, or copy folder from obs to env, or copy folder from env to obs
    """
    try:
        mox.file.copy_parallel(folder_dir, obs_folder_url)
        print(f'\u2705 Completed Download {folder_dir} to {obs_folder_url}')
    except Exception as e:
        print(f'\u274C moxing download {folder_dir} to {obs_folder_url} failed: {str(e)}')
    return     

def upload_folder(folder_dir, obs_folder_url):
    """
    upload folder to obs
    """
    try:
        print(f'Start Upload Output ...')
        mox.file.copy_parallel(folder_dir, obs_folder_url)
        print(f'\u2705 Completed Upload Output')
    except Exception as e:
        print(f'\u274C moxing upload {folder_dir} to {obs_folder_url} failed: {str(e)}')
    return       