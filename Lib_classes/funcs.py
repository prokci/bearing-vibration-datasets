import functools
import operator
from typing import TypeVar

import numpy as np

TObj = TypeVar('TObj')
def raise_none(obj: None| TObj) -> TObj: 
    if obj is None:
        raise TypeError(obj)
    else:
        return obj


def set_like(func, *set_like):    
    return list(func(*(set(i) for i in set_like)))

def set_like_order(func, *set_likes):
    all = functools.reduce(operator.iadd, (list(set_like) for set_like in set_likes), [])
    after_func = set_like(func, *set_likes)
    return [i for i in all if i in after_func]

        
def get_max_len_key(dict_:dict):
    max_key = next(iter(dict_.keys()))
    for key in dict_:
        if len(dict_[key]) > len(dict_[max_key]):
            max_key = key
    return max_key


def get_min_len_key(dict_:dict):
    min_key = next(iter(dict_.keys()))
    for key in dict_:
        if len(dict_[key]) < len(dict_[min_key]):
            min_key = key
    return min_key


def get_seed(rng: np.random.Generator):
    return rng.integers(0, np.iinfo(np.int32).max)
