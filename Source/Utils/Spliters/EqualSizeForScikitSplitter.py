import copy
import numpy as np
import pandas as pd
from typing import Dict
from Lib_classes.funcs import get_seed
from Lib_classes.Logger import LoggerEmpty
from sklearn.model_selection import BaseCrossValidator



class EqualSizeForScikitSplitter(BaseCrossValidator):
    """
    Pure Fabrication responsible for splitting a dataset of indices into
    exactly N chunks of equal size, maintaining stratification.
    """
    def __init__(
        self, 
        cross_validation: BaseCrossValidator, 
        rng: np.random.Generator, 
        logger: LoggerEmpty = LoggerEmpty(), 
        is_shuffle: bool = True, 
        is_equalizing = True, 
        add_remainder = True
    ):
        self._cross_validation = cross_validation
        self._rng = rng
        self.n_chunks = cross_validation.get_n_splits()
        self.logger = logger
        self.is_shuffle = is_shuffle
        self.is_equalizing = is_equalizing
        self.add_remainder = add_remainder
        
        if hasattr(cross_validation, 'random_state'):
            self._cross_validation.random_state = get_seed(self._rng) # type: ignore

    def split(self, X, y, group) -> dict[int, np.ndarray]:
        """
        Distributes indices from groups into chunks.
        
        1. Trims global excess to ensure total_size % n_chunks == 0.
        2. Distributes main body of groups evenly.
        3. Distributes remainders probabilistically to balance chunk sizes.
        """
        if self.is_equalizing:
            X, y, group = self._trim_global_excess(X, y, group)
        
        chunks = {}
        with self.logger.presbar('EqualSizeForScikitSplitter', self.n_chunks) as pbar:
            for i, (_, index) in enumerate(self._cross_validation.split(X, y, group)):
                chunks[i] = X[index]
                if self.is_shuffle:
                    self._rng.shuffle(chunks[i])
                pbar()
        
        if self.is_equalizing:
            chunks = self._equaling_chunks(chunks, X, y, group)
        
        if self.add_remainder and self.is_equalizing:
            if not self._remainder.shape[0] == 0:
                chunks[i+1] = self._remainder
                if self.is_shuffle:
                    self._rng.shuffle(chunks[i+1])
                    
        return chunks
    
    def _equaling_chunks(self, chunks:dict[int, np.ndarray], X = None, y = None, group=None):
        """
        Redistributes indices between chunks to ensure strictly equal sizes.
        Excess indices are gathered into a pool and redistributed to smaller chunks.
        """
        chunks = copy.deepcopy(chunks)
        
        
        total_samples = sum(len(c) for c in chunks.values())
        target_size = total_samples // self.n_chunks

        surplus_indices = []
        for chunk_id, indices in chunks.items():
            current_len = len(indices)
            if current_len > target_size:
                excess_count = current_len - target_size
                keep_indices = indices[:-excess_count]
                removed_indices = indices[-excess_count:]
                
                chunks[chunk_id] = keep_indices
                
                surplus_indices.extend(removed_indices)

        surplus_indices = np.array(surplus_indices)
        if self.is_shuffle and len(surplus_indices) > 0:
            self._rng.shuffle(surplus_indices)

        surplus_iter = iter(surplus_indices)
        
        for chunk_id, indices in chunks.items():
            current_len = len(indices)
            if current_len < target_size:
                needed_count = target_size - current_len
                fillers = [next(surplus_iter) for _ in range(needed_count)]
                chunks[chunk_id] = np.concatenate([indices, np.array(fillers)])
                
        return chunks
    
    def get_n_splits(self):
        return self.n_chunks

    def _trim_global_excess(self, X, y, group):
        """Removes indices from largest groups so total count fits n_chunks."""
        total_samples = X.shape[0]
        remainder = total_samples % self.n_chunks
        
        if remainder == 0:
            self._remainder = np.array([])
            return X, y, group
        
        group_df = pd.DataFrame(group, index = map(tuple, X)) # type: ignore
        y_df = pd.DataFrame(y, index = map(tuple, X)) # type: ignore
        
        y_df['is_remainder'] = False
        
        for _ in range(remainder):
            y_df['count'] = 0
            c_y_df = y_df[~y_df['is_remainder']].copy()
            
            for i in range(y.shape[1]):
                c_y_df['count'] += c_y_df.groupby(y_df.columns[i]).transform('size')
            idx_to_update = c_y_df['count'].idxmax()
            y_df.loc[[idx_to_update], 'is_remainder'] = True
                    
        self._remainder = np.stack(y_df[y_df['is_remainder']].index.values) # type: ignore
        
        select = y_df[~y_df['is_remainder']]
            
        return np.stack(select.index.values), select[range(y.shape[1])].values, group_df.loc[select.index.values].values  # type: ignore