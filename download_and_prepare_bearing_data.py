import re
from argparse import ArgumentParser

from prepare_bearing_data import prepare_bearing_data
from Source.Download.AggregationLoader import AggregationLoader
from Source.Download.download_spec import DOWNLOAD_SPEC

if __name__ == "__main__":
    arguments = ArgumentParser()
    arguments.add_argument('--datasets', nargs='+', type = str, default = ['CWRU', 'HUST', 'MFPT','Multi-domain1', 'Multi-domain2', 'Multi-domain3', 'SCA', 'hitwzc','XJTU-SY'])#'KAt',
    arguments.add_argument('--n_chunks', type = int, default = 5)
    arguments.add_argument('--rng', type = int, default = None)
    arguments.add_argument('--n_signals_per_chunk_with_disbalance', type = int, default = 200)
    arguments.add_argument('--n_signals_per_chunk', type = int, default = 5000)
    arguments.add_argument('--need_params', nargs='+', default = ['zT', 'dT', 'd0', 'rotation', 'rolling_body'])
    arguments.add_argument('--split_proportion', nargs='+', type=int, default=[3, 1, 1])
    arguments.add_argument('--split_names', nargs='+', default=['train', 'validate', 'test'])
    args = arguments.parse_args()
    
    download_names = [x['load'](x['name'], x['download_url'], x['page_url']) for x in DOWNLOAD_SPEC if x['name'] in args.datasets]
    
    if sum(args.split_proportion) != args.n_chunks:
        raise ValueError("The sum of split_proportion must equal n_chunks")
    
    app = AggregationLoader(download_names)
    app.run_all()
    
    args.split_proportion = [int(x) for x in args.split_proportion]
    args.datasets = [re.sub(r'\d+$', '',  dataset) for dataset in args.datasets]
    prepare_bearing_data(**vars(args))