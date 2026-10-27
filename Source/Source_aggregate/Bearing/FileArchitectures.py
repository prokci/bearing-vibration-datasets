import os
from abc import abstractmethod
from os.path import abspath

from Lib_classes.FileArchitecture import FileStackArchitecture
from Lib_classes.Logger import Logger
from Lib_classes.Paths import Paths

file_path = os.path.dirname(abspath(__file__))


class BearingDatasetFileArchitectures(FileStackArchitecture):
    extension = 'mat'
    def __init__(self, path: str, max_stack_size: int = 10):
        self.path = path
        self.max_stack_size = max_stack_size
        
    def buld_path_str(self, name: str):
        return os.path.abspath(os.path.join(self.path, f'{name}.{self.extension}'))
    
    @abstractmethod
    def get_file(self, index: str):
        pass
    
    def iter(self):
        for _, path, _ in Paths.get_all_expasion_for_path(self.path, f'.{self.extension}', logger=Logger(f'{self.__class__.__qualname__}')):
            name = Paths.get_name_from_path(path)
            yield self.get_file(name)
            
class BearingDatasetFileWithFolders(BearingDatasetFileArchitectures):
    
    depth = 1
    def buld_path_str(self, name: str, *folders:str):
        return os.path.abspath(os.path.join(self.path, *folders, f'{name}.{self.extension}'))
    
    def iter(self):
        def get_folder(path: str, currrent_depth: int, folders: list):
            if os.path.isdir(path):
                for path_folder in os.listdir(path):
                    new_folder = [folder for folder in folders]
                    new_folder.append(path_folder)
                    
                    if currrent_depth == 1:
                        yield from get_files(path_folder, path, new_folder )
                    else:
                        yield from get_folder(os.path.join(path, path_folder), currrent_depth-1, new_folder)
        
        def get_files(path_folder, path, folders):
            full_path = os.path.join(path, path_folder)
            if os.path.isdir(full_path):
                for _, path_, _ in Paths.get_all_expasion_for_path(full_path, self.extension, logger=Logger(f'{self.__class__.__qualname__}')):
                    name = Paths.get_name_from_path(path_)
                    yield self.get_file(name, *folders)
                    
        folders = []
        yield from get_folder(self.path, self.depth, folders)
    
    @abstractmethod     
    def get_file(self, name: str, *folders:str):
        pass


