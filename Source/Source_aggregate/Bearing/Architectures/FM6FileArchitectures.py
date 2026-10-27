
import numpy as np
import pandas as pd
import re

from Source.Source_aggregate.Bearing.FileArchitectures import BearingDatasetFileWithFolders




import numpy as np
import pandas as pd
import re

from scipy import stats

from Source.Source_aggregate.Bearing.FileArchitectures import BearingDatasetFileWithFolders


class FM6FileArchitectures(BearingDatasetFileWithFolders):
    
    extension = 'csv'
    
    # def buld_path_str(self, name: str, folder:str):
    #     return self.path + f'\\{folder}' + f'\\{name}.' + self.extension
    
    # def iter(self):
    #     for path_folder in os.listdir(self.path):
    #         if path_folder != 'metadata.json':
    #             for _, path, _ in Paths.get_all_expasion_for_path(self.path + '\\' + path_folder, self.extension):
    #                 name = Paths.get_name_from_path(path)
    #                 yield self.get_file(name, path_folder)
        
    def get_file(self, name: str, folder:str):
        path = self.buld_path_str(name, folder)
        data_dict = pd.read_csv(path)
        rows = []
        if not name.endswith('pulley'):
            if re.search(r'^\d+.\d+\D+-\d+watt(-\w+)*$', name) is None:
                raise Exception('name format not supported')
        
        def get_data(colum):
            return np.array(data_dict[colum].to_list())
        
        def get_rpm() -> float:
            return -1
            
        def get_sample_by_second():
            return 10_000
        
        def get_place():
            return 'base'
        
        def get_type_defect():
            inner = False
            ball = False
            outer = False
            
            if not name.endswith('pulley'):
                start = re.search(r'^\d+.\d+', name).span()[1] # type: ignore
                end = re.search(r'^\d+.\d+\D+', name).span()[1] # type: ignore
                
                name_type = name[start:end-1]
                if name_type == 'inner':
                    inner = True
                elif name_type == 'outer':
                    outer = True
                else:
                    raise ValueError(f'unknown type {name_type}')
            
            return inner, ball, outer 
        
        def get_fault():
            if name.endswith('pulley'):
                return -1
            
            return float(re.search(r'^\d.\d',name).group(0)) # type: ignore
        
        def get_load_W():
            if name.endswith('pulley'):
                return -1
            
            span = re.search(r'-\d+watt', name).span() # type: ignore
            return float(f'{name[span[0]+1:span[1]-4]}')
        
        
        
        rpm = get_rpm()
        place = get_place()
        inner, ball, outer = get_type_defect()
        fault = get_fault()
        load_W = get_load_W()
        id_bearing = ''
        
        ts = get_data('Time Stamp')
        count_row = pd.to_timedelta(ts).value_counts().sort_index().values[1:-1]
        samples_by_second = int(round(np.mean(count_row))) # type: ignore
        # confidence = 0.95
        # df = len(count_row) - 1
        
        # std_err = stats.sem(count_row)
        # print(stats.t.interval(confidence, df, loc=samples_by_second, scale=std_err))
        
        columns = [colum for colum in data_dict.columns if colum != 'Time Stamp']
        
        from Source.Source_aggregate.SourceAggregator import SourceAggregator
        for colum in (colum for colum in data_dict.columns if colum != 'Time Stamp'):
            rows.append(SourceAggregator.valid_make_row(
                data                   = get_data(colum),
                rpm                    = rpm,
                samples_by_second      = samples_by_second,
                place                  = place,
                inner_race             = inner,
                ball                   = ball,
                outer_race             = outer,
                original_path          = path,
                fault                  = fault,
                load_w                 = load_W,
                id_bearing             = id_bearing,
                weight                 = 1/len(columns)
            ))
        return rows