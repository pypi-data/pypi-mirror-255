from __future__ import annotations

import re
from functools import reduce
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from keras.models import Model as KerasModel


class MetricService:
    def __init__(self, cell_data: dict):
        self._cell_data = cell_data
        self._model_cell = None

    def _get_model_metrics(self, data: dict) -> dict[str, Any]:
        # TODO mix of models ?
        cell_content = data["cell"]
        variables = data["variables"]

        if not cell_content:
            return {}
        # Get model cell content for metrics
        self._model_cell = cell_content
        metrics = self._get_regression_metrics() or self._get_classification_metrics()
        # Temporary fix for additional metrics used with regression or classification
        other_metrics = self._get_other_metrics()
        metrics += other_metrics
        return reduce(
            lambda identified_metrics, key: (
                {**identified_metrics, key: variables[key]}
                if key in metrics and isinstance(variables[key], (int, float))
                else identified_metrics
            ),
            variables.keys(),
            {},
        )

    def _get_regression_metrics(self):
        from sklearn.metrics import _regression  # pyright: ignore[reportPrivateUsage]

        return reduce(self._get_metric, dir(_regression), [])

    def _get_classification_metrics(self):
        from sklearn.metrics import _classification  # pyright: ignore[reportPrivateUsage]

        return reduce(self._get_metric, dir(_classification), [])

    def _get_other_metrics(self):
        from sklearn.metrics import (
            _ranking,  # pyright: ignore[reportPrivateUsage]
            _scorer,  # pyright: ignore[reportPrivateUsage]
            cluster,  # pyright: ignore[reportPrivateUsage]
        )

        all_metrics = dir(_ranking) + dir(_scorer) + dir(cluster)
        return reduce(self._get_metric, all_metrics, [])

    def _get_metric(self, metrics: list[Any], func: str):
        # TODO regex working but should be tested more
        metric = re.findall(rf"(.*?) = {func}", self._model_cell) if self._model_cell else []
        return [*metrics, *metric] if metric else metrics

    def _get_keras_training_metrics(self, model: KerasModel) -> dict[str, float]:
        try:
            return {
                str(key)
                + "_train": float(model.get_metrics_result()[key].numpy())  # pyright: ignore[reportGeneralTypeIssues]
                for key in model.get_metrics_result().keys()  # pyright: ignore[reportGeneralTypeIssues]
            }
        except Exception:
            return {}
