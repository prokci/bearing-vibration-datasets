from Source.Download.CWRUDatasetLoader import DatasetCWRULoader
from Source.Download.DatasetZipLoader import DatasetZipLoader
from Source.Download.HitwzcDatasetLoader import HitwzcDatasetLoader
from Source.Download.KAtDatasetLoader import KatDatasetLoader
from Source.Download.MFPTDatasetLoader import MFPTDatasetLoader
from Source.Download.MultiDomainDatasetLoader import MultiDomainDatasetLoader

DOWNLOAD_SPEC = [
    {
        'name':'CWRU',
        'download_url':'',
        'page_url': 'https://engineering.case.edu/bearingdatacenter/download-data-file',
        'load':DatasetCWRULoader
    },
    {
        'name': 'fm6xzxnf36-2',
        'download_url':'https://data.mendeley.com/public-api/zip/fm6xzxnf36/download/2',
        'page_url': 'https://data.mendeley.com/datasets/fm6xzxnf36/2',
        'load':DatasetZipLoader
    },
    {
        'name':'HUST',
        'download_url':'https://data.mendeley.com/public-api/zip/cbv7jyx4p9/download/3',
        'page_url': 'https://bmcresnotes.biomedcentral.com/articles/10.1186/s13104-023-06400-4',
        'load':DatasetZipLoader
    },
    {
        'name':'MFPT',
        'download_url':'https://www.kaggle.com/api/v1/datasets/download/emperorpein/mfpt-fault-datasets',
        'page_url': 'https://www.mfpt.org/fault-data-sets/',
        'load':MFPTDatasetLoader
    },
    {
        'name':'KAt',
        'download_url':'https://groups.uni-paderborn.de/kat/BearingDataCenter/',
        'page_url': 'https://groups.uni-paderborn.de/kat/BearingDataCenter/',
        'load':KatDatasetLoader
    },
    {
        'name':'JNU',
        'download_url':'https://github.com/ClarkGableWang/JNU-Bearing-Dataset/archive/refs/heads/main.zip',
        'page_url': 'https://bmcresnotes.biomedcentral.com/articles/10.1186/s13104-023-06400-4',
        'load':DatasetZipLoader
    },
    {
        'name':'Multi-domain1',
        'download_url':'https://data.mendeley.com/public-api/zip/53vtnjy6c6/download/1',
        'page_url': 'https://data.mendeley.com/datasets/53vtnjy6c6/1',
        'load':MultiDomainDatasetLoader
    },
    {
        'name':'Multi-domain2',
        'download_url':'https://data.mendeley.com/public-api/zip/7trwzz77xh/download/1',
        'page_url': 'https://data.mendeley.com/datasets/7trwzz77xh/1',
        'load':MultiDomainDatasetLoader
    },
    {
        'name':'Multi-domain3',
        'download_url':'https://data.mendeley.com/public-api/zip/2cygy6y4rk/download/1',
        'page_url': 'https://data.mendeley.com/datasets/2cygy6y4rk/1',
        'load':MultiDomainDatasetLoader
    },
    {
        'name':'SCA',
        'download_url':'https://data.mendeley.com/public-api/zip/tdn96mkkpt/download/2',
        'page_url': 'https://data.mendeley.com/datasets/tdn96mkkpt/2',
        'load':DatasetZipLoader
    },
    {
        'name':'hitwzc',
        'download_url':'https://github.com/hitwzc/Bearing-datasets/archive/refs/heads/main.zip',
        'page_url': 'https://github.com/hitwzc/Bearing-datasets',
        'load':HitwzcDatasetLoader
    },
    {
        'name':'XJTU-SY',
        'download_url':'https://github.com/prokci/xjtu-su-mirror/archive/refs/heads/main.zip',
        'page_url': 'https://biaowang.tech/xjtu-sy-bearing-datasets/',
        'load':DatasetZipLoader
    }
]