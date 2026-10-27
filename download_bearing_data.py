from argparse import ArgumentParser

from Source.Download.AggregationLoader import AggregationLoader
from Source.Download.download_spec import DOWNLOAD_SPEC

if __name__ == "__main__":
    arguments = ArgumentParser()
    arguments.add_argument('--datasets', nargs='+', type = str, default = [ 'CWRU', 'HUST', 'KAt','Multi-domain1', 'Multi-domain2', 'Multi-domain3', 'SCA', 'hitwzc', 'XJTU-SY' ])
    args = arguments.parse_args()
    select_datasets = args.datasets
    
    download_names = [x['load'](x['name'], x['download_url'], x['page_url']) for x in DOWNLOAD_SPEC if x['name'] in select_datasets]
    app = AggregationLoader(download_names)
    app.run_all()