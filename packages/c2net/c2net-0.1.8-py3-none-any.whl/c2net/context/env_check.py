import os
import tarfile
import zipfile
def env_check():
    try:
        import moxing as mox
        f'✅ enviornment check pass: Modelarts enviornment checked'
        return True
    except:
        f'✅ enviornment check failed: please run the code on the Qizhi platform NPU resource'
        return False
    
def code_to_env(code_url, code_dir, unzip_required):
    if env_check():
        from .helper import moxing_code_to_env as func
        func(code_url, code_dir, unzip_required)    

def dataset_to_env(multi_data_url, data_dir, unzip_required):
    if env_check():
        from .helper import moxing_dataset_to_env as func
        func(multi_data_url, data_dir, unzip_required)

def pretrain_to_env(pretrain_url, pretrain_dir, unzip_required):
    if env_check():
        from .helper import moxing_pretrain_to_env as func
        func(pretrain_url, pretrain_dir, unzip_required)

def obs_copy_file(obs_file_url, file_url):
    if env_check():
        from .helper import obs_copy_file as func
        func(obs_file_url, file_url)
    
def obs_copy_folder(folder_dir, obs_folder_url):
    if env_check():
        from .helper import obs_copy_folder as func
        func(folder_dir, obs_folder_url)

def upload_folder(folder_dir, obs_folder_url):
    if env_check():
        from .helper import upload_folder as func
        func(folder_dir, obs_folder_url)
        
def unzip_dataset(zipfile_path, unzipfile_path):
    try:
        if zipfile_path.endswith(".tar.gz"):
            with tarfile.open(zipfile_path, 'r:gz') as tar:
                tar.extractall(unzipfile_path)
            print(f'✅ Successfully extracted {zipfile_path} to {unzipfile_path}')
        elif zipfile_path.endswith(".zip"):
            with zipfile.ZipFile(zipfile_path, 'r') as zip_ref:
                zip_ref.extractall(unzipfile_path)
            print(f'✅ Successfully extracted {zipfile_path} to {unzipfile_path}')
        else:
            print(f'❌ The dataset is not in tar.gz or zip format!')
    except Exception as e:
        print(f'❌ Extraction failed for {zipfile_path}: {str(e)}')
    finally:
        try:
            os.remove(zipfile_path)
            print(f'✅ Successfully Deleted {zipfile_path}')
        except Exception as e:
            print(f'Deletion failed for {zipfile_path}: {str(e)},but this does not affect the operation of the program,so you can ignore')

def is_directory_empty(path):
    if len(os.listdir(path)) == 0:
        return True
    else:
        return False


       