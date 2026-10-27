from typing import Dict

import numpy as np
import pandas as pd

from Lib_classes.FileArchitecture import PdPickleFileArchitecture
from Lib_classes.Logger import LoggerEmpty
from Source.Utils.BalancedChunkRunner.ABalancedChunkRunner import ABalancedChunkRunner
from Source.Utils.ProviderChunksMixin.ProviderChunksMixin import ProviderChunksMixin
from Source.Utils.Signature.BearingFaultSignature import ASignature
from Source.Utils.Signature.MultiSignature import MultiSignature
from Source.Utils.Spliters.EqualSizeForScikitSplitter import EqualSizeForScikitSplitter


class SkLearnBalancedChunkRunner(ABalancedChunkRunner, ProviderChunksMixin):
    def __init__(self, 
                 pfa: PdPickleFileArchitecture,
                 spliter: EqualSizeForScikitSplitter,
                 signature_strategy: MultiSignature,
                 group_strategy: ASignature,
                 rng: np.random.Generator,
                 logger: LoggerEmpty = LoggerEmpty()
        ):
        super(ProviderChunksMixin, self).__init__()
        super(ABalancedChunkRunner, self).__init__(pfa, rng) 
        
        self._signature_strategy = signature_strategy
        self._splitter = spliter
        
        self._group_strategy = group_strategy
        
    def generate_chunk_indices(self) -> Dict[int, np.ndarray]:
        """
        Loads a file, groups data by signature, and returns balanced chunk indices.
        """
        size = len(self.pfa.rows())
        chunk_size = self.pfa.max_stack_size
        self._X = np.empty((size, 2))
        self._y = np.empty((size, self._signature_strategy.get_size()))
        self._group = np.empty(size)
         
        for i in self.pfa.iter_stack_index():
            df = self.pfa.get_file(i)
            sl = np.s_[i*chunk_size:i*chunk_size+df.shape[0]]
            self._X[sl], self._y[sl], self._group[sl] = self._extract(df, i)
            
        chunk_map = self._splitter.split(self._X, self._y, self._group)
        
        return chunk_map
    
    def _extract(self, df: pd.DataFrame, c_file:int):
        """Groups DataFrame indices by their stratification signature."""
        X = np.stack(pd.MultiIndex.from_product([[c_file], df.index.values]).values) # type: ignore
        y = np.empty((df.shape[0], self._signature_strategy.get_size()))
        group = np.empty(df.shape[0])
        for i, (idx, row) in enumerate(df.iterrows()):
            y[i] = self._signature_strategy.get_signature(row)
            group[i] = self._group_strategy.get_signature(row)
        return X, y, group