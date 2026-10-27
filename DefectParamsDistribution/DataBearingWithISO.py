

from typing import ClassVar

from DefectParamsDistribution.DataBearing import DataBearing


class DataBearingWithISO(DataBearing):
    need_column:ClassVar = {
        'bearing':['ss_bearing', 'di', 'de','rolling_body', 'b', 'rpm_max', 'ISO' ],#'type_bearing',
        'bearing_2':['ss_bearing', 'radial_load_max'], #'type_bearing_2','di', 'de'
        'rolling_bodies':['ss_bearing',  'dT', 'zT', 'mT', 'steel_grade'],
        'steel_grade':['steel_grade', 'p'],
        'radial_load_norm':['ratio_radial_load_from_not', 'ratio_radial_load_to_is', 'rotation_diameter_from_not', 'rotation_diameter_to_is']
    }