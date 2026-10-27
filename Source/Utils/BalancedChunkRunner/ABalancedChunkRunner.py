from abc import abstractmethod
from typing import Dict, List
import numpy as np
from Lib_classes.FileArchitecture import PdPickleFileArchitecture
from Source.Utils.Signature.BearingFaultSignature import ASignature
from Source.Utils.Spliters.EqualSizeSplitter import EqualSizeSplitter
from Source.Utils.ProviderChunksMixin.ProviderChunksMixin import ProviderChunksMixin

class ABalancedChunkRunner(ProviderChunksMixin):
    def __init__(self, 
                 pfa: PdPickleFileArchitecture,
                 spliter: EqualSizeSplitter,
                 signature_strategy: ASignature,
                 rng: np.random.Generator
        ):
        super().__init__(pfa, rng) 
        self._signature_strategy = signature_strategy
        self._splitter = spliter
    @abstractmethod
    def generate_chunk_indices(self)-> Dict[int, List[int]]:...
