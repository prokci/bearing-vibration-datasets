import numpy as np
import pandas as pd

from Source.Utils.Signature.BearingFaultSignature import BearingFaultSignature
from Source.Utils.Signature.MultiSignature import MultiSignature


class BearingPathSignatureMulti(BearingFaultSignature, MultiSignature):
    """
    Concrete strategy for Bearing datasets. 
    Combines 'original_path' source and fault labels into a unique key.
    """
    def __init__(self, sources:list):
        self._labels = sources
        self._path_labels = dict(zip(sources, range(len(sources))))

    def get_signature(self, row: pd.Series) -> np.ndarray:
        path = self._path_labels[self._get_path(row)]
        coded_path = np.zeros((len(self._path_labels)))
        coded_path[path] = 1
        return coded_path
    
    def get_size(self):
        return len(self._labels)