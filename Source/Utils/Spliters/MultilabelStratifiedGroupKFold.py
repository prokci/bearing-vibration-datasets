import numpy as np
import pandas as pd
from iterstrat.ml_stratifiers import MultilabelStratifiedKFold
from sklearn.model_selection import BaseCrossValidator


class MultilabelStratifiedGroupKFold(BaseCrossValidator):
    def __init__(self, n_splits=5, random_state=None, shuffle=False):
        self.n_splits = n_splits
        self.random_state = random_state
        self.shuffle = shuffle
        
        if self.random_state is not None:
            self.mskf = MultilabelStratifiedKFold(
                n_splits=self.n_splits, 
                random_state=self.random_state, 
                shuffle=self.shuffle
            )
        else:
            self.mskf = MultilabelStratifiedKFold(
                n_splits=self.n_splits, 
                shuffle=self.shuffle
            )
        
    def split(self, X, y, groups):
        y_arr = np.asarray(y)
        groups_arr = np.asarray(groups)
        
        df = pd.DataFrame(y_arr)
        df['group'] = groups_arr
        group_df = df.groupby('group').mean().round()
        
        assert ((group_df == 0.) | (group_df == 1.)).all().all(), "Each group must have a one label"
        
        groups_unique = group_df.index.values
        y_groups = group_df.values
        
        
        X_dummy = np.zeros(len(groups_unique))
        
        for train_groups_idx, val_groups_idx in self.mskf.split(X_dummy, y_groups):
            train_groups = groups_unique[train_groups_idx]
            val_groups = groups_unique[val_groups_idx]
            
            train_idx = np.where(np.isin(groups_arr, train_groups))[0]
            val_idx = np.where(np.isin(groups_arr, val_groups))[0]
            
            yield train_idx, val_idx
            
    def get_n_splits(self, X=None, y=None, groups=None):
        return self.n_splits