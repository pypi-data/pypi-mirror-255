from __future__ import annotations

from abc import abstractmethod
from importlib.util import find_spec
from typing import Any, Protocol

from vectice.api.http_error_handlers import VecticeException
from vectice.autolog.asset_services import (
    AutologCatboostService,
    AutologKerasService,
    AutologLightgbmService,
    AutologPandasService,
    AutologPysparkService,
    AutologSklearnService,
)


class IAutologService(Protocol):
    @abstractmethod
    def get_asset(self) -> dict[str, Any] | None:
        ...


class AssetFactory:
    @staticmethod
    def get_asset_service(key: str, asset: Any, data: dict) -> IAutologService:
        is_pandas = find_spec("pandas") is not None
        is_pyspark = find_spec("pyspark") is not None
        is_lgbm = find_spec("lightgbm") is not None
        is_sklearn = find_spec("sklearn") is not None
        is_catboost = find_spec("catboost") is not None
        is_keras = find_spec("keras") is not None

        if is_pandas:
            from pandas import DataFrame

            if isinstance(asset, DataFrame):
                return AutologPandasService(key, asset)

        if is_pyspark:
            from pyspark.sql import DataFrame as SparkDF

            if isinstance(asset, SparkDF):
                return AutologPysparkService(key, asset)

        if is_lgbm:
            from lightgbm.basic import Booster

            if isinstance(asset, Booster):
                return AutologLightgbmService(key, asset, data)

        if is_catboost:
            from catboost.core import CatBoost

            if isinstance(asset, CatBoost):
                return AutologCatboostService(key, asset, data)

        if is_keras:
            from keras.models import Model as KerasModel

            if isinstance(asset, KerasModel):
                return AutologKerasService(key, asset, data)

        if is_sklearn:
            return AutologSklearnService(key, asset, data)

        raise VecticeException(f"Asset {asset} of type ({type(asset)!r}) not handled")
