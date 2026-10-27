import numpy as np
import pandas as pd

from Source.Utils.Signature.MultiSignature import MultiSignature


class MultiLabelStratificationError:
    def __init__(self, signature: MultiSignature):
        self.chunk_distributions = []
        self.signature = signature
        
    def add_chunk(self, df: pd.DataFrame):
        y_chunk = np.array([self.signature.get_signature(row) for _, row in df.iterrows()])
        if np.any((y_chunk != 1) & (y_chunk != 0)):
            raise ValueError("Stratification signature must be binary")
        
        class_counts = y_chunk.sum(axis=0)
        self.chunk_distributions.append(class_counts)
        print(class_counts)


    def report(self):
        chunk_distributions = np.array(self.chunk_distributions)
        global_class_counts = chunk_distributions.sum(axis=0)
        expected_counts_per_chunk = global_class_counts / chunk_distributions.shape[0]
        


        with np.errstate(divide='ignore', invalid='ignore'):
            abs_diff = np.abs(chunk_distributions - expected_counts_per_chunk)
            percent_error = (abs_diff / expected_counts_per_chunk) * 100
            percent_error = np.nan_to_num(percent_error)


        mean_error_per_class = percent_error.mean(axis=0)
        overall_mean_error = percent_error.mean()

        print("\n--- Stratification Error Report ---")
        print(f"Overall Distribution Error: {overall_mean_error:.2f}%\n")

        print("Error by Class:")
        for i, (err, count) in enumerate(zip(mean_error_per_class, global_class_counts)):
            class_name = self.signature.labels[i]
            print(f"{class_name.ljust(20)} | Total samples: {int(count):<6} | Error: {err:.2f}%")
    
#Overall Distribution Error: 1.85% //without equal
#Overall Distribution Error: 2% //with equal
#Overall Distribution Error: 2.8% //without stratifity