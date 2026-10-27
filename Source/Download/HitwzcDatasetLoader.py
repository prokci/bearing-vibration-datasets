import json
import os
import shutil

from Lib_classes.Paths import Paths
from Source.Download.DatasetZipLoader import DatasetZipLoader


class HitwzcDatasetLoader(DatasetZipLoader):
    def load(self):
        super().load()
        for path in os.listdir(self.base_dir):
            if os.path.isdir(os.path.join(self.base_dir, path)):
                os.rename(os.path.join(self.base_dir, path), os.path.join(Paths.dir_source, path))
                shutil.copy2(os.path.join(self.base_dir, 'metadata.json'), os.path.join(Paths.dir_source, path, 'metadata.json'))
                
        shutil.rmtree(self.base_dir)
        
        
    def cleanup(self):
        for path in os.listdir(Paths.dir_source):
            if os.path.isdir(os.path.join(Paths.dir_source, path)) and os.path.exists(os.path.join(Paths.dir_source, path, 'metadata.json')):
                with open(os.path.join(Paths.dir_source, path, 'metadata.json'), 'r') as file:
                    metadata = json.load(file)
                if metadata['name'] == self.dataset_name:
                    shutil.rmtree(os.path.join(Paths.dir_source, path))
                
        os.makedirs(self.base_dir, exist_ok=True)