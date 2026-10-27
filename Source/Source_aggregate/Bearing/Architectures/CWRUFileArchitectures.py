
import random
import re
from copy import deepcopy

import numpy as np
import scipy
import scipy.io
from typing_extensions import Final

from MyMath.Conversions import by_HP_to_W, by_inch_to_mm
from Source.Source_aggregate.Bearing.FileArchitectures import (
    BearingDatasetFileArchitectures,
)


class CWRUFileArchitectures(BearingDatasetFileArchitectures):
    NORMAL_SPEC_INITILISATION = 'random'
    MAP_BOUND = "id_bearing"
    BEARING_PARAMS: Final[dict[str, dict]] = {
        "6205-2RS JEM SKF":{
            'di': 25.0, 
            'de': 52.0, 
            'dT': 7.94,  
            'zT': 9, 
            'b': 0.0,
            'rpm': 1760,  
            'radial_load': 500.0,  
            'mT': 0.0014, 
            'type': 'rolling',  
            'rolling_body': 'ball', 
            'rotation': 'internal',

            'p': 7850.0, 
            'E': 2.1e11
        },
        "6203-2RS JEM SKF":{
            'di': 17.0, 
            'de': 40.0, 
            'dT': 6.74,
            'zT': 8,  
            'b': 0.0, 
            'radial_load': 350.0, 
            'mT': 0.0014,
            'type': 'rolling',
            'rolling_body': 'ball',
            'rotation': 'internal',

            'p': 7850.0,
            'E': 2.1e11
        }
    }
    
    name_to_RPMs: Final[dict[str, int]] = {
        '0' : 1797,
        '1' : 1772,
        '2' : 1750,
        '3' : 1730
    }

    def get_file(self, name: str):
        path = self.buld_path_str(name)
        data_dict = scipy.io.loadmat(path)
        rows = []
        def get_data(key):
            data: np.ndarray = data_dict[key]
            return data.reshape(data.shape[0])
        
        def get_rpm() -> float:
            get_rpm_dict = lambda: self.name_to_RPMs[name[-1]]
            key = next(iter(filter(lambda key: key.endswith('RPM'), data_dict.keys())), '')
            return data_dict[key][0][0] if key != '' else get_rpm_dict()
            
        def get_sample_by_second():
            if name.startswith('48k-drive') or name.startswith('norm'):
                return 48_000
            else:
                return 12_000
        
        def place(key:str):
            to_full_name = {
                'DE':'drive end',
                'FE':'fan end',
                'BA': 'base'
            }
            ch_key = key[:key.find('_time')]
            ch_key = ch_key[-2:]
            return to_full_name[ch_key]
        
        def get_type_defect():
            inner = False
            ball = False
            outer = False
            
            if name.startswith('norm'):
                pass
            elif name.find('_B') != -1:
                ball = True
            elif name.find('_IR') != -1:
                inner = True
            elif name.find('_OR') != -1:
                outer = True
            return inner, ball, outer
        
        def get_faults():
            if name.startswith('norm'):
                return -1
            original_name = name[name.find('_')+1:]
            if re.search(r'^\D{1,2}\d{3}(@\d+)*_\d$', original_name) is not None:
                start = re.search(r'^\D{1,2}', original_name).span()[1] # type: ignore
                end = re.search(r'^\D{1,2}\d{3}', original_name).span()[1] # type: ignore
                return by_inch_to_mm(float(f'0.{original_name[start:end]}'))
            raise Exception('Not found faunts')
        
        def get_load_W():
            if name.startswith('norm'):
                return -1
            original_name = name[name.find('_')+1:]
            return by_HP_to_W(float(original_name[-1]))
        
        def get_bearing_id():
            to_bearing_id = {
                "drive": "6205-2RS JEM SKF",
                "fan": "6203-2RS JEM SKF"
            }
            if name.startswith('norm'):
                match self.NORMAL_SPEC_INITILISATION:
                    case 'random':
                        return random.choice(list(to_bearing_id.values()))
                    case 'drive':
                        return to_bearing_id['drive']
                    case 'fan':
                        return to_bearing_id['fan']
                    case _:
                        raise Exception('Not found bearing id')
            else:
                res = re.match(r'^(\d{1,2})k-(\D+)_(\D{1,2})(\d{3})(@\d+)*_(\d)$', name)
                if res is not None:
                    return to_bearing_id[res.group(2)]
                else:
                    raise Exception('Not found bearing id')
                     
        
        rpm = get_rpm()
        samples_by_second = get_sample_by_second()
        inner, ball, outer = get_type_defect()
        fault = get_faults()
        load_W = get_load_W()
        id_bearing = get_bearing_id()
        
        from Source.Source_aggregate.SourceAggregator import SourceAggregator
        
        keys = [key for key in data_dict.keys() if key.endswith('_time')]
        
        for key in keys:
            rows.append(SourceAggregator.valid_make_row(
                data                   = get_data(key),
                rpm                    = rpm,
                samples_by_second      = samples_by_second,
                place                  = place(key),
                inner_race             = inner,
                ball                   = ball,
                outer_race             = outer,
                original_path          = path,
                fault                  = fault,
                load_w                 = load_W,
                id_bearing             = id_bearing,
                weight                 = 1/len(keys),
                object_params         = deepcopy(self.BEARING_PARAMS[id_bearing])
            ))
        return rows