
from collections import defaultdict
from typing import Dict, List, Optional
import numpy as np

class EqualSizeSplitter:
    """
    Pure Fabrication responsible for splitting a dataset of indices into
    exactly N chunks of equal size, maintaining stratification.
    """
    def __init__(self,  rng: np.random.Generator, n_chunks: Optional[int] = None, size_chunk: Optional[int] = None, size: Optional[int] = None):
        self._rng = rng
        if size_chunk is not None and size is not None:
            self.n_chunks = size//size_chunk
            self.max_size_chunk = size_chunk
        elif n_chunks is not None:
            self.n_chunks = n_chunks
        self._n_group_remains_determined = self.n_chunks

    def split(self, groups: Dict[str, List[int]]) -> Dict[int, List[int]]:
        """
        Distributes indices from groups into chunks.
        
        1. Trims global excess to ensure total_size % n_chunks == 0.
        2. Distributes main body of groups evenly.
        3. Distributes remainders probabilistically to balance chunk sizes.
        """
        # Create a working copy to avoid side effects
        working_groups = {k: v.copy() for k, v in groups.items()}
        
        tail_idx = self._trim_global_excess(working_groups)
        
        chunks = defaultdict(list)
        
        # Sort keys to ensure deterministic processing order
        sorted_keys = sorted(working_groups.keys())
        c_working_groups = len(working_groups)
        for key in sorted_keys:
            indices = working_groups[key]
            self._rng.shuffle(indices)
            
            self._split_group(indices, chunks, c_working_groups)
            c_working_groups-=1
        
        chunks[max(chunks.keys())+1] = tail_idx
        for key, val in chunks.items():
            chunks[key] = self._rng.permutation(val).tolist()
        
        return dict(chunks)

    def _trim_global_excess(self, groups: Dict[str, List[int]]) -> list:
        """Removes indices from largest groups so total count fits n_chunks."""
        tail_idx = []
        total_samples = sum(len(v) for v in groups.values())
        if hasattr(self, 'max_size_chunk'):
            remainder = total_samples % self.max_size_chunk
        else:
            remainder = total_samples % self.n_chunks
        
        if remainder == 0:
            return []

        # Strategy: Remove from the largest groups to preserve rare classes
        for _ in range(remainder):
            largest_group_key = max(groups, key=lambda k: len(groups[k]))
            if groups[largest_group_key]:
                # Remove a random element
                idx_to_remove = self._rng.integers(0, len(groups[largest_group_key]))
                tail_idx.append(groups[largest_group_key].pop(idx_to_remove))
                
        return tail_idx

    def _split_group(self, indices: List[int], chunks: Dict[int, List[int]], n_group_remains:int) -> None:
        """Splits a single group's indices across chunks."""
        need_size = len(indices)//self.n_chunks
        if need_size == 0:
            self._split_underloaded_chunk(indices, chunks, n_group_remains)
        else:
            for chunk in range(self.n_chunks):
                if need_size != 0:
                    current_group = indices[:need_size]
                    if len(current_group) != need_size:
                        raise ValueError('len(current_group) != need_size')
                    chunks[chunk].extend(indices[:need_size])
                    del indices[:need_size]
        
        if len(indices) != 0:
            self._split_group(indices, chunks, n_group_remains)

    def _split_underloaded_chunk(self, indices: List[int], chunks: Dict[int, List[int]], n_group_remains:int ):
        """
        Selects a chunk index based on inverse probability of current size.
        Smaller chunks have higher probability of being selected.
        """
        p = np.zeros((self.n_chunks,))
        for key, chunk in chunks.items():
            p[key] = len(chunk)
        p = np.max(p)-p+1
        p = p/np.sum(p)
        
        if n_group_remains > self._n_group_remains_determined: 
            i_select = self._rng.choice(
                np.arange(self.n_chunks),
                size = (len(indices), ),
                p = p,
                replace = False
            )
            
            for chunk in i_select:
                chunks[chunk].append(indices.pop(0))
        else:
            for _ in range(len(indices)):
                get_key = min(chunks.keys(), key=lambda k: len(chunks[k]))
                chunks[get_key].append(indices.pop())