from abc import abstractmethod
from typing import List

import numpy as np
import pandas as pd


class MultiSignature:
    _labels: List[str]
    """
    Abstract Strategy for defining how a data row is classified 
    for stratification purposes.
    """
    @abstractmethod
    def get_signature(self, row: pd.Series) -> np.ndarray:
        """Returns a unique string key representing the stratum of the row."""
        pass
    
    @abstractmethod
    def get_size(self)-> int:...
    
    @property
    def labels(self)-> List[str]: return self._labels