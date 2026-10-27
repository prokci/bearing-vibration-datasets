import math
from typing import Any

import numpy as np

from DefectParamsDistribution.DataBearingWithISO import DataBearingWithISO
from Lib_classes.Logger import Logger, LoggerEmpty


class BearingParamsFiller:
    db_mapping = {
        'de': 'de',
        'di': 'di',
        'zT': 'zT',
        'dT': 'dT',
        'mT': 'mT',
        'b': 'b',
        'p': 'p',
        'rolling_body': 'rolling_body',
        'rpm': 'rpm_max',             
        'radial_load': 'radial_load_max'
    }
    
    
    def __init__(
        self, 
        need_params: list[str], 
        bearing_config: DataBearingWithISO, 
        logger_warn: LoggerEmpty = LoggerEmpty('BearingParamsFiller(warn)'),
        logger_error: LoggerEmpty = Logger('BearingParamsFiller(error)'),
    ) -> None:
        """Filler and for bearing parameters

        Args:
            need_params (list[str]): paramas that need to be filled. Can be eny combination of the above:
                'dT' - ball diameter (mm)
                'd0' - pitch circle diameter(mm)
                'mT' - ball or rolling body mass (kg)
                'zT' - number of balls (integer)
                'di' - inner race diameter (mm)
                'de' - outer race diameter (mm)
                'b' - contact angle (degree)
                'rotation' - which race rotates (internal, external)
                'rolling_body' - type of rolling body (ball, rolling)
                'type' - bearing type (rolling, sliding)
                'accuracy' - accurate or approximate calculation (true, false)
                'slippage' - true if the rolling element slips in the rolling bearing (true, false)
                for autofull support or any other witch included in `bearing_config` or already exict in source.
                
                
            bearing_config (DataBearingWithISO): Bearing configuration for ISO codes.
            logger_warn (LoggerEmpty, optional): Logger for warnings. Defaults to LoggerEmpty('BearingParamsFiller(warn)').
            logger_error (LoggerEmpty, optional): Logger for errors. Defaults to Logger('BearingParamsFiller(error)').
        """
        
        self.need_params = need_params
        self.bearing_config = bearing_config
        self.logger_warn = logger_warn
        self.logger_error = logger_error
        self.config_table = self.bearing_config.all
        
        self.config_table['ISO'] = self.config_table['ISO'].astype('str').str.replace(' ','')
        
        self._is_undefined_bearing = False
        
        self.undefined_bearing = []
        

    def full(self, id_bearing: str, params: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """
        Populate the params dictionary strictly sequentially:
        1. Try to load missing params from configuration based on ISO (id_bearing)
        2. Calculate any remaining missing params mathematically or set reasonable defaults.
        """
        params = self._load_from_file(id_bearing, params)
        params = self._calculate_missing(params)
        self._check_unfilled(id_bearing, params)
        return id_bearing, params

    def _is_missing(self, param_key: str, params: dict[str, Any]) -> bool:
        """Helper to determine if a parameter is truly missing or empty."""
        return (
            param_key not in params or 
            params[param_key] is None or 
            (isinstance(params[param_key], float) and np.isnan(params[param_key])) or
            params[param_key] == ""
        )

    def _load_from_file(self, id_bearing: str, params: dict[str, Any]) -> dict[str, Any]:
        """Loads missing values from the configuration dataframe using the ISO code."""
        self._is_undefined_bearing = False
        if not id_bearing:
            self.logger_warn("id_bearing is empty. Skipping file load.")
            return params

        try:
            df = self.config_table
            
            if 'ISO' not in df.columns:
                self.logger_warn("'ISO' column is missing in DataBearing configuration dataframe.")
                return params
                
            bearing_data = self.config_table[self.config_table['ISO'].astype('str') == id_bearing]
            
            if bearing_data.empty:
                self.logger_warn(f"Bearing with ISO '{id_bearing}' not found in configuration file.")
                self._is_undefined_bearing = True
                return params

            row = bearing_data.iloc[0]
            new_params = row.to_dict()
            self.logger_warn(f"Loaded '{new_params} from config for ISO '{id_bearing}'.")
            new_params.update(params)
            params = new_params # type: ignore
        except Exception as e:
            self.logger_error(f"Exception occurred while loading from config for ISO '{id_bearing}': {e}")
            
        return params

    def _calculate_missing(self, params: dict[str, Any]) -> dict[str, Any]:
        """Calculates parameters that are still missing utilizing physical/geometrical logic."""
        def has(*args) -> bool:
            return all(not self._is_missing(a, params) for a in args)

        for param_name in self.need_params:
            if self._is_missing(param_name, params):
                calculated_val = None
                
                if param_name == 'dT':
                    if has('de', 'di'):
                        calculated_val = (params['de'] - params['di']) / 2.0
                        self.logger_warn("Calculated 'dT' approximately from 'de' and 'di'.")
                        
                elif param_name == 'd0':
                    if has('de', 'di'):
                        calculated_val = (params['de'] + params['di']) / 2.0
                        self.logger_warn("Calculated 'd0' approximately from 'de' and 'di'.")
                        
                elif param_name == 'mT':
                    if has('p', 'dT'):
                        if params.get('rolling_body') == 'ball':
                            dt_m = params['dT'] / 1000.0
                            volume = (math.pi / 6.0) * (dt_m ** 3)
                            calculated_val = params['p'] * volume
                            self.logger_warn("Calculated 'mT' (mass) from density 'p' and ball diameter 'dT'.")
                        else:
                            self.logger_warn("Cannot calculate 'mT'. Rolling body is not 'ball' (roller length unknown).")
                            
                elif param_name == 'zT':
                    if has('de', 'di', 'dT'):
                        pitch_d = (params['de'] + params['di']) / 2.0
                        calculated_val = int(math.floor((math.pi * pitch_d) / params['dT'] * 0.7))
                        self.logger_warn("Calculated 'zT' (ball number) approximately.")

                elif param_name == 'di':
                    if has('de', 'dT'):
                        calculated_val = params['de'] - (2.0 * params['dT'])
                        self.logger_warn("Calculated 'di' from 'de' and 'dT'.")

                elif param_name == 'de':
                    if has('di', 'dT'):
                        calculated_val = params['di'] + (2.0 * params['dT'])
                        self.logger_warn("Calculated 'de' from 'di' and 'dT'.")

                elif param_name == 'b':
                    calculated_val = 0.0
                    self.logger_error("Defaulted contact angle 'b' to 0.0 degrees.")
                    
                elif param_name == 'rotation':
                    calculated_val = 'internal'
                    self.logger_error("Defaulted 'rotation' to 'internal'.")
                    
                elif param_name == 'rolling_body':
                    calculated_val = 'ball'
                    self.logger_error("Defaulted 'rolling_body' to 'ball'.")
                    
                elif param_name == 'type':
                    calculated_val = 'rolling'
                    self.logger_error("Defaulted 'type' to 'rolling'.")
                    
                elif param_name == 'accuracy':
                    calculated_val = False
                    self.logger_error("Defaulted 'accuracy' to False.")
                    
                elif param_name == 'slippage':
                    calculated_val = False
                    self.logger_error("Defaulted 'slippage' to False.")

                if calculated_val is not None:
                    params[param_name] = calculated_val
                else:
                    self.logger_warn(f"Could not calculate missing parameter '{param_name}': insufficient base parameters.")

        return params

    def _check_unfilled(self, bearing_id, params: dict[str, Any]):
        """Logs a warning for any required parameters that are still missing."""
        for param_name in self.need_params:
            if self._is_missing(param_name, params):
                self.logger_error(f"Parameter '{param_name}' remains unfilled after loading and calculation.")
                if self._is_undefined_bearing and bearing_id not in self.undefined_bearing:
                    self.undefined_bearing.append(bearing_id)