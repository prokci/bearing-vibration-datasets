import random
import sys
import time
from io import StringIO
from typing import Final

import pandas as pd
import requests
import tqdm
from bs4 import BeautifulSoup


class Html:
    header: Final[dict] = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': '',
        'dnt': '1',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    } if sys.platform == "win32" else {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:149.0) Gecko/20100101 Firefox/149.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1",
        "If-None-Match": "0a87da3ea58c440d9ddd9ffe37aa6be7-ssl-df",
        "Priority": "u=0, i",
        "TE": "trailers"
    }
    
    @staticmethod
    def get_all_href(url):
        with requests.get(url, headers=Html.header) as response:
            soup = BeautifulSoup(response.text, 'html.parser')
            return ((a.text, a['href']) for a in soup.find_all('a', href=True))

    @staticmethod
    def get_all_tables(url):
        r = requests.get(url, headers=Html.header)
        dfs = pd.read_html(StringIO(str(r.text)), thousands=None)
        return dfs
    
    @staticmethod
    def delay():
        time.sleep(random.randint(126, 253)*0.001)