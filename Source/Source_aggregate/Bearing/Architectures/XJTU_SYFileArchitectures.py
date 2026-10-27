from copy import deepcopy
from typing import Final

import pandas as pd

from MyMath.Conversions import by_fH_to_rpm
from Source.Source_aggregate.Bearing.FileArchitectures import (
    BearingDatasetFileWithFolders,
)


class XJTU_SYFileArchitectures(BearingDatasetFileWithFolders):
    extension = 'csv'
    depth = 2
    
    subfolder: Final[dict[str, dict]] = {
        '1_1':{
            'type': 'o',
            'fs' : 35
        }, 
        '1_2':{
            'type': 'o',
            'fs' : 35,
        }, 
        '1_3':{
            'type': 'o',
            'fs' : 35,
        }, 
        '1_4':{
            'type': 'n',
            'fs' : 35,
        },
        '1_5':{
            'type': 'oi',
            'fs' : 35,
        },
        '2_1':{
            'type': 'i',
            'fs' : 37.5,
        }, 
        '2_2':{
            'type': 'o',
            'fs' : 37.5,
        }, 
        '2_3':{
            'type': 'n',
            'fs' : 37.5,
        },
        '2_4':{
            'type': 'o',
            'fs' : 37.5,
        },
        '2_5':{
            'type': 'o',
            'fs' : 37.5,
        },
        '3_1':{
            'type': 'o',
            'fs':40,
        },
        '3_2':{
            'type': 'ibo',
            'fs':40,
        },
        '3_3':{
            'type': 'i',
            'fs':40,
        },
        '3_4':{
            'type': 'i',
            'fs':40,
        },
        '3_5':{
            'type': 'o',
            'fs':40,
        },
    }
    
    id_bearing = 'LDK UER204'
    bearing_params: Final[dict] = {
        'di': 20,
        'de': 47,
        'dT': 7.94,
        'zT': 7,
        'b': 0,
        'rolling_body': 'ball',
        'rotation': 'internal'
    }
    
    
    def get_file(self, name, folder, subfolder):
        path = self.buld_path_str(name, folder, subfolder)
        
        
        def get_type_defect(type: str):
            inner, ball, outer = False, False, False
            if type == 'n':
                pass
            else:
                if type.find('i') != -1:
                    inner = True
                if type.find('b') != -1:
                    ball = True
                if type.find('o') != -1:
                    outer = True
            return inner, ball, outer
            
        metadata = self.subfolder[subfolder[-3:]]
        
        pd_data = pd.read_csv(path)
        weight = [pd_data[col].to_numpy() for col in pd_data.columns]
        from Source.Source_aggregate.SourceAggregator import SourceAggregator
        res_list = []
        for data in weight:
            inner, ball, outer = get_type_defect(metadata['type'])
        
            res_list.append(SourceAggregator.valid_make_row(
                data,
                rpm = by_fH_to_rpm(metadata['fs']),
                samples_by_second = 25_600,
                place = 'base',
                inner_race = inner,
                ball = ball,
                outer_race= outer,
                original_path = path,
                fault = -1,
                load_w = -1,
                id_bearing = self.id_bearing,
                weight = 1/len(weight),
                object_params = deepcopy(self.bearing_params)
            ))
        return res_list