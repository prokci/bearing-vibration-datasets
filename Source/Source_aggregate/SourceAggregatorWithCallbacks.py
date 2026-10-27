import os

from Lib_classes.DataFrameFilesBuilderStack import DataFrameStackBuilder
from Lib_classes.FileArchitecture import PdPickleFileArchitecture
from Lib_classes.Logger import Logger, LoggerEmpty
from Lib_classes.Paths import Paths
from Source.Source_aggregate.Bearing.BindClasses import bind_classess
from Source.Source_aggregate.Callbacks.SourceAggregatorCallback import (
    SourceAggregatorCallback,
)
from Source.Source_aggregate.SourceAggregator import SourceAggregator


class SourceAggregatorWithCallbacks(SourceAggregator):
    @staticmethod
    def proxy_make_row(kwargs:dict):
        kwargs['samples_by_second'] = kwargs.pop('samples/second')
        
        return SourceAggregator.valid_make_row(**kwargs)
    
    def __init__(
        self, 
        max_stack_size: int = 10, 
        path = os.path.join(Paths.dir_dataframe_pickles, 'Bearing'), 
        logger: LoggerEmpty = Logger('SourceAggregator'), 
        bind_classess = bind_classess,
        callbacks:list[SourceAggregatorCallback] = [],
    ):
        self.path = Paths.dir_source
        self.max_stack_size = max_stack_size
        self.pickle_arch = PdPickleFileArchitecture(path, max_stack_size=self.max_stack_size)
        self.LOGGER = logger
        self.bind_classess = bind_classess
        self.callbacks = callbacks
            
                
    def __call__(self):
        builder = DataFrameStackBuilder(self.COLUMNS, file_stack_architecture=self.pickle_arch)
        for rows in self.get_rows():
            processed_rows = []
            for row in rows:
                row = dict(zip(self.COLUMNS, row))
                [row := callback.on_before_row_save(row) for callback in self.callbacks]
                if all(callback.filter_row(row) for callback in self.callbacks):
                    processed_rows.append(self.proxy_make_row(row))
            builder.add(processed_rows)
        builder.save_tail()
        