from typing import List

import numpy as np
import pandas as pd

from Source.Utils.Signature.BearingPathSignatureMulti import BearingPathSignatureMulti
from Source.Utils.Signature.MultiSignature import MultiSignature
from Source.Utils.Signature.MultiSimpleStraficater import MultiSimpleStraficater


class BearingFaultSignatureMulti(MultiSignature):
    """
    Concrete strategy for Bearing datasets. 
    Combines 'original_path' source and fault labels into a unique key.
    """
    def __init__(self, class_columns: List[str], sources:list):
        self._class_labels =  MultiSimpleStraficater(class_columns)
        self._path_labels = BearingPathSignatureMulti(sources)
        self._labels = [f'{class_},{path_}' for class_ in self._class_labels.labels for path_ in self._path_labels.labels]
        self._labels_dict = dict(zip(self._labels, range(len(self._labels))))
        

    def get_signature(self, row: pd.Series) -> np.ndarray:
        path = self._path_labels.get_signature(row)
        classes = self._class_labels.get_signature(row)
        zer = np.zeros((self._class_labels.get_size(), self._path_labels.get_size())) 
        zer[np.where(classes>0)[0], np.where(path>0)[0]] = 1
        return zer.flatten()
    
    def get_size(self):
        return len(self._labels)