import os
import random
import shutil
from itertools import zip_longest
from typing import Any, Callable, Hashable, Iterable

import numpy as np
import pandas as pd

from Lib_classes.FileArchitecture import FileStackArchitecture, PdPickleFileArchitecture
from Lib_classes.Logger import Logger
from Lib_classes.Paths import Paths as p


class DataFrameStackBuilder:
    def __init__(self, columns: list[str], file_stack_architecture: FileStackArchitecture):
        self.columns = columns
        self.tail: pd.DataFrame = pd.DataFrame(columns=columns)
        self.file_stack_architecture = file_stack_architecture
        
    def add_df(self, df: pd.DataFrame):
        def get_start_index():
            return self.tail.index[-1] + 1 if len(self.tail) > 0 else 0
        start_i = get_start_index()
        df.index = pd.RangeIndex(start=start_i, stop=start_i+len(df), step=1)
        
        if len(df) == 0: return self
        elif len(self.tail) != 0:
            df = pd.concat(
                [self.tail, df],
            )
        while len(df) > self.file_stack_architecture.max_stack_size:
            self.file_stack_architecture.add_file(df.iloc[:self.file_stack_architecture.max_stack_size])
            df = df.iloc[self.file_stack_architecture.max_stack_size:]
        
        self.tail = df
            
        return self
    
    def save_tail(self):
        self.file_stack_architecture.add_file(self.tail)
        self.tail = pd.DataFrame(columns=self.columns)
    
    def add(self, data: dict[Any, Any] | Iterable[list | tuple[Hashable, list] | dict[Any, Any]]):
        return self.add_df(pd.DataFrame(data=data, columns=self.columns))
    
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save_tail()
        return False
    
    @staticmethod
    def test():
        pfa = PdPickleFileArchitecture(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test'), max_stack_size=2)
        DataFrameStackBuilder(['array', 'protery'], pfa ) \
            .add_df(pd.DataFrame(
                [[np.array([1, 2, 3]), 1],
                [np.array([4, 5, 6]), 2],
                [np.array([7, 8, 9]), 3],],
            columns=['array', 'protery']
            ))\
            .add_df(pd.DataFrame(
                [[np.array([1, 2, 3]), 1],
                [np.array([4, 5, 6]), 2],
                [np.array([7, 8, 9]), 3],],
            columns=['array', 'protery']
            ))\
            .add([[np.array([1, 2, 3]), 1],
                [np.array([4, 5, 6]), 2],
                [np.array([7, 8, 9]), 3],])\
            .save_tail()
            
        for i in pfa.iter():
            print(i)
    
    # if necessary, you can distribute it among the stacks.
    @staticmethod    
    def separation_from_train_and_test(pfa: PdPickleFileArchitecture, 
                                       train_size: float = 0.8, 
                                       saved_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'result')):
        pfa_train = PdPickleFileArchitecture(os.path.join(saved_path, 'train'), max_stack_size=pfa.max_stack_size)
        builder_train = DataFrameStackBuilder(list(pfa.get_columns()), pfa_train)
        
        pfa_test = PdPickleFileArchitecture(os.path.join(saved_path, 'test'), max_stack_size=pfa.max_stack_size)
        builder_test = DataFrameStackBuilder(list(pfa.get_columns()), pfa_test)
        
        for i in pfa.iter_stack_index():
            df = pfa.get_file(i)
            test = np.random.random(len(df)) > train_size
            
            df_test = df.iloc[test]
            df_train = df.iloc[~test]
            
            builder_train.add_df(df_train)
            builder_test.add_df(df_test)
            
        builder_train.save_tail()
        builder_test.save_tail()
        
        return pfa_train, pfa_test
    
    @staticmethod
    def randomizer(
        pfa: PdPickleFileArchitecture, 
        saved_path: str,
        depth: int = -1,  
        reference_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reference'),
        logger = Logger('randomizer')
    ):
        if depth == -1:
            depth = len(pfa)
            
        p.rename_old_file_full(saved_path)
        
        shutil.copytree(pfa.path, saved_path)
        
        saved_pfa = PdPickleFileArchitecture.open(saved_path)
            
        reference_pfa = PdPickleFileArchitecture(reference_path, max_stack_size=pfa.max_stack_size)
        reference_builder = DataFrameStackBuilder(list(pfa.get_columns()), reference_pfa)
        
        with logger.presbar('depth', depth) as step:
            for _ in range(depth):
                indexed = list(saved_pfa.iter_stack_index())
                random.shuffle(indexed)
                index_iter = iter(indexed)
                for i, j in zip_longest(index_iter, index_iter):
                    list_ = [saved_pfa.get_file(i)]
                    if j is not None:
                        list_.append(saved_pfa.get_file(j))
                    common = pd.concat(list_, axis=0)
                    common = common.sample(frac=1, replace=False)
                    reference_builder.add_df(common)

                reference_builder.save_tail()
                
                shutil.rmtree(saved_path)
                # shutil.copytree(pfa_random.path, saved_path)
                os.rename(reference_path, saved_path)
                os.mkdir(reference_path)
                
                saved_pfa = PdPickleFileArchitecture.open(saved_path)
                reference_pfa = PdPickleFileArchitecture(reference_path, pfa.max_stack_size)
                reference_builder = DataFrameStackBuilder(list(pfa.get_columns()), reference_pfa)
                step()

        shutil.rmtree(reference_path)
    
    @staticmethod
    def map_file(func: Callable[[pd.DataFrame], pd.DataFrame], pfa: PdPickleFileArchitecture, saved_path: str):
        reference_pfa = PdPickleFileArchitecture(saved_path, max_stack_size=pfa.max_stack_size)
        reference_builder = DataFrameStackBuilder(list(pfa.get_columns()), reference_pfa)
        
        for i in pfa.iter_stack_index():
            df = pfa.get_file(i)
            df = func(df)
            reference_builder.add_df(df)
        reference_builder.save_tail()
        return reference_pfa
    

    def slice_signal(self, s: float, pfa: PdPickleFileArchitecture, saved_path: str):
        raise NotImplementedError("This method is not implemented yet.")
        def func(df: pd.DataFrame) -> pd.DataFrame:
            new_df = pd.DataFrame(columns=df.columns)
            for i in range(len(df)):
                matadata = df.iloc[i][list(filter(lambda x: x != 'data', df.columns))]
                signal = df.iloc[i]['data'].to_numpy()
                
                for j in range(len(signal)):
                    pass 
            return new_df
        
        return self.map_file(func, pfa, saved_path)
    

        
            
            
            
                