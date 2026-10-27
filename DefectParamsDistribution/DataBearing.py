import os
from functools import cached_property
from typing import ClassVar

import numpy as np
import pandas as pd

from Lib_classes.Paths import Paths
from Lib_classes.Resource import MyResource


class DataBearing(MyResource):
    file_path: ClassVar[str] = os.path.join(Paths.dir_configs, 'bearing_configuration')
    list_names: ClassVar[list] = ['bearing','bearing_2','rolling_bodies','steel_grade','radial_load_norm']
    need_column: ClassVar[dict] = {
        'bearing':['ss_bearing', 'di', 'de','rolling_body', 'b', 'rpm_max', ],#'type_bearing',
        'bearing_2':['ss_bearing', 'radial_load_max'], #'type_bearing_2','di', 'de'
        'rolling_bodies':['ss_bearing',  'dT', 'zT', 'mT', 'steel_grade'],
        'steel_grade':['steel_grade', 'p'],
        'radial_load_norm':['ratio_radial_load_from_not', 'ratio_radial_load_to_is', 'rotation_diameter_from_not', 'rotation_diameter_to_is']
    }
    radial_load_norm_min: ClassVar[float] = 0.0001
    radial_load_norm_max: ClassVar[float] = 0.9
    
    def init(self, **kwds):
        super().init(**kwds)
        self.bearing_1 = self._get_resource_by_excel(self.list_names[0])
        self.bearing_2 = self._get_resource_by_excel(self.list_names[1])
        self.rolling_bodies = self._get_resource_by_excel(self.list_names[2])
        self.steel_grade = self._get_resource_by_excel(self.list_names[3])
        self.radial_load_norm = self._get_resource_by_excel(self.list_names[4])
        
    # def get_resource_by_excel(self, name)->pd.DataFrame:
    #     return pd.read_excel(DataBearing.file_path, sheet_name=name)[DataBearing.need_column[name]]
    
    @cached_property
    def all(self)->pd.DataFrame:
        bearing_all_ = self.bearing_1.merge(self.bearing_2, on="ss_bearing", how="outer")
        bearing_all_ = bearing_all_.merge(self.rolling_bodies, on="ss_bearing", how="outer")
        bearing_all_ = bearing_all_.merge(self.steel_grade, on="steel_grade", how="outer")
        # bearing_all_.set_index('ss_bearing', inplace=True)
        return bearing_all_
    
    @cached_property
    def all_not_null(self)->pd.DataFrame:
       bearing_all_ = self.bearing_1.merge(self.bearing_2, on="ss_bearing", how="inner")
       bearing_all_ = bearing_all_.merge(self.rolling_bodies, on="ss_bearing", how="inner")
       bearing_all_ = bearing_all_.merge(self.steel_grade, on="steel_grade", how="inner")
       bearing_all_ = bearing_all_.loc[bearing_all_.isna().any(axis=1)==False]
    #    bearing_all_.set_index('ss_bearing', inplace=True)
       return bearing_all_
       #return 
    
    
    def find_norm_ratio_radial_load(self, d_rotation):
        def if_need_fix_ratio_radial_load(rr_from_not, rr_to_is):
            rr_from_not = rr_from_not if not np.isnan(rr_from_not) else self.radial_load_norm_min
            rr_to_is = rr_to_is if not np.isnan(rr_to_is) else self.radial_load_norm_max
            return rr_from_not, rr_to_is
        
        for rr_from_not, rr_to_is, from_not, to_is in zip(self.radial_load_norm['ratio_radial_load_from_not'],
                                        self.radial_load_norm['ratio_radial_load_to_is'],
                                        self.radial_load_norm['rotation_diameter_from_not'],
                                        self.radial_load_norm['rotation_diameter_to_is']):
            
            if np.isnan(from_not) and d_rotation <= to_is:
                yield if_need_fix_ratio_radial_load(rr_from_not, rr_to_is)
            elif np.isnan(to_is) and from_not > d_rotation:
               yield if_need_fix_ratio_radial_load(rr_from_not, rr_to_is)
            elif from_not > d_rotation and d_rotation <= to_is:
                yield if_need_fix_ratio_radial_load(rr_from_not, rr_to_is)