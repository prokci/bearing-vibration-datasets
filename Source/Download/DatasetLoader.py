import json
import os
import shutil
import zipfile

import rarfile
from dotenv import load_dotenv

load_dotenv()
_unrar_env = os.getenv("UNRAR_TOOL")
if _unrar_env and not (os.name != "nt" and (":" in _unrar_env or "\\" in _unrar_env or _unrar_env.endswith(".exe"))):
    rarfile.UNRAR_TOOL = _unrar_env
else:
    rarfile.UNRAR_TOOL = "unrar"

import time

import requests
import tqdm
from urllib3.exceptions import IncompleteRead, ProtocolError

from Lib_classes.Paths import Paths

UNIT_DIVISOR = 1024



class DatasetLoader:
    def __init__(self, dataset_name, download_url, page_url):
        self.dataset_name = dataset_name
        self.download_url = download_url
        self.base_dir = os.path.join(Paths.dir_source, self.dataset_name)
        self.session = requests.Session()
        self.page_url = page_url

    def prepare_directory(self):
        self.cleanup()
        self.add_metadata()
        
    def cleanup(self):
        if os.path.exists(self.base_dir):
            shutil.rmtree(self.base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def download_file(self, url, dest_path, max_retries=50, show_progress=True, chunk_in_kb=64, added_headers=None):
        downloaded_bytes = os.path.getsize(dest_path) if os.path.exists(dest_path) else 0
        total_size = 0
        retries = 0
        
        self.session.trust_env = False

        while total_size == 0 or downloaded_bytes < total_size:
            headers = {}
            if added_headers is not None:
                headers.update(added_headers)
                
            if downloaded_bytes > 0:
                headers['Range'] = f'bytes={downloaded_bytes}-'

            try:
                with self.session.get(url, stream=True, headers=headers, timeout=30) as r:
                    r.raise_for_status()
                    
                    if r.status_code == 206:
                        mode = 'ab'
                    elif r.status_code == 200:
                        mode = 'wb'
                        downloaded_bytes = 0
                    
                    if total_size == 0:
                        content_length = r.headers.get('content-length')
                        if content_length:
                            total_size = downloaded_bytes + int(content_length)
                    
                    if total_size != 0 and downloaded_bytes >= total_size:
                        print(f"[{self.dataset_name}] File already fully downloaded.")
                        return True

                    with open(dest_path, mode) as f:
                        if show_progress:
                            bar = tqdm.tqdm(
                                desc=f'[{self.dataset_name}] Downloading',
                                total=total_size if total_size > 0 else None,
                                initial=downloaded_bytes, 
                                unit='B',
                                unit_scale=True,
                                unit_divisor=UNIT_DIVISOR,
                            ).__enter__()
                        for chunk in r.iter_content(chunk_size=chunk_in_kb * UNIT_DIVISOR):
                            if chunk:
                                f.write(chunk)
                                downloaded_bytes += len(chunk)
                                if show_progress:
                                    bar.update(len(chunk))
                                
                        if show_progress:
                            bar.__exit__(None, None, None)
                            
                        return True

            except (requests.exceptions.RequestException, ProtocolError, IncompleteRead) as e:
                retries += 1
                if retries > max_retries:
                    raise RuntimeError(f"Download failed after {max_retries} attempts.") from e
                
                wait_time = min(retries * 2, 30)
                tqdm.tqdm.write(f"\n[Warning] {str(e).rstrip('.')}({type(e)}). Resuming after {wait_time}s...")
                time.sleep(wait_time)

        return True
        

    def extract_zip(self, zip_path, extract_to, recursive_rebase=True):
        tqdm.tqdm.write(f"[{self.dataset_name}] Extracting {zip_path} -> {extract_to}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            
        os.remove(zip_path)
        if recursive_rebase:
            self.recursive_rebase_folder(extract_to)
        
    def extract_rar(self, rar_path, extract_to, recursive_rebase=True):
        tqdm.tqdm.write(f"[{self.dataset_name}] Extracting {rar_path} -> {extract_to}")
        with rarfile.RarFile(rar_path, 'r') as rar_ref:
            rar_ref.extractall(extract_to)
        
        os.remove(rar_path)
        if recursive_rebase:
            self.recursive_rebase_folder(extract_to)
        
    def recursive_rebase_folder(self, extract_to, recursive_rebase=True):
        folders = [full_path for obj in os.listdir(extract_to) if (os.path.isdir(full_path:=os.path.join(extract_to, obj)))]
        if len(folders) == 1: 
            Paths.rebase_folder(folders[0])
            self.recursive_rebase_folder(extract_to)
        
    def load(self):
        self.prepare_directory()
        zip_path = os.path.join(self.base_dir, 'dataset.zip')
        if self.download_file(self.download_url, zip_path):
            self.extract_zip(zip_path, self.base_dir)
            
    def add_metadata(self):
        metadata = {
            'name': self.dataset_name,
            'url': self.page_url
        }
        metadata_path = os.path.join(self.base_dir, 'metadata.json')
        with open(metadata_path, 'w') as file:
            json.dump(metadata, file)