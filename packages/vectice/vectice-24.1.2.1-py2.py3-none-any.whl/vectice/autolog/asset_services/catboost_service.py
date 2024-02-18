from __future__ import annotations

from typing import TYPE_CHECKING

from vectice.autolog.asset_services.metric_service import MetricService
from vectice.autolog.model_library import ModelLibrary

if TYPE_CHECKING:
    from catboost.core import CatBoost


class AutologCatboostService(MetricService):
    def __init__(self, key: str, asset: CatBoost, data: dict):
        self._asset = asset
        self._key = key

        super().__init__(cell_data=data)

    def get_asset(self):
        return {
            "variable": self._key,
            "model": self._asset,
            "library": ModelLibrary.CATBOOST,
            "metrics": self._get_model_metrics(self._cell_data),
        }
