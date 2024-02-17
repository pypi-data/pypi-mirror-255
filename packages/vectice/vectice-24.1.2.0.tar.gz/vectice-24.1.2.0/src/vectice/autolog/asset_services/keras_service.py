from __future__ import annotations

from typing import TYPE_CHECKING

from vectice.autolog.asset_services.metric_service import MetricService
from vectice.autolog.model_library import ModelLibrary

if TYPE_CHECKING:
    from keras.models import Model as KerasModel


class AutologKerasService(MetricService):
    def __init__(self, key: str, asset: KerasModel, data: dict):
        self._asset = asset
        self._key = key
        super().__init__(cell_data=data)

    def get_asset(self):
        model_metrics = self._get_model_metrics(self._cell_data)
        training_metrics = self._get_keras_training_metrics(self._asset)
        return {
            "variable": self._key,
            "model": self._asset,
            "library": ModelLibrary.KERAS,
            "metrics": {**model_metrics, **training_metrics},
        }
