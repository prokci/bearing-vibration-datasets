from abc import ABC
from typing import Any


class SourceAggregatorCallback(ABC):
    def on_before_row_save(self, params: dict[str, Any]):
        return params
    
    def filter_row(self, params: dict[str, Any]):
        return True