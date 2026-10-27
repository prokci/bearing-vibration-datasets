import json
import os

from Source.Download.DatasetZipLoader import DatasetZipLoader


class MultiDomainDatasetLoader(DatasetZipLoader):
    def add_metadata(self):
        metadata = {
            'name': self.dataset_name[:-1],
            'url': self.page_url
        }
        metadata_path = os.path.join(self.base_dir, 'metadata.json')
        with open(metadata_path, 'w') as file:
            json.dump(metadata, file)