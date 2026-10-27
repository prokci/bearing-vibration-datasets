import getpass
import os
import re
from pathlib import Path

from Lib_classes.ComputerSettings import ComputerSettings
from Lib_classes.Logger import Logger, LoggerEmpty


class Paths:
    
    @staticmethod
    def base_directore_for_user():
        return ComputerSettings.get_user_dict()['path']

    base_directore = base_directore_for_user()

    dir_dataframe_pickles = os.path.join(base_directore, 'dataframe_pickles')
    dir_source = os.path.join(base_directore, 'source')
    dir_configs = os.path.join(base_directore, 'configs')


    @staticmethod
    def make_all_need_dir():
        Paths.make_path(Paths.base_directore)

        for dir in [ Paths.dir_dataframe_pickles, 
                    Paths.dir_source,]:
            if not os.path.exists(dir):
                os.mkdir(dir)
                
    @staticmethod
    def make_path(dir:str):
        if not os.path.exists(dir):
            Paths.make_path(os.path.dirname(dir))
            os.mkdir(dir)
            return True
        return False
    
    @staticmethod
    def rename_old_dir(dir:str):
        if Paths.make_path(dir):
            return -1
        else:
            index = Paths.rename_old_file_full(dir)[0]
            Paths.make_path(dir)
            return index
    
    

    @staticmethod
    def make_json(name = 'standart'):
        return os.path.join(Paths.dir_configs, f'{name}.json')
    
    # @staticmethod
    # def make_model_json(name = 'standart'):
    #     return Paths.dir_models_config + f'\\{name}.json'

    @staticmethod
    def rename_old_file(file_name):
        return Paths.rename_old_file_full(file_name)[0]

    @staticmethod
    def rename_old_file_full(file_name):
        old_file = file_name; i = 0
        while os.path.exists(old_file):
            i+=1
            old_file = file_name + f'.old({i})'
            
        if(i!=0):
            os.rename(file_name, old_file)
            
        if old_file == file_name:
            old_file = None
            
        return i+1, old_file

    @staticmethod
    def delete_old_file(file_name):
        if(os.path.exists(file_name)):
            os.remove(file_name)

    @staticmethod
    def rename_or_delate_old_file(file_name, isRenameOldFile):
            if isRenameOldFile:
                Paths.rename_old_file(file_name)
            else:
                Paths.delete_old_file(file_name)
            
    @staticmethod
    def get_original_name(file_name):
        reg  = r'\.old\(\d+\)$'
        if len(file_name)>7 and re.search(reg, file_name) is not None:
            return re.sub(reg, '', file_name)
            
        return None

    @staticmethod
    def get_old_number(file_name, isChecking = True):
        def get_number(file_name):
            start = r'^.*\.old\('
            end = r'\)$'
            
            str = re.sub(start, '', file_name)
            str = re.sub(end, '', str)
            
            return int(str)
        
        if isChecking:
            if Paths.get_original_name(file_name) is not None:
                return get_number(file_name)
            else:
                return -1
        else:
            return get_number(file_name)

    @staticmethod
    def get_all_expasion_for_path(
        dir:str, expansion:str, 
        filter = ['standart.json'], 
        logger:LoggerEmpty = Logger('get_all_expasion_for_path')):
            curent_dir = os.listdir(dir)
            with logger.presbar("files", len(curent_dir)) as pbar:

                for file in curent_dir:
                    if file in filter:
                        pass
                    buf_original_name = Paths.get_original_name(file)
                    
                    index = -1
                    if buf_original_name is not None:
                        index = Paths.get_old_number(file, False)
                    
                    if(file.endswith(expansion) or 
                        (buf_original_name is not None and buf_original_name.endswith(expansion))):
                        (yield index,
                            os.path.join(dir, file), 
                            os.path.join(dir, buf_original_name) if buf_original_name is not None else None)
                        
                    pbar()
    @staticmethod         
    def rebase_folder(dir_path):
        parent_dir = os.path.dirname(dir_path)
        for files in os.listdir(dir_path):
            os.rename(os.path.join(dir_path, files), os.path.join(parent_dir, files))
        os.rmdir(dir_path)
                
                    

    @staticmethod
    def get_name_from_path(path:str):
        name = Path(path).name
        return name[:name.rfind('.')]#[path.rfind('\\')+1:]
    
    
    @staticmethod
    def crc32(fileName):
        import zlib
        with open(fileName, 'rb') as fh:
            hash = 0
            while True:
                s = fh.read(65536)
                if not s:
                    break
                hash = zlib.crc32(s, hash)
            return "%08X" % (hash & 0xFFFFFFFF)
