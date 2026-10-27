import os
import re
from typing import Final

import tqdm

from Source.Download.DatasetLoader import DatasetLoader
from Source.Download.HTML import Html


class DatasetCWRULoader(DatasetLoader):
    
    SITES: Final[list] = [
        {
            'url':'https://engineering.case.edu/bearingdatacenter/normal-baseline-data',
            'prefix':'norm'
        }, 
        {
            'url':'https://engineering.case.edu/bearingdatacenter/12k-drive-end-bearing-fault-data',
            'prefix':'12k-drive'
        },
        {
            'url':'https://engineering.case.edu/bearingdatacenter/48k-drive-end-bearing-fault-data',
            'prefix':'48k-drive'
        },
        {
            'url':'https://engineering.case.edu/bearingdatacenter/12k-fan-end-bearing-fault-data',
            'prefix':'12k-fan'
        },
    ]

    def load(self):
        self.prepare_directory()
        for i in self.SITES:
            links = [(text, link) for text, link in Html.get_all_href(i['url']) if link.endswith('.mat')] # type: ignore
            for text, link in tqdm.tqdm(links, desc=f'[{self.dataset_name}] Downloading {i['prefix']}'):
                safe_text = re.sub(r'[\\/*?:"<>|]', '_', text)
                self.download_file(link, os.path.join(self.base_dir, f'{i["prefix"]}_{safe_text}.mat'), show_progress=False)
        
