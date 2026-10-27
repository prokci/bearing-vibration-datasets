from copy import deepcopy
from typing import Any

from Source.Source_aggregate.Callbacks.BearingParamsFiller import BearingParamsFiller
from Source.Source_aggregate.Callbacks.SourceAggregatorCallback import SourceAggregatorCallback


class BearingParamsFillerCallback(BearingParamsFiller, SourceAggregatorCallback):
    def on_before_row_save(self, row: dict[str, Any]) -> dict[str, Any]:
        id_bearing = row['id_bearing']
        params = deepcopy(row['object_params'])
        id_bearing, params = self.full(id_bearing, params)
        row['id_bearing'] = id_bearing
        row['object_params'] = params
        return row