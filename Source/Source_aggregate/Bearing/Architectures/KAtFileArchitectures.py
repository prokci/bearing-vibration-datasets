import os
import re
from copy import deepcopy
from typing import Final

import mat73
import numpy as np
import pandas as pd
import scipy
import scipy.io

from MyMath.Conversions import by_fH_to_rpm
from MyMath.Signal.dominant_freq import get_dominant_freq
from Source.Source_aggregate.Bearing.FileArchitectures import (
    BearingDatasetFileWithFolders,
    file_path,
)


class KAtFileArchitectures(BearingDatasetFileWithFolders):
    extension = 'mat'
    POLE_PAIRS = 4
    RPM_RATE_ERROR = 0.15
    RPM_RATE_ERROR_INTERVAL = (1-RPM_RATE_ERROR, 1+RPM_RATE_ERROR)
    id_bearing = '6203'
    
    bearning_params:Final[dict] = {
        'd0': 29.05,
        'zT': 8,
        'dT': 6.75,
        'b': 0,
        'rotation': 'internal',
        'rolling_body': 'ball',
    }
    
    def __init__(self, path: str, max_stack_size: int = 10):
        super().__init__(path, max_stack_size)
        self.config_table = pd.read_csv(os.path.join(file_path, "Configs", "KatConfig.csv"))
  

    def try_get_file(self, path):
        if not path.endswith(self.extension):
            raise TypeError(path) 
    
        if os.path.getsize(path) == 0:
            raise TypeError(path, 'size')
        
        try:
            np_dict = scipy.io.loadmat(path)
        except (TypeError, NotImplementedError):
            try:
                np_dict = mat73.loadmat(path)
            except TypeError as e:
                raise TypeError(path)

        return np_dict
    
        

    def get_file(self, name, folder):
        path = self.buld_path_str(name, folder)
        
        def get_type_defect(folder: str):
            type = self.config_table[self.config_table['Bearing code'] == folder]['Bearing element'].item()
            inner, ball, outer = False, False, False
            if type == 'N':
                pass
            else:
                if type.find('IR') != -1:
                    inner = True
                if type.find('OR') != -1:
                    outer = True
                if not inner and not outer:
                    raise ValueError('unknown type defect')
            return inner, ball, outer
            
        
        format = re.search(r'^N(\d{2})_M(\d{2})_F(\d{2})_(K[\d\D]\d{2})_\d+$', name)
        if format is not None:
            rpm = int(format.group(1)+'00')
            load_torque = float(format.group(2))/10
            radial_force = float(format.group(3)+'00')
            
            try:
                #some files(/KA08/N15_M01_F10_KA08_2.mat) in Kat are corrupted
                np_dict = self.try_get_file(path)
            except TypeError:
                return []
            data = np_dict[next(iter(key for key in np_dict if not key.startswith('__')))]
            
            electro_phases = list(filter(lambda s: str(s[1][0]).startswith('phase_current'), enumerate(data[0][0]['Y']['Name'][0])))
            vibro_waveforms = list(filter(lambda s: str(s[1][0]).startswith('vibration'), enumerate(data[0][0]['Y']['Name'][0])))
            
            if len(vibro_waveforms) != 1:
                raise ValueError('file don\'t include one vibration')
            
            indx, _name = vibro_waveforms[0]
            
            signal = data[0][0]['Y']['Data'][0][indx][0]

            time = next(iter(data[0][0]['X']['Data'][0][i][0] for i in range(len(data[0][0]['X']['Data'][0])) if len(data[0][0]['X']['Data'][0][i][0]) == len(signal)))
            seconds = np.max(time) - np.min(time)
            dicritization = len(signal)/seconds
            
            
            rpms = [by_fH_to_rpm(get_dominant_freq(data[0][0]['Y']['Data'][0][indx][0], dicritization))/self.POLE_PAIRS for indx, _name in electro_phases]
            calc_rpm = np.mean(rpms).item()
            if not (rpm*self.RPM_RATE_ERROR_INTERVAL[0] < calc_rpm < rpm*self.RPM_RATE_ERROR_INTERVAL[1]):
                raise ValueError('calculating and declaring value don\'t match')
            
            inner, ball, outer = get_type_defect(folder)
        
            from Source.Source_aggregate.SourceAggregator import SourceAggregator
            return [SourceAggregator.valid_make_row(
                signal,
                rpm = calc_rpm,
                samples_by_second = dicritization,
                place = 'base',
                inner_race = inner,
                ball = ball,
                outer_race= outer,
                original_path = path,
                fault = -1,
                load_w = -1,
                id_bearing = self.id_bearing,
                weight = 1/len(vibro_waveforms),
                load_torque = load_torque,
                radial_force = radial_force,
                object_params = deepcopy(self.bearning_params)
            )]
            
            
        else:
            raise ValueError(f"Error: file {name} has incorrect name format.")