import os

from Source.Download.DatasetLoader import DatasetLoader


class DatasetZipLoader(DatasetLoader):
    def load(self, headers=None):
        self.prepare_directory()
        zip_path = os.path.join(self.base_dir, 'dataset.zip')
        if self.download_file(self.download_url, zip_path, added_headers=headers):
            self.extract_zip(zip_path, self.base_dir)
