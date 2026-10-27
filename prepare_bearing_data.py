
import os
import shutil
from argparse import ArgumentParser

import numpy as np
from tqdm import tqdm

from DefectParamsDistribution.DataBearingWithISO import DataBearingWithISO
from Lib_classes.DataFrameFilesBuilderStack import DataFrameStackBuilder
from Lib_classes.FileArchitecture import PdPickleFileArchitecture
from Lib_classes.Logger import Logger, LoggerEmpty
from Lib_classes.Paths import Paths
from Source.Source_aggregate.Bearing.BindClasses import bind_classess
from Source.Source_aggregate.Callbacks.BearingParamsFillerCallback import (
    BearingParamsFillerCallback,
)
from Source.Source_aggregate.Callbacks.RpmFilter import RpmFilter
from Source.Source_aggregate.SourceAggregator import SourceAggregator
from Source.Source_aggregate.SourceAggregatorWithCallbacks import (
    SourceAggregatorWithCallbacks,
)
from Source.Utils.BalancedChunkRunner.SkLearnBalancedChunkRunner import (
    SkLearnBalancedChunkRunner,
)
from Source.Utils.Signature.BearingFaultSignatureMulti import BearingFaultSignatureMulti
from Source.Utils.Signature.PathSignature import PathSignature
from Source.Utils.Spliters.EqualSizeForScikitSplitter import EqualSizeForScikitSplitter
from Source.Utils.Spliters.MultilabelStratifiedGroupKFold import (
    MultilabelStratifiedGroupKFold,
)


def prepare_bearing_data(
    datasets = None,
    n_chunks = 5,
    rng = None,
    n_signals_per_chunk_with_disbalance = 1000,
    n_signals_per_chunk = 5000,
    need_params = None,
    split_proportion = None,
    split_names = None,
):
    if rng is None:
        rng = np.random.default_rng(42)
    elif isinstance(rng, int):
        rng = np.random.default_rng(rng)
        
    if need_params is None:
        need_params = ['zT', 'dT', 'd0', 'rotation', 'rolling_body']
        
    if split_proportion is None:
        split_proportion = [3, 1, 1]
        
    if split_names is None:
        split_names = ['train', 'validate', 'test']
        
    if datasets is None:
        datasets = ['CWRU', 'fm6xzxnf36-2', 'HUST', 'JNU', 'KAt', 'MFPT','Multi-domain', 'SCA', 'hitwzc', 'XJTU-SY']
        
    if sum(split_proportion) != n_chunks:
        raise ValueError("The sum of split_proportion must equal n_chunks")


    target_folder = os.path.join(Paths.dir_dataframe_pickles, 'Bearing')
    balance_chunk_path = os.path.join(target_folder, SourceAggregator.CHUNK_FOLDER_NAME)

    all_sources = list(filter(lambda x: x.find('.') == -1, os.listdir(Paths.dir_source)))
    selected_sources = {name:source for name, source in bind_classess.items() if name in datasets}
    
    rf = RpmFilter()
    bear_params = BearingParamsFillerCallback(
        need_params = need_params,
        bearing_config = DataBearingWithISO(),
        logger_warn = LoggerEmpty('BearingParamsFiller(warn)'),
        logger_error = Logger('BearingParamsFiller(error)')
    )

    sa = SourceAggregatorWithCallbacks(
        max_stack_size=n_signals_per_chunk_with_disbalance, 
        path = target_folder,
        bind_classess = selected_sources,
        callbacks=[rf, bear_params], 
    )

    sa()

    pfa = PdPickleFileArchitecture.open(target_folder)
    bcr = SkLearnBalancedChunkRunner(
        pfa,
        EqualSizeForScikitSplitter(MultilabelStratifiedGroupKFold(n_splits = n_chunks), rng, is_equalizing = False, add_remainder = False),
        BearingFaultSignatureMulti(SourceAggregator.REAL_CLASS_ORDER, all_sources),
        PathSignature(),
        rng,
    )


    chunks = bcr.generate_chunk_indices()

    pmf = PdPickleFileArchitecture(
        balance_chunk_path,
        max_stack_size=len(next(iter(chunks.values())))
    )
    for k_, df in tqdm(bcr.provide_chunks(chunks), total=n_chunks):
        pmf.add_file(df)

    for file in os.listdir(os.path.join(target_folder)):
        path = os.path.join(target_folder, file)
        if not os.path.isdir(path) and path.endswith(PdPickleFileArchitecture.extension):
            os.remove(os.path.abspath(path))


    pdpickle = PdPickleFileArchitecture.open(balance_chunk_path, n_signals_per_chunk)

    count = 0
    for chunks, folder_name in zip(split_proportion, split_names):
        current_pdpickle = PdPickleFileArchitecture(os.path.join(target_folder, folder_name), len(pdpickle.get_file(count)))
        for i in range(chunks):
            df = pdpickle.get_file(count)
            current_pdpickle.add_file(df)
            count += 1

    shutil.rmtree(balance_chunk_path)

    train_path = os.path.join(target_folder,'train')
    temp_train_path = os.path.join(target_folder,'train_temp')

    train = PdPickleFileArchitecture.open(train_path)
    with DataFrameStackBuilder(train.get_columns().to_list(), PdPickleFileArchitecture(temp_train_path, 1000)) as builder:
        for i in train.iter_stack_index():
            df = train.get_file(i)
            builder.add_df(df)
            
    shutil.rmtree(train_path)
    os.rename(temp_train_path, train_path)
    

if __name__ == "__main__":
    arguments = ArgumentParser()
    
    arguments.add_argument('--datasets', nargs='+', default=[ 'CWRU', 'HUST', 'KAt', 'Multi-domain', 'SCA', 'hitwzc', 'XJTU-SY'])
    arguments.add_argument('--n_chunks', type = int, default = 5)
    arguments.add_argument('--rng', type = int, default = None)
    arguments.add_argument('--n_signals_per_chunk_with_disbalance', type = int, default = 200)
    arguments.add_argument('--n_signals_per_chunk', type = int, default = 5000)
    arguments.add_argument('--need_params', nargs='+', default = ['zT', 'dT', 'd0', 'rotation', 'rolling_body'])
    arguments.add_argument('--split_proportion', nargs='+', type=int, default=[3, 1, 1])
    arguments.add_argument('--split_names', nargs='+', default=['train', 'validate', 'test'])


    args = arguments.parse_args()
    args.split_proportion = [int(x) for x in args.split_proportion]
    prepare_bearing_data(**vars(args))
    
    