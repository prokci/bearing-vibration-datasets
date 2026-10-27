from abc import ABC, abstractmethod

import pandas as pd


class ASignature(ABC):
    """
    Abstract Strategy for defining how a data row is classified 
    for stratification purposes.
    """
    @abstractmethod
    def get_signature(self, row: pd.Series) -> str:
        """Returns a unique string key representing the stratum of the row."""
        pass