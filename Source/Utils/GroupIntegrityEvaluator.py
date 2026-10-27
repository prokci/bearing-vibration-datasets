from typing import Dict, List, Set

import pandas as pd
from sklearn.metrics import completeness_score

from Source.Utils.Signature.ASignature import ASignature


class GroupIntegrityEvaluator:
    """
    Pure Fabrication: Evaluates if distinct data groups (e.g., specific bearings, 
    machines, or recording sessions) are leaking across chunks.
    
    Uses Scikit-Learn's Completeness Score.
    """
    def __init__(self, group_signature: ASignature):
        self._group_signature = group_signature
        
        # Storing parallel arrays of true group IDs and assigned chunk IDs
        self._true_groups: List[str] = []
        self._assigned_chunks: List[int] = []
        
    def add_chunk(self, chunk_df: pd.DataFrame, chunk_id: int) -> None:
        """
        Records the group signatures and chunk assignments for a given split.
        """
        if chunk_df.empty:
            return
            
        signatures =[self._group_signature.get_signature(row) for _, row in chunk_df.iterrows()]
        
        self._true_groups.extend(signatures)
        self._assigned_chunks.extend([chunk_id] * len(signatures))

    def _calculate_completeness(self):
        """
        Calculates metric: 1.0 means all elements of every true group 
        were assigned to exactly one chunk.
        """
        if not self._true_groups:
            return 0.0
            
        return completeness_score(
            labels_true=self._true_groups, 
            labels_pred=self._assigned_chunks
        )

    def _identify_leaked_groups(self) -> Dict[str, Set[int]]:
        """
        Information Expert: Maps groups to chunks to find which groups span boundaries.
        Returns a dictionary of only the leaked groups.
        """
        group_to_chunks: Dict[str, Set[int]] = {}
        
        for group, chunk in zip(self._true_groups, self._assigned_chunks):
            if group not in group_to_chunks:
                group_to_chunks[group] = set()
            group_to_chunks[group].add(chunk)
            
        return {
            group: chunks 
            for group, chunks in group_to_chunks.items() 
            if len(chunks) > 1
        }

    def report(self) -> None:
        """Controller: Orchestrates the calculation and printing of the evaluation."""
        if not self._true_groups:
            print("No data provided for evaluation.")
            return

        score = self._calculate_completeness()
        leaked_groups = self._identify_leaked_groups()
        total_groups = len(set(self._true_groups))
        
        print("\n--- Group Integrity & Leakage Report ---")
        print(f"Completeness Score: {score:.4f}")
        print(f"Total Unique Groups: {total_groups}")
        print(f"Leaked Groups (Spanning multiple chunks): {len(leaked_groups)}\n")
        
        if leaked_groups:
            print("Data Leakage Detected.")
            self._print_leakage_details(leaked_groups)
        else:
            print("No leakage.")

    def _print_leakage_details(self, leaked_groups: Dict[str, Set[int]], max_display: int = 10) -> None:
        """Handles formatting details to avoid massive console dumps."""
        for i, (group, chunks) in enumerate(leaked_groups.items()):
            if i >= max_display:
                break
            print(f"Group '{group}' split across chunks: {list(chunks)}")
            
        if len(leaked_groups) > max_display:
            print(f"... and {len(leaked_groups) - max_display} more leaked groups.")