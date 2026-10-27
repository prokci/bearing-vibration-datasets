from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from Lib_classes.Paths import Paths
from Source.Utils.Signature.ASignature import ASignature


EPSILON = np.finfo(np.float32).eps


class BearingFaultSignature(ASignature):
    """
    Concrete strategy for Bearing datasets. 
    Combines 'original_path' source and fault labels into a unique key.
    """
    def __init__(self, class_columns: List[str], rng: np.random.Generator):
        self.class_columns = class_columns
        self._rng = rng

    def get_signature(self, row: pd.Series) -> str:
        return f"{self._get_path(row)}_{self._get_reduce_class(row)}"
    
    def _get_path(self, row: pd.Series) -> str:
        return Path(row['original_path']).parts[len(Path(Paths.dir_source).absolute().parts)]
    
    def _get_reduce_class(self, row: pd.Series) -> str:
        fault_vector:np.ndarray = row[self.class_columns].values.astype(np.float32) # type: ignore
        fault_sum = np.sum(fault_vector)
        
        if fault_sum == 0:
            group_idx = 0.0
        elif fault_sum == 1:
            group_idx = np.where(fault_vector > 1.0 - EPSILON)[0].item() + 1
        else:
            active_indices = np.where(fault_vector > 1.0 - EPSILON)[0]
            if active_indices.size > 0:
                picked = self._rng.choice(active_indices)
                group_idx = float(picked) + 1
            else:
                group_idx = 0.0
        return str(int(group_idx))