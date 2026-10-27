import csv
import os
from typing import Final, Generator

import pandas as pd

from Lib_classes.funcs import set_like_order
from Lib_classes.Logger import LoggerEmpty
from Lib_classes.Paths import Paths as p
from Lib_classes.Singleton import Singleton


class MyResource(Singleton):
    file_path: str
    list_names: list
    need_column: dict
    filter_columns: dict
    max_count_row: Final[int] = 100_000
    
    def init(self, **kwds):
        self.logger = kwds.get('logger', LoggerEmpty())
    
    def _select_columns(self, df:pd.DataFrame, name:str):
        colums = self.need_column.get(name)
        if colums is not None:
            return df[colums]
        else:
            return df
        
        
    def _filter_columns(self, df:pd.DataFrame, name:str):
        filter_colums = self.filter_columns.get(name)
        if filter_colums is not None:
            colums = set_like_order(lambda col, fit_col: col-fit_col,df.columns,filter_colums)
            return df[colums]
        else:
            return df
        
        
    #get resources
    
    def _get_resource_by_excel(self, name)->pd.DataFrame:
        source = pd.read_excel(self.file_path + '.xlsx', sheet_name=name)
        return self._select_columns(source, name)
    
    def _get_resource_by_csv(self, name)->pd.DataFrame:
        source = pd.read_csv(os.path.join(self.file_path, f'{name}.csv'))
        return self._select_columns(source, name)
    
    #resafe resources
    
    def _resafe_to_excel(self,new_data:pd.DataFrame, name:str):
        new_data = self._select_columns(new_data, name)
        
        file_name = self.file_path + '.xlsx'
        p.rename_old_file(file_name)
        
        
        new_data.to_excel(file_name, index=False, sheet_name=self.list_names[0])
        return new_data
    
    def _resafe_to_csv(self, new_data:pd.DataFrame, name:str):
        
        file_name = os.path.join(self.file_path, f'{name}.csv')
        p.rename_old_file(file_name)
        
        new_data = self._select_columns(new_data, name)
        new_data.to_csv(file_name,  index=False)
        return new_data
    
    #iter resurce
    def _csv_iter_save(self, name:str, column_names, generator:Generator[dict, None, None]):
        
        file_name = os.path.join(self.file_path, f'{name}.csv')
        p.rename_old_file(file_name)
        
        with open(file_name, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=column_names)
            writer.writeheader()
            
            for row in generator:
                writer.writerow(row)
                
    def _csv_save_by_with(self, name:str, column_names):
    #     with open(self.file_path + '_'+ name + '.csv', 'w', newline='') as csvfile:
            class CSVSaver:
                def __init__(self, file_path, column_names, name):
                    self.csvfile = os.path.join(file_path, f'{name}.csv')
                    self.column_names = column_names
                    
                def __enter__(self):
                    p.rename_old_file(self.csvfile)
                    
                    self.file = open(self.csvfile, 'w', newline='')
                    self.file = self.file.__enter__()
                    
                    self.writer = csv.DictWriter(self.file, fieldnames=self.column_names)
                    self.writer.writeheader()
                    return self
                
                def __exit__(self, exc_type, exc_val, exc_tb):
                    self.file.__exit__(exc_type, exc_val, exc_tb)
                def __call__(self, row):
                    self.writer.writerow(row)

            return CSVSaver(self.file_path, column_names, name)
            
                
    
    
    def _csv_iter_load(self, name:str, lenght:int|None = None):
        if lenght is None:
            lenght = self.max_count_row
            
        
        with open(os.path.join(self.file_path, f'{name}.csv'), 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile, quoting=csv.QUOTE_MINIMAL)
            
            with self.logger.presbar(name, lenght) as bar:
                for row in reader:
                    # if lenght is not None:
                    #     lenght -= 1
                    #     if lenght < 0:
                    #         return None
                        
                    yield row
                    
                    bar()
                    
    def _csv_iter_load_to_df(self, name:str, lenght:int):
        return pd.DataFrame(list(self._csv_iter_load(name, lenght)))
    
    
                
 
 
# class DDResource(Singleton):
#     file_path = ''
#     list_names = []
#     need_column = {}
    
    
#     def _select_columns(self, df:dd.DataFrame, name:str): # type: ignore
#         colums = self.need_column.get(name)
#         if colums is not None:
#             return df[colums]
#         else:
#             return df
        
        
#     #get resources
    
#     def _get_resource_by_csv(self, name, **configs)->dd.DataFrame: # type: ignore
#         source = dd.read_csv(self.file_path + '\\'+ name + '.csv', **configs) # type: ignore
#         return self._select_columns(source, name)
    
#     def _get_resource_by_csv_limit(self, name, count_row)->dd.DataFrame: # type: ignore
#         source = from_pandas(pd.read_csv(self.file_path + '\\'+ name + '.csv', nrows=count_row), chunksize=200)
#         return self._select_columns(source, name)
    
    

    
#     #resafe resources
    
#     def _resafe_to_csv(self,new_data:dd.DataFrame, name:str): # type: ignore
#         new_data = self._select_columns(new_data, name)
#         new_data.to_csv(self.file_path + '\\'+ name + '.csv',  index=False).compute() # type: ignore
#         return new_data
    
    
                
    