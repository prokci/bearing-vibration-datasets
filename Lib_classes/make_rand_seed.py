import random

import numpy as np


def make_rand_seed(seed=42):
    np.random.seed(seed)
    random.seed(seed)