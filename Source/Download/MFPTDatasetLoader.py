import os
import shutil

from Source.Download.DatasetZipLoader import DatasetZipLoader
from Source.Source_aggregate.Bearing.Architectures.MFPTFileArchitectures import (
    MFPTFileArchitectures,
)


class MFPTDatasetLoader(DatasetZipLoader):
    def load(self):
        super().load(
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        for name in os.listdir(self.base_dir):
            path = os.path.join(self.base_dir, name)
            if os.path.isdir(path) and MFPTFileArchitectures.settings.get(name, None) is None:
                shutil.rmtree(path)
        