
import numpy as np
import scipy
import scipy.io
import re

from MyMath.Conversions import  by_fH_to_rpm
from Source.Source_aggregate.Bearing.FileArchitectures import BearingDatasetFileArchitectures


class HUSTFileArchitectures(BearingDatasetFileArchitectures):
    base_params = {
        'b': 0.0,              
        'rpm': 1500.0,        
        'p': 7850.0,           
        'E': 2.1e11,           
        'rotation': 'internal',
        'rolling_body': 'ball', 
        'fr_c': 0.15,          
        'radial_load': 1000.0,   
        'type': 'rolling',     
    }

    density_kg_mm3 = 7.85e-6
    calc_ball_mass = lambda dT: (4/3) * np.pi * ((dT / 2)**3) * 7.85e-6

    MAP_BOUND = "id_bearing"

    BEARING_PARAMS = {
        "6204": {
            **base_params,
            'bearing_id': '6204',
            'di': 20.0,
            'de': 47.0,
            'dT': 7.6,
            'zT': 8,
            'mT': calc_ball_mass(7.6),
        },
        "6205": {
            **base_params,
            'bearing_id': '6205',
            'di': 25.0,
            'de': 52.0,
            'dT': 7.8,
            'zT': 9,
            'mT': calc_ball_mass(7.8),
        },
        "6206": {
            **base_params,
            'bearing_id': '6206',
            'di': 30.0,
            'de': 62.0,
            'dT': 9.0,
            'zT': 9,
            'mT': calc_ball_mass(9.0),
        },
        "6207": {
            **base_params,
            'bearing_id': '6207',
            'di': 35.0,
            'de': 72.0,
            'dT': 11.0,
            'zT': 9,
            'mT': calc_ball_mass(11.0),
        },
        "6208": {
            **base_params,
            'bearing_id': '6208',
            'di': 40.0,
            'de': 80.0,
            'dT': 12.0,
            'zT': 9,
            'mT': calc_ball_mass(12.0), 
        }
    }
    def get_file(self, name):
        path = self.buld_path_str(name)
        data_dict = scipy.io.loadmat(path)
        
        def get_type_defect(type: str):
            inner, ball, outer = False, False, False
            if type == 'N':
                pass
            else:
                if type.find('I') != -1:
                    inner = True
                if type.find('B') != -1:
                    ball = True
                if type.find('O') != -1:
                    outer = True
            return inner, ball, outer
            
        
        format = re.search(r'^(\D{1,2})(\d)0(\d)$', name)
        if format is not None:
            data = np.array(data_dict['data'])
            data = data.reshape(data.shape[0])
            
            inner, ball, outer = get_type_defect(format.group(1))
        
            from Source.Source_aggregate.SourceAggregator import SourceAggregator
            return [SourceAggregator.valid_make_row(
                data,
                rpm = by_fH_to_rpm(data_dict['fs'][0][0]),
                samples_by_second = 51_200,
                place = 'base',
                inner_race = inner,
                ball = ball,
                outer_race= outer,
                original_path = path,
                fault = 0.2,
                load_w = float(format.group(3)+'00'),
                id_bearing = '620' + format.group(2),
                weight = 1,
                object_params = {'rotation': 'internal'},
            )]
        
        else:
            raise Exception(f"Error: file {name} has incorrect name format.")
