import re

import numpy as np
import pandas as pd

from Source.Source_aggregate.Bearing.FileArchitectures import (
    BearingDatasetFileArchitectures,
)


class JNUFileArchitectures(BearingDatasetFileArchitectures):
    extension = 'csv'
    def get_file(self, name):
        path = self.buld_path_str(name)
        
        
        def get_type_defect(type: str):
            inner, ball, outer = False, False, False
            if type == 'n':
                pass
            else:
                if type.find('ib') != -1:
                    inner = True
                if type.find('tb') != -1:
                    ball = True
                if type.find('ob') != -1:
                    outer = True
            return inner, ball, outer
            
        
        format = re.search(r'^(\D{1,2})(\d{3,4})(_3)*_2$', name)
        if format is not None:
            pd_data = pd.read_csv(path)
            data = pd_data[pd_data.columns[0]].to_list()
            data = [float(str) for str in sum([[pd_data.columns[0]], data], [])]
            data = np.array(data)

            # print(f"{name=}")
            # print(f"{format.group(1)=} {format.group(2)=}")
            inner, ball, outer = get_type_defect(format.group(1))
            # print(f"{inner=}, {ball=}, {outer=}")
        
            from Source.Source_aggregate.SourceAggregator import SourceAggregator
            return [SourceAggregator.valid_make_row(
                data,
                rpm = float(format.group(2)),
                samples_by_second = 50_000,
                place = 'base',
                inner_race = inner,
                ball = ball,
                outer_race= outer,
                original_path = path,
                fault = 0.3,
                load_w = -1,
                id_bearing = '',
                weight = 1
            )]
        
        else:
            raise Exception(f"Error: file {name} has incorrect name format.")
               