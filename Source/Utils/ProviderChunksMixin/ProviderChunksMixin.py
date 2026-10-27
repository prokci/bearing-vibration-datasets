import numpy as np
import pandas as pd
from Lib_classes.FileArchitecture import PdPickleFileArchitecture
from Lib_classes.funcs import raise_none

class ProviderChunksMixin:
    def __init__(self, 
                 pfa: PdPickleFileArchitecture,
                 rng: np.random.Generator
        ):
        self.pfa = pfa
        self._rng = rng
        
    def provide_chunks(self, chunks:dict):
        for key, chunk in chunks.items():
            chunk_df = None
            for i in self.pfa.iter_stack_index():
                cur_chunks = list(map(lambda x: x[1], filter(lambda x: x[0] == i, chunk)))
                df = self.pfa.get_file(i).loc[cur_chunks]
                chunk_df = pd.concat([chunk_df, df], ignore_index=True) if chunk_df is not None else df
            chunk_df = raise_none(chunk_df).sample(frac=1, random_state=self._rng.integers(0, np.iinfo(np.int32).max)).reset_index(drop=True)
            yield key, chunk_df