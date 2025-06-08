from PyQt6.QtCore import QObject
import os

class MergeCode(QObject):
    app_prefix = 'bs2daisy'
    supported_code_ext = {'js', 'html', 'py'}
    
    def __init__(self, source_dir: str, target_dir: str, variables: dict):
        self._sourceDir = source_dir
        self._targetDir = target_dir
        self._variables = variables
    
    @property
    def variables(self) -> dict:
        return self._variables
        
    @property
    def source_dir(self) -> str:
        return self._sourceDir
    
    @property
    def target_dir(self) -> str:
        return self._targetDir    
    
    def merge_folder(self, variables: dict, folder: str=None):
        if folder is None:
            folder = self.source_dir
            
        for root, dirs, files in os.walk(folder):
            output_root = self._merge_folder_path(root, variables)
            
            #TODO make use of target_dir, this is currently not correct
            
            for file in files:
                _, code_ext = os.path.splitext(file)
                output_file = self._merge_filename(file)
                output_path = os.path.join(output_root, output_file)
                input_path = os.path.join(root, file)
                
                with open(input_path, 'r') as file:
                    source = file.read()                     
                
                if code_ext in self.supported_code_ext:               
    
                    with open(output_path, 'r') as output_file:
                        target = output_file.read()
                        
                    if code_ext == 'js':                    
                        target = self._merge_javascript_source(source, target, variables)
                    elif code_ext == 'html':
                        target = self._merge_html_source(source, target, variables)
                    elif code_ext == 'py':
                        target = self._merge_python_source(source, target, variables)
                    else:
                        assert 0
                else:
                    # if file == 'requirements.txt' etc
                    
                    target = source         # Overwrite source is the default behavior for unknown code ext
                    
                with open(output_path, 'w') as output_file:
                    output_file.write(target)                    
                
            for directory in dirs:
                self.merge_folder(variables, folder=directory)                
                
    def _merge_folder_path(self, path: str, variables:dict):
        path_parts = os.path.split(path)
        path_list = []        
        for folder_name in path_parts:
            if folder_name.startswith(self.app_prefix):
                folder_name = self._merge_filename(folder_name, variables)
                path_list.append(folder_name)        
        return os.path.join(*path_list)
    
    def _merge_filename(self, filename: str, variables:dict):
        key = filename[len(self.app_prefix):]
        filename = variables[key]
        return filename
        
    def _merge_python_source(self, source: str, target: str, variables: dict):
        import libcst as cst
        source_tree = cst.parse_expression(source)
        