import os

from Lib_classes.Paths import Paths
from Source.Download.DatasetLoader import DatasetLoader


class AggregationLoader:
    def __init__(self, loaders: list[DatasetLoader]):
        self.loaders = loaders

    def run_all(self):
        os.makedirs(Paths.dir_source, exist_ok=True)
        for loader in self.loaders:
            loader.load()

