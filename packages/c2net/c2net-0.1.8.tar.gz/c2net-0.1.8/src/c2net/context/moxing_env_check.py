def moxing_env_check():
    try:
        import moxing as mox
        f'\u2705 enviornment check pass: Modelarts enviornment checked'
        return True
    except:
        f'\u2705 enviornment check failed: please run the code on the NPU resource'
        return False
    
def code_to_env(code_url, code_dir, unzip_required, data_download_method):
    if moxing_env_check():
        from .moxing_helper import moxing_code_to_env as func
        func(code_url, code_dir, unzip_required, data_download_method)    

def dataset_to_env(multi_data_url, data_dir, unzip_required, data_download_method):
    if moxing_env_check():
        from .moxing_helper import moxing_dataset_to_env as func
        func(multi_data_url, data_dir, unzip_required, data_download_method)

def pretrain_to_env(pretrain_url, pretrain_dir, unzip_required, data_download_method):
    if moxing_env_check():
        from .moxing_helper import moxing_pretrain_to_env as func
        func(pretrain_url, pretrain_dir, unzip_required, data_download_method)

def obs_copy_file(obs_file_url, file_url):
    if moxing_env_check():
        from .moxing_helper import obs_copy_file as func
        func(obs_file_url, file_url)
    
def obs_copy_folder(folder_dir, obs_folder_url):
    if moxing_env_check():
        from .moxing_helper import obs_copy_folder as func
        func(folder_dir, obs_folder_url)

def upload_folder(folder_dir, obs_folder_url):
    if moxing_env_check():
        from .moxing_helper import upload_folder as func
        func(folder_dir, obs_folder_url)
        


       