import re

import scipy.io as sio

from Source.Source_aggregate.Bearing.FileArchitectures import (
    BearingDatasetFileWithFolders,
)


class MultiDomainFileArchitectures(BearingDatasetFileWithFolders):
    depth = 2
    bearing_params = {
        "N204": {
            'di': 20.0,
            'de': 47.0,
            'dT': 5.9,
            'zT': 13,
            'b': 0.0,
            'mT': 0.0014,
            'type': 'rolling',
            'rolling_body': 'rolling',
        },
        "30204": {
            'di': 20.0,
            'de': 47.0,
            'dT': 6.5,
            'zT': 15,
            'b': 13.0,        
            'mT': 0.0014,
            'type': 'rolling',
            'rolling_body': 'rolling',
        },
        "NJ204": {
            'di': 20.0,
            'de': 47.0,
            'dT': 5.97,
            'zT': 11,
            'b': 0.0,         
            'mT': 0.0014,
            'type': 'rolling',
            'rolling_body': 'rolling',
        }
    }

    

    def get_file(self, name: str, folder: str, under_folder:str):
        file_path = self.buld_path_str(name, folder, under_folder)
        mat_data = sio.loadmat(file_path)

        if 'Data' not in mat_data:
            raise ValueError(f"File {file_path} does not contain required 'Data' field.")

        data = mat_data['Data'].flatten()
        metadata = self.parse_filename(name)

        from Source.Source_aggregate.SourceAggregator import SourceAggregator
        return [SourceAggregator.valid_make_row(
            data=data,
            rpm=metadata["rpm"],
            samples_by_second=metadata["sampling_rate"] * 1000,
            place="base",  
            inner_race=metadata["bearing_condition"] == "IR",
            ball=metadata["bearing_condition"] == "B",
            outer_race=metadata["bearing_condition"] == "OR",
            original_path=file_path,
            fault=-1,  # Adjust based on fault data, if available
            load_w=-1,  # Adjust based on load data, if available
            id_bearing=metadata["bearing_model"],
            weight=1,
            object_params={
                'rotation': 'internal', 
                **(self.bearing_params[metadata["bearing_model"]] if metadata["bearing_model"] in self.bearing_params else {})
            }
        )]

    def parse_filename(self, filename):
        match = re.match(r'^([A-Z\d]{1,2})_([A-Z]{1,2})_(\d{1,2})_([A-Z\d]{4,6})_(\d{3,4})$', filename)
        if not match:
            raise ValueError(f"Invalid file name format: {filename}")

        rotating_component_condition, bearing_condition, sampling_rate, bearing_model, rpm = match.groups()
        
        return {
            "rotating_component_condition": rotating_component_condition,
            "bearing_condition": bearing_condition,
            "sampling_rate": int(sampling_rate),
            "bearing_model": bearing_model,
            "rpm": int(rpm)
        }