import pandas as pd

from Source.Utils.Signature.MultiSignature import MultiSignature


class MultiSimpleStraficater(MultiSignature):
    def __init__(self, labels):
        self._labels = labels
    
    def get_signature(self, row:pd.Series):
        return row[self._labels].to_numpy().astype(int)
    
    def get_size(self):
        return len(self._labels)