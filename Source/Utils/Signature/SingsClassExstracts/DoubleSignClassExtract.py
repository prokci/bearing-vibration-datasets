import numpy as np
import pandas as pd

from DefectSignalGeneration.Sign.SignSimilarityRunner import SignSimilarityRunner
from Source.Source_generator.UniqueSignPdformat import UniqueSignPdformat
from Source.Utils.Signature.MultiSignature import MultiSignature


class DoubleSignClassExtract(MultiSignature):
    def __init__(self, zero_data, similary_data, simulary_data2):
        self._reduce_map = SignSimilarityRunner.load_map(similary_data)
        self._reduce_map2 = SignSimilarityRunner.load_map(simulary_data2)
        self._zero_classis = UniqueSignPdformat.get_not_zero_classes(zero_data)
        self._labels = sorted(list({self._reduce_map2[self._reduce_map[label]] for label in self._zero_classis}))
        
    
    def get_signature(self, row: pd.Series) -> np.ndarray:
        c_labels = set(self._reduce_map2[self._reduce_map[keys]] for keys in row['signs'].keys())
        code_labels = np.zeros((self.get_size()))
        code_labels[list(i for i, lab in enumerate(self._labels) if lab in c_labels)] = 1
        return code_labels
    
    def get_size(self):
        return len(self._labels) 