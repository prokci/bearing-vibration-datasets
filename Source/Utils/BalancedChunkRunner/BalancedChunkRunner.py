
import pandas as pd
from typing import Dict, List
from collections import defaultdict
from Source.Utils.BalancedChunkRunner.ABalancedChunkRunner import ABalancedChunkRunner

class BalancedChunkRunner(ABalancedChunkRunner):
    def generate_chunk_indices(self) -> Dict[int, List[int]]:
        """
        Loads a file, groups data by signature, and returns balanced chunk indices.
        """
        cum_groups = defaultdict(list)
        for i in self.pfa.iter_stack_index():
            df = self.pfa.get_file(i)
            groups = self._group_data(df, i)
            [cum_groups[k].extend(v) for k, v in groups.items()]
            
        chunk_map = self._splitter.split(cum_groups)
        
        return chunk_map
    
    def _group_data(self, df: pd.DataFrame, c_file:int) -> Dict[str, List[int]]:
        """Groups DataFrame indices by their stratification signature."""
        groups = defaultdict(list)
        
        for idx, row in df.iterrows():
            signature = self._signature_strategy.get_signature(row)
            groups[signature].append((c_file, idx))
        return dict(groups)