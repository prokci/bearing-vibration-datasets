
from copy import deepcopy

import scipy.io
import re
import os
from os.path import abspath

from MyMath.Conversions import by_HP_to_W, by_fH_to_rpm, by_inch_to_mm
from Source.Source_aggregate.Bearing.FileArchitectures import BearingDatasetFileArchitectures

class HitwzcFileArchitectures(BearingDatasetFileArchitectures):
    extension = 'mat'
    
    bearing_id = '6205'
    bearing_params = {
        'rotation': 'internal',
    }
    
    def get_file(self, name):
        path = self.buld_path_str(name)
        
        
        def get_type_defect(type: str):
            inner, ball, outer = False, False, False
            if type == 'n':
                pass
            else:
                if type.find('IR') != -1:
                    inner = True
                if type.find('N') != -1:
                    ball = True
                if type.find('OR') != -1:
                    outer = True
            return inner, ball, outer
            
        
        format = re.search(r'^([A-Za-z]{2,6})(\d{0,1})_(\d{3,4})$', name)
        if format is not None:
            np_dict = scipy.io.loadmat(path)
            data = np_dict[next(iter((key for key in np_dict.keys() if not key.startswith('__'))))].flatten()
            
            inner, ball, outer = get_type_defect(format.group(1))
        
            from Source.Source_aggregate.SourceAggregator import SourceAggregator
            return [SourceAggregator.valid_make_row(
                data,
                rpm = float(format.group(3)),
                samples_by_second = 51_200,
                place = 'base',
                inner_race = inner,
                ball = ball,
                outer_race= outer,
                original_path = path,
                fault = -1,
                load_w = -1,
                id_bearing = self.bearing_id,
                weight = 1,
                object_params = deepcopy(self.bearing_params)
            )]
        
        else:
            raise Exception(f"Error: file {name} has incorrect name format.")