import pandas as pd
from itertools import count
from collections import defaultdict
from Source.Utils.Signature.ASignature import ASignature


class PathSignature(ASignature):
    def __init__(self):
        self.c_files = count()
        self.files = defaultdict(self.c_files.__next__)
    
    def get_signature(self, row: pd.Series) -> int:
        """Returns a unique string key representing the stratum of the row."""
        return self.files[row['original_path']]