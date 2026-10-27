from collections import defaultdict

import numpy as np
import pandas as pd

from DefectConfiguration.Strateges.StageStrategy import DefectConfStageStrategy
from DefectSignalGeneration.Sign.SignSimilarityRunner import SignSimilarityRunner
from Source.Source_generator.UniqueSignPdformat import UniqueSignPdformat
from Source.Utils.Signature.MultiSignature import MultiSignature


class WithoutReduceStageSignClassExtract(MultiSignature):
    def __init__(self, zero_data):
        self._zero_classis = UniqueSignPdformat.get_not_zero_classes(zero_data)
        self._labels = sorted(list({label for label in self._zero_classis}))
        
    def get_signature(self, row: pd.Series) -> np.ndarray:
        def get_key_defect(item):
            if len(item[1]) != 1:
                raise ValueError(f"sing not unique it has several params {item[1]}")
            
            if item[1][0]['defect'] == 'bearing overall':
                stage = np.random.uniform(0.0, 1.0-DefectConfStageStrategy.MIN_STAGE_RESERVE)
            else:
                stage = row['stages'][item[1][0]['defect']]
            if stage > 4.0 or stage < 0.0:
                raise ValueError(f"stage out of range {stage}")
            else:
                return item[0], stage
                
        stages = {k: v for k, v in (get_key_defect(item) for item in row['signs'].items())}
        
        code_labels = np.fromiter(
            (stages.get(lab, 0) for i, lab in enumerate(self._labels)), 
            dtype = np.float32, 
            count = self.get_size()
        )
        return code_labels
    
    def get_size(self):
        return len(self._labels) 
    
class StageSignClassExtract(MultiSignature):
    def __init__(self, zero_data, similary_data, reduce_func):
        self._reduce_map = SignSimilarityRunner.load_map(similary_data)
        self._zero_classis = UniqueSignPdformat.get_not_zero_classes(zero_data)
        self._labels = sorted(list({self._reduce_map[label] for label in self._zero_classis}))
        self._reduce_func = reduce_func
        
    def get_signature(self, row: pd.Series) -> np.ndarray:
        def get_key_defect(item):
            if len(item[1]) != 1:
                raise ValueError(f"sing not unique it has several params {item[1]}")
            
            if item[1][0]['defect'] == 'bearing overall':
                stage = np.random.uniform(0.0, 1.0-DefectConfStageStrategy.MIN_STAGE_RESERVE)
            else:
                stage = row['stages'][item[1][0]['defect']]
            if stage > 4.0 or stage < 0.0:
                raise ValueError(f"stage out of range {stage}")
            else:
                return item[0], stage
            
        stages = defaultdict(list)
        for item in row['signs'].items():
            name, stage = get_key_defect(item)
            stages[self._reduce_map[name]].append(stage)
            
        code_labels = np.fromiter(
            (self._reduce_func(stages.get(lab, [0])) for i, lab in enumerate(self._labels)), 
            dtype = np.float32, 
            count = self.get_size()
        )
        return code_labels
    
    def get_size(self):
        return len(self._labels) 