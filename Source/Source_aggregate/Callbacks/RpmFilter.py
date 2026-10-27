from Source.Source_aggregate.Callbacks.SourceAggregatorCallback import SourceAggregatorCallback


class RpmFilter(SourceAggregatorCallback):
    def __init__(self):
        self.filtered_rows = []
    
    def filter_row(self, params):
        ans = params['rpm'] > 0 and params['rpm'] < 3000
        if not ans:
            self.filtered_rows.append(params)
        return ans