from __future__ import annotations

from typing import Any

from vectice.autolog.asset_services.metric_service import MetricService
from vectice.autolog.model_library import ModelLibrary


class AutologSklearnService(MetricService):
    def __init__(self, key: str, asset: Any, data: dict):
        self._asset = asset
        self._key = key

        super().__init__(cell_data=data)

    def get_asset(self):
        # xgboost relies on BaseEstimator
        # lightgbm has Booster and sklearn API which uses BaseEstimator
        try:
            from sklearn.base import is_classifier, is_regressor

            if is_regressor(self._asset) or is_classifier(self._asset):
                try:
                    # TODO fix regex picking up classes
                    # Ignore Initialized variables e.g LogisticRegression Class
                    self._asset.get_params()  # pyright: ignore[reportGeneralTypeIssues]
                    return {
                        "variable": self._key,
                        "model": self._asset,
                        "library": ModelLibrary.SKLEARN,
                        "metrics": self._get_model_metrics(self._cell_data),
                    }
                except Exception:
                    pass
        except ImportError:
            pass
