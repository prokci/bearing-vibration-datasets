import os
from typing import Final

import numpy as np
import scipy
import scipy.io

from MyMath.Conversions import by_fH_to_rpm, by_ft_lb_s_to_W, by_inch_to_mm
from Source.Source_aggregate.Bearing.FileArchitectures import (
    BearingDatasetFileWithFolders,
)


class MFPTFileArchitectures(BearingDatasetFileWithFolders):
    extension = 'mat'
    
    settings:Final[dict] = {
        '1 - Three Baseline Conditions':{
            'fc' : 25,
            'load': 270,
            'discretizations': 97_656,
            'type' : 'n',
        },
        '2 - Three Outer Race Fault Conditions':{
            'fc' : 25,
            'load': 270,
            'discretizations': 97_656,
            'type' : 'o',
        },
        '3 - Seven More Outer Race Fault Conditions':{
            'fc' : 25,
            'load': [25,50,100,150,200,250,300],
            'discretizations': 48_828,
            'type' : 'o',
        },
        '4 - Seven Inner Race Fault Conditions':{
            'fc' : 25,
            'load': [0, 25, 50, 100, 150, 200, 250, 300],
            'discretizations': 48_828,
            'type' : 'i',
        }
    }
    
    bearing_params:Final[dict] = {
        'd0': by_inch_to_mm(1.245),
        'dT': by_inch_to_mm(0.235),
        'zT' : 8,
        'b' : 0,
        'rotation' : 'internal',
        'rolling_body' : 'ball'
    }
    
    def get_file(self, name, path):
        name_path = self.buld_path_str(name, path)
        data_dict = scipy.io.loadmat(name_path)
        
        data = np.array(data_dict['bearing']['gs'][0][0])
        data = np.reshape(data, (data.shape[0]))
        
        load = data_dict['bearing']['load'][0][0][0][0]
        if isinstance(load, str):
            load = int(data_dict['bearing']['load'][0][0][0])


        def get_type_defect(type: str):
            inner, ball, outer = False, False, False
            if type == 'n':
                pass
            else:
                if type.find('i') != -1:
                    inner = True
                if type.find('o') != -1:
                    outer = True
            return inner, ball, outer
            
        
        config = MFPTFileArchitectures.settings.get(os.path.basename(path), None)
        if config is None:
            return []
        
        inner, ball, outer = get_type_defect(config['type'])

        # ft = config['load'] if not isinstance(config['load'], list) else config['load'][int(name[-1])]

        from Source.Source_aggregate.SourceAggregator import SourceAggregator
        return [SourceAggregator.valid_make_row(
            data,
            rpm = by_fH_to_rpm(config['fc']),
            samples_by_second = config['discretizations'],
            place = 'base',
            inner_race = inner,
            ball = ball,
            outer_race= outer,
            original_path = name_path,
            fault = -1,
            load_w = by_ft_lb_s_to_W(load),
            id_bearing = '',
            weight = 1,
            object_params = self.bearing_params
        )]