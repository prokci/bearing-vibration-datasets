import os
import re
from urllib.parse import urljoin

import tqdm

from Source.Download.DatasetLoader import DatasetLoader
from Source.Download.HTML import Html


class KatDatasetLoader(DatasetLoader):
    def load(self):
        self.prepare_directory()
        r = self.session.get(self.download_url, Html.header,timeout=30)
        r.raise_for_status()
        rar_links = set(re.findall(r'href=["\']([^"\']+\.rar)["\']', r.text))
        for link in tqdm.tqdm(rar_links, desc=f'[{self.dataset_name}] Downloading'):
            if not link.startswith('http'):
                link = urljoin(self.download_url, link)
            filename = os.path.basename(link)
            dest = os.path.join(self.base_dir, filename)
            if self.download_file(link, dest):
                self.extract_rar(dest, self.base_dir, recursive_rebase=False)