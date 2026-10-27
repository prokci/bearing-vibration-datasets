import json
import os
from pathlib import Path
import re

import numpy as np
from tqdm import tqdm

from Lib_classes.DataFrameFilesBuilderStack import DataFrameStackBuilder
from Lib_classes.FileArchitecture import FileStackArchitecture, PdPickleFileArchitecture
from Lib_classes.Logger import Logger, LoggerEmpty
from Source.Source_aggregate.Bearing.BindClasses import bind_classess
from Lib_classes.Paths import Paths
from Source.Utils.Signature.BearingFaultSignature import BearingFaultSignature
from Source.Utils.Spliters.EqualSizeSplitter import EqualSizeSplitter
from Source.Utils.BalancedChunkRunner.BalancedChunkRunner import BalancedChunkRunner


class Source:
    def __init__(self, path, max_stack_size: int = 10, bind_classess = bind_classess):
        self.path = path
        self.max_stack_size = max_stack_size
        self.bind_classess = bind_classess
        
    def read_metadata(self):
        metadata_path = os.path.join(self.path, 'metadata.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as file:
                return json.load(file)
        else:
            raise Exception(f"Error: '{metadata_path}' file doesn't exist.")
        
    def get_file_archive(self):
        file_archive = self.bind_classess.get(self.read_metadata().get('name'))
        if file_archive:
            return file_archive(self.path, self.max_stack_size)
        


class SourceAggregator:
    COLUMNS = ['data', 'rpm', 'samples/second', 'place', 'inner_race', 'ball', 'outer_race', 'original_path', 'fault', 'load_w', 'id_bearing', 'weight', 'object_params']
    PLACE_TYPE = ['drive end', 'fan end', 'base', 'wire_roller', 'engine', 'pump', 'strainer', 'motor' ]
    LOGGER = Logger('SourceAggregator')
    REAL_CLASS_ORDER = ['inner_race', 'ball', 'outer_race']
    
    
    @classmethod
    def valid_make_row(
        cls,
        data:np.ndarray, 
        rpm:float, 
        samples_by_second:int, 
        place:str, 
        inner_race:bool, 
        ball:bool, 
        outer_race:bool, 
        original_path: str, 
        fault:float,
        load_w:float,
        id_bearing:str,
        weight:float,
        load_torque:float = -1,
        radial_force:float = -1,
        object_params:dict|None = None
    ):
        object_params = object_params or {}
        errors = []
        def check_type(var, expected_type, var_name):
            if not isinstance(var, expected_type):
                errors.append(f"{var_name}: expected {expected_type.__name__}, got {type(load_torque).__name__}")
                
        check_type(data, np.ndarray, "data")
        # check_type(rpm, (int, float), "rpm")  # Можно допустить int, так как float может принимать целые значения
        # check_type(samples_by_second, int, "samples_by_second")
        # check_type(place, str, "place")
        # check_type(inner_race, bool, "inner_race")
        # check_type(ball, bool, "ball")
        # check_type(outer_race, bool, "outer_race")
        # check_type(original_path, str, "original_path")
        # check_type(fault, (int, float), "fault")  # Можно допустить int, так как float может принимать целые значения
        # check_type(load_w, (int, float), "load_w")  # Можно допустить int, так как float может принимать целые значения
        # check_type(id_bearing, str, "id_bearing")
        # check_type(load_torque, (int, float), "load_torque")  # Можно допустить int, так как float может принимать целые значения
        # check_type(radial_force, (int, float), "radial_force")  # Можно допустить int, так как float может принимать целые значения
        
        if data.dtype != np.float64:
            errors.append(f'data must np.ndarray[np.float64]')
        if place not in cls.PLACE_TYPE:
            errors.append(f'{place} is not in {cls.PLACE_TYPE}')
            
        if errors:
            raise TypeError("Type errors detected:\n" + "\n".join(errors))
        
        # SourceAggregator.logger(f'data.shape = {np.array(data).shape}')
        # SourceAggregator.logger(f'rpm = {rpm}')
        # SourceAggregator.logger(f'samples_by_second = {samples_by_second}' )
        # SourceAggregator.logger(f'place = {place}')
        # SourceAggregator.logger(f'inner_race = {inner_race}')
        # SourceAggregator.logger(f'ball = {ball}')
        # SourceAggregator.logger(f'outer_race = {outer_race}')
        # SourceAggregator.logger(df'original_path = {original_path}')
        # SourceAggregator.logger(f'fault = {fault}')
        # SourceAggregator.logger(f'load_w = {load_w}')
        # SourceAggregator.logger(f'id_bearing = {id_bearing}')
        # SourceAggregator.logger(f'load_torque = {load_torque}')
        # SourceAggregator.logger(f'radial_force = {radial_force}')
        
        return [data, rpm, samples_by_second, place, inner_race, ball, outer_race, original_path, fault, load_w, id_bearing, float(weight), object_params]
        
    
    def __init__(self, max_stack_size: int = 10, path = os.path.join(Paths.dir_dataframe_pickles, 'Bearing'), logger: LoggerEmpty = Logger('SourceAggregator'), bind_classess = bind_classess):
        self.path = Paths.dir_source
        self.max_stack_size = max_stack_size
        self.pickle_arch = PdPickleFileArchitecture(path, max_stack_size=self.max_stack_size)
        self.LOGGER = logger
        self.bind_classess = bind_classess
        
        
    def get_rows(self):
        for file in os.listdir(self.path):
            s =  Source(os.path.join(self.path, file), self.max_stack_size, self.bind_classess)
            file_archive = None
            # try:
            file_archive = s.get_file_archive()
            if file_archive is None:
                continue
            for row in file_archive.iter():
                yield row

            # except Exception as exp:
            #     exp.add_note('folder:' + file)
            #     self.LOGGER(exp)
            

            # file_archive = s.get_file_archive()
            # for row in file_archive.iter():
            #     yield row

            
                
    def __call__(self):
        builder = DataFrameStackBuilder(self.COLUMNS, file_stack_architecture=self.pickle_arch)
        
        for row in self.get_rows():
            builder.add(row)

        builder.save_tail()
        
        # for i, row in enumerate(self.pickle_arch.iter()):
        #     self.logger(row)
        
    @staticmethod
    def test():
        SourceAggregator(1000, os.path.join(Paths.dir_dataframe_pickles, 'Bearing_temp'))()


        
    @staticmethod
    def bearing_aggregate_and_preparation(max_stack_size: int = 1000, train_size: float = 0.8):
        bearing_path = os.path.join(Paths.dir_dataframe_pickles, 'Bearing')
        train_path = os.path.join(Paths.dir_dataframe_pickles, 'Bearing', 'train')
        
        train_random_path = os.path.join(Paths.dir_dataframe_pickles, 'Bearing', 'train_random')
        reference_path = os.path.join(Paths.dir_dataframe_pickles, 'Bearing', 'reference')
        
        SourceAggregator(max_stack_size)()
        DataFrameStackBuilder.separation_from_train_and_test(
            PdPickleFileArchitecture.open(bearing_path),
            train_size,
            saved_path = bearing_path
        )
        
        DataFrameStackBuilder.randomizer(
            PdPickleFileArchitecture.open(train_path),
            saved_path = train_random_path,
            reference_path = reference_path
        )
        
        
        Paths.rename_old_file_full(train_path)
        os.rename(train_random_path, train_path)
    
    
    CHUNK_FOLDER_NAME = 'balancer_chunks'
    @classmethod
    def split_chunks(cls, n_chunks = 10, rng = np.random.default_rng(0)):
        pfa = PdPickleFileArchitecture.open(os.path.join(Paths.dir_dataframe_pickles, 'Bearing'))
        
        bcr = BalancedChunkRunner(
            pfa,
            EqualSizeSplitter(rng, n_chunks = n_chunks),
            BearingFaultSignature(SourceAggregator.REAL_CLASS_ORDER, rng),
            rng
        )
        chunks = bcr.generate_chunk_indices()
        
        path = os.path.join(Paths.dir_dataframe_pickles, 'Bearing', cls.CHUNK_FOLDER_NAME)
        
        pmf = DataFrameStackBuilder(
            list(pfa.get_columns()), 
            PdPickleFileArchitecture(
                path,
                max_stack_size=len(next(iter(chunks.values())))
            )
        )

        for k_, df in tqdm(bcr.provide_chunks(chunks), total=n_chunks):
            pmf.add_df(df)

        pmf.save_tail()
        
    @classmethod
    def split_groups(
        cls,
        pfa:FileStackArchitecture,
        chunk_size = 1000,
        get_split_column = None,
        rng = np.random.default_rng(0),
        output_base = Path(Paths.dir_dataframe_pickles)/'Bearing'/'splits_validate'
    ):
        
        def split_column(x):
            x = Path(x).parts[len(Path(Paths.dir_source).absolute().parts)]
            match = re.search(r'^([\D\d]+\D)\d+$', x) 
            if match is None:
                return x
            return match.group(1)
        
        if get_split_column is None:
            get_split_column = lambda df:df['original_path'].map(split_column)
        
        builders = {}
        columns = list(pfa.get_columns())
        
        try:
            for i in tqdm(pfa.iter_stack_index(), desc="Processing Source Files", total=len(list(pfa.iter_stack_index()))):
                full_df = pfa.get_file(i)
                full_df['split'] = get_split_column(full_df)
                grouped = full_df.groupby('split')
                
                for split_name, group_df in grouped:
                    
                    if split_name not in builders:
                        split_dir = output_base / str(split_name)
                        builders[split_name] = DataFrameStackBuilder(
                            columns,
                            PdPickleFileArchitecture(str(split_dir), max_stack_size=chunk_size)
                        )
                        builders[split_name].__enter__()
                    group_df = group_df.sample(frac=1, random_state=rng.integers(0, np.iinfo(np.int32).max)).reset_index(drop=True)
                    builders[split_name].add_df(group_df)

        finally:
            for builder in builders.values():
                builder.__exit__(None, None, None)
        
