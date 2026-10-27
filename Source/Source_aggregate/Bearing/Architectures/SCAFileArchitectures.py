from typing import Final

import numpy as np
import scipy.io as sio

from Source.Source_aggregate.Bearing.FileArchitectures import (
    BearingDatasetFileWithFolders,
)


class SCAFileArchitectures(BearingDatasetFileWithFolders):
    depth = 1

    metadata:Final = {
            '1': {
                "Bearing": "22320",
                "Sampling Frequency (Hz)": 640,
                "Location": "wire_roller",
                "Location Side": "DS",
                "Fixed Speed": "No",
                "Average Rotation Speed (RPM)": 1120.6,
                "Fault Type": "i",
            },
            '2': {
                "Bearing": "6310",
                "Sampling Frequency (Hz)": 5120,
                "Location": "engine",
                "Location Side": "DS",
                "Fixed Speed": "Yes",
                "Average Rotation Speed (RPM)": 1162.0,
                "Fault Type": "o",
            },
            '3': {
                "Bearing": "6310",
                "Sampling Frequency (Hz)": 512,
                "Location": "wire_roller",
                "Location Side": "FS",
                "Fixed Speed": "No",
                "Average Rotation Speed (RPM)": 34.6,
                "Fault Type": "i",
            },
            '4': {
                "Bearing": "NU328",
                "Sampling Frequency (Hz)": 8192,
                "Location": "pump",
                "Location Side": "FS",
                "Fixed Speed": "No",
                "Average Rotation Speed (RPM)": 1100.3,
                "Fault Type": "i",
            },
            '5': {
                "Bearing": "7312",
                "Sampling Frequency (Hz)": 12800,
                "Location": "pump",
                "Location Side": "DS",
                "Fixed Speed": "No",
                "Average Rotation Speed (RPM)": 2483.5,
                "Fault Type": "b",
            },
            '6': {
                "Bearing": "NU328",
                "Sampling Frequency (Hz)": 6400,
                "Location": "pump",
                "Location Side": "FS",
                "Fixed Speed": "No",
                "Average Rotation Speed (RPM)": 1208.2,
                "Fault Type": "i"
            },
            '7': {
                "Bearing": "7221",
                "Sampling Frequency (Hz)": 4096,
                "Location": "strainer",
                "Location Side": "Upper",
                "Fixed Speed": "Yes",
                "Average Rotation Speed (RPM)": 700,
                "Fault Type": "i",
            },
            '8': {
                "Bearing": "6228",
                "Sampling Frequency (Hz)": 5120,
                "Location": "motor",
                "Location Side": "DS",
                "Fixed Speed": "No",
                "Average Rotation Speed (RPM)": 1105.9,
                "Fault Type": "o",
            },
            '9': {
                "Bearing": "6310",
                "Sampling Frequency (Hz)": 5120,
                "Location": "motor",
                "Location Side": "DS",
                "Fixed Speed": "Yes",
                "Average Rotation Speed (RPM)": 1162.0,
                "Fault Type": "o",
            },
            '10': {
                "Bearing": "NU316",
                "Sampling Frequency (Hz)": 5120,
                "Location": "motor",
                "Location Side": "DS",
                "Fixed Speed": "No",
                "Average Rotation Speed (RPM)": 189.3,
                "Fault Type": "o",
            },
            '11' : {
                "Bearing": "6228",
                "Sampling Frequency (Hz)": [5120, 12800],
                "Location": "motor",
                "Location Side": "FS",
                "Fixed Speed": "No",
                "Average Rotation Speed (RPM)": 189.3,
                "Fault Type": "n",
            }
    }
    
    bearing_params:Final = {
        "22320":{
            'di':100,
            'de':215,
            'dT':27,
            'zT':14,
            'type': 'rolling',
            'rolling_body': 'rolling',
        },
        "6228":{
            'di':140,
            'de':250,
            'dT':37.25,
            'zT':8,
            'type': 'rolling',
            'rolling_body': 'rolling',
        }, 
        "7312":{
            'di':60,
            'de':130,
            'dT':46.85,
            'zT':12,
            'type': 'rolling',
            'rolling_body': 'ball',
        }
    }

    def get_file(self, name: str, folder: str):
        file_path = self.buld_path_str(name, folder)
        mat_data = sio.loadmat(file_path)

        results = []
        # plasments = ["DS", "FS", "upper", "lower"]
        plasments = sorted(list(set(mat_data.keys()) & set(["DS", "FS", "upper", "lower"])))
        for placement in plasments:
            # if placement in mat_data.keys():
            placement_data = mat_data[placement]
            raw_data = placement_data["rawData"][0][0]
            if isinstance(raw_data[0][0], np.ndarray):
                raw_data = raw_data[0][0]

            sampling_rate = placement_data["samplingRate"].flatten()[0][0]
            rpm = placement_data["RPM"].flatten()[0][0]
            fault_labels = placement_data["label"].flatten()[0][0]

            for idx in range(len(raw_data)):
                from Source.Source_aggregate.SourceAggregator import SourceAggregator
                results.append(SourceAggregator.valid_make_row(
                    data=raw_data[idx],
                    rpm=rpm[idx],
                    samples_by_second=sampling_rate[idx],
                    place = SCAFileArchitectures.metadata[folder]['Location'],
                    inner_race=fault_labels[idx] == 1,
                    ball=fault_labels[idx] == 2,
                    outer_race=fault_labels[idx] == 3,
                    original_path=file_path,
                    fault=-1,
                    load_w=-1, 
                    id_bearing = SCAFileArchitectures.metadata[folder]['Bearing'],
                    weight=1/(len(raw_data) * len(plasments)),
                    object_params = {
                        'rotation': 'internal',
                        **(self.bearing_params.get(SCAFileArchitectures.metadata[folder]['Bearing'], {}))
                    }
                ))

        return results
        
        # f

        # for name in ['FS', ] :
        #     mat_data[name][0]

        # if 'vibration' not in mat_data:
        #     raise ValueError(f"File {file_path} does not contain required 'vibration' field.")

        # data = mat_data['vibration'].flatten()
        # metadata = SCAFileArchitectures.metadata[folder]
        
        # faul_type = 'n' if name == 'train' else metadata['Fault Type']

        # from Source_aggregate.SourceAggregator import SourceAggregator
        # return [SourceAggregator.valid_make_row(
        #     data=data,
        #     rpm=metadata["Average Rotation Speed (RPM)"],
        #     samples_by_second=metadata["Sampling Frequency (Hz)"],
        #     place=metadata["Location"],
        #     inner_race=faul_type == 'i',
        #     ball=faul_type == 'b',
        #     outer_race=faul_type== 'o',
        #     original_path=file_path,
        #     fault=-1,
        #     load_w=-1,  
        #     id_bearing=metadata["Bearing"]
        # )]

    