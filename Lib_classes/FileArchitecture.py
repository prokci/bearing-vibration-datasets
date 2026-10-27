import os
from abc import abstractmethod

import pandas as pd

from Lib_classes.Logger import LoggerEmpty
from Lib_classes.Paths import Paths


class FileStackArchitecture:
    
    extension = ''
    def __init__(self, path: str, max_stack_size: int = 10, is_new: bool = True, logger = LoggerEmpty('FileStackArchitecture')):
        self.path = path
        self.max_stack_size = max_stack_size
        self._stack_index = 0
        self._is_opened = False
        self.logger = logger

        if is_new:
            Paths.rename_old_dir(path)

    def get_columns(self):
        return self.get_file(0).columns
        
    def buld_path_str(self, index: int):
        return os.path.join(self.path, str(index)) + f'.{self.extension}'
    
    @abstractmethod
    def get_file(self, index: int) -> pd.DataFrame:
        raise NotImplementedError
    
    @abstractmethod
    def add_file(self, df: pd.DataFrame) -> None:
        raise NotImplementedError
    
    def __len__(self):
        return self._stack_index+1
    
    def iter(self):
        for i in self.iter_stack_index():
            stack = self.get_file(i)
            for row in stack.iterrows():
                yield row
                
    def iter_stack_index(self):
        with self.logger.presbar('iter_stack_index', self._stack_index+1) as log:
            for i in range(self._stack_index+1):
                yield i
                log()
    
    def update_stack_index(self):
        self._stack_index = len(
            list(Paths.get_all_expasion_for_path(self.path, self.extension, logger=LoggerEmpty()))
        )-1
        
    def update_max_stack_size(self):
        self.max_stack_size = len(self.get_file(0))
        
        
    class Rows:
        def __init__(self, parent: 'FileStackArchitecture'):
            self.parent = parent
            if not self.parent._is_opened:
                parent.update_stack_index()
                parent.update_max_stack_size()
                parent._is_opened = True
            
            self.max_stack_size = self.parent.max_stack_size
            self._len = self.max_stack_size * self.parent._stack_index \
                + len(self.parent.get_file(self.parent._stack_index)) if self.parent._stack_index > -1 else 0
                
        def __len__(self):
            return self._len
        
        def index(self, index: int):
            ix_in_stack = index % self.max_stack_size
            stack_ix = index // self.max_stack_size
            return  stack_ix, ix_in_stack
        def __getitem__(self, index: int):
            stack_ix, ix_in_stack = self.index(index)
            return self.parent.get_file(stack_ix).iloc[ix_in_stack]
        
    def rows(self, is_new = False):
        if hasattr(self, '_rows') and not is_new:
            return self._rows
        else:
            self._rows = self.Rows(self)
        return self._rows
                
                
    @staticmethod
    def open(path: str, max_stack_size: int|None = None, logger = LoggerEmpty('PdPickleFileArchitecture')):
        pdf = PdPickleFileArchitecture(path, max_stack_size=max_stack_size, is_new=False, logger=logger)
        pdf.update_stack_index()
        if max_stack_size is not None:
            pdf.max_stack_size = max_stack_size
        else:
            pdf.update_max_stack_size()
        pdf._is_opened = True
        return pdf
        
class PdPickleFileArchitecture(FileStackArchitecture):
    extension = 'pickle'
        
    def get_file(self, index: int)-> pd.DataFrame:
        return pd.read_pickle(self.buld_path_str(index))
    
    def add_file(self, df: pd.DataFrame):
        
        df.to_pickle(self.buld_path_str(self._stack_index))
        self._stack_index += 1