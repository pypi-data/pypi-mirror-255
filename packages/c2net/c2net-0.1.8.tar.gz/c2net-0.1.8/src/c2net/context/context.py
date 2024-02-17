from .download import prepare_code, prepare_dataset, prepare_pretrain_model, prepare_output_path
from .upload import upload_c2net

class C2netContext:
    """
    Args:
        code_path:              The storage path of the code
        dataset_path:           The storage path of the dataset
        pretrain_model_path:    The storage path of the pretrain model
        output_path:            The storage path of the output
    """
    def __init__(self, code_path, dataset_path, pretrain_model_path, output_path):
        self.code_path = code_path
        self.dataset_path = dataset_path
        self.pretrain_model_path = pretrain_model_path
        self.output_path = output_path
        
def prepare():
    """
    Prepare the dataset, pretrain model and output path
    """
    print(
        r"""
       ___                _            _            _          
      |__ \              | |          | |          | |         
  ___    ) | _ __    ___ | |_  ______ | |__    ___ | |_   __ _ 
 / __|  / / | '_ \  / _ \| __||______|| '_ \  / _ \| __| / _` |
| (__  / /_ | | | ||  __/| |_         | |_) ||  __/| |_ | (_| |
 \___||____||_| |_| \___| \__|        |_.__/  \___| \__| \__,_|
                                                               
         """
    )
    print(
        """
If you have any problems while preparing the data, you can submit an issue in this repository: https://openi.pcl.ac.cn/OpenIOSSG/c2net-pypi
        """)
    code_path = prepare_code()
    dataset_path = prepare_dataset()
    pretrain_model_path = prepare_pretrain_model()
    output_path = prepare_output_path()
    t = C2netContext(code_path, dataset_path, pretrain_model_path, output_path)
    return t

def upload_output():
    """
    Upload the output to c2net
    """
    return upload_c2net()    
