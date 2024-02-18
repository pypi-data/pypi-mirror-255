from __future__ import annotations

import ast
import logging
import re
import tempfile
from ast import literal_eval
from collections import OrderedDict
from importlib.util import find_spec
from typing import TYPE_CHECKING, Any, TypeVar

from typing_extensions import TypedDict

from vectice.api.http_error_handlers import VecticeException
from vectice.autolog.autolog_asset_factory import AssetFactory
from vectice.autolog.model_library import ModelLibrary
from vectice.utils.code_parser import VariableVisitor

if TYPE_CHECKING:
    from tempfile import TemporaryDirectory

    from catboost.core import CatBoost
    from keras import Model as KerasModel
    from lightgbm.basic import Booster
    from pandas import DataFrame
    from pyspark.sql import DataFrame as SparkDF
    from sklearn.base import BaseEstimator

    from vectice.models import Phase
    from vectice.models.resource.metadata.db_metadata import TableType

    ModelTypes = TypeVar("ModelTypes", BaseEstimator, Booster, CatBoost, KerasModel)
    TModel = TypedDict("TModel", {"variable": str, "model": ModelTypes, "library": ModelLibrary, "metrics": dict})
    DataframeTypes = TypeVar("DataframeTypes", SparkDF, DataFrame)
    TDataset = TypedDict("TDataset", {"variable": str, "dataframe": DataframeTypes, "type": TableType})


try:
    from IPython.core.getipython import get_ipython
    from IPython.core.interactiveshell import InteractiveShell
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "To use autolog, please install extra dependencies from vectice package using '%pip install vectice[autolog]'"
    ) from None

is_plotly = False
is_matplotlib = False
if find_spec("plotly") is not None:
    is_plotly = True

if find_spec("matplotlib") is not None:
    is_matplotlib = True

_logger = logging.getLogger(__name__)

NOTEBOOK_CELLS = {}


def start_listen():
    ipython = get_ipython()  # type: ignore

    def _notebook_cell_content_update():
        # Collab
        # cell_id = IP.get_parent()["metadata"]["colab"]["cell_id"]

        # Databricks
        # cell_id = IP.get_parent()["metadata"]["commandId"]
        cell_metadata = ipython.get_parent()["metadata"]  # type: ignore
        if cell_metadata.get("colab") and "cell_id" in cell_metadata.get("colab"):  # type: ignore
            cell_id = cell_metadata["colab"]["cell_id"]
        elif cell_metadata.get("commandId"):  # type: ignore
            cell_id = cell_metadata["commandId"]
        else:
            cell_id = cell_metadata["cellId"]
        cell_content = ipython.get_parent()["content"]["code"]  # type: ignore
        NOTEBOOK_CELLS[cell_id] = cell_content

    def _load_ipython_extension():
        """Load the extension in IPython."""
        ipython.events.register("post_execute", _notebook_cell_content_update)  # type: ignore

    if ipython and not any([ev for ev in ipython.events.callbacks["post_execute"] if "_notebook_cell_content_update" in str(ev)]):  # type: ignore
        _load_ipython_extension()


####### Autolog logic
class Autolog:
    def __init__(
        self,
        phase: Phase | None,
        ipy: InteractiveShell,
        is_notebook: bool,
        create: bool = True,
        note: str | None = None,
    ):
        from vectice.services.phase_service import PhaseService

        if phase is None:
            raise ValueError("Login")

        if create is True:
            iteration = phase.create_iteration()
        else:
            iteration = PhaseService(
                phase._client  # pyright: ignore[reportPrivateUsage]
            ).get_active_iteration_or_create(phase)

        self._iteration = iteration
        self._iteration_service = iteration._service  # pyright: ignore[reportPrivateUsage]
        self._ip = ipy
        self._local_vars = self._ip.user_global_ns
        self._cell_content = self._get_notebook_cell_content() if is_notebook is True else self._get_cell_content()
        self._vectice_data = self._get_variable_matches(self._local_vars)
        self._failed_assets = []

        # Get back objects to log
        self._assets = self._get_assets()
        graphs = self._get_graphs()

        if note:
            self._iteration_service.log_comment(note)
            _logger.info(f"Note logged in iteration {self._iteration.index!r}.")

        # Log objects
        self._log_assets(self._assets)

        if graphs:
            for graph in graphs:
                try:
                    self._iteration_service.log_image_or_file(graph)
                    _logger.info(f"Graph {graph!r} logged in iteration {self._iteration.index!r}.")
                except Exception as e:
                    self._failed_assets.append({"reason": e, "asset": graph, "type": "Graph"})

        if len(self._failed_assets):
            _logger.warning("The following assets failed to log:")
        for failed_asset in self._failed_assets:
            _logger.warning(f"{failed_asset['type']} {failed_asset['asset']!r}, reason: {failed_asset['reason']}")

    def _get_variable_matches(self, local_vars: dict[str, Any]) -> list[dict[Any, Any]]:
        vectice_data = []

        for cell in self._cell_content:
            vectice_match = {}
            all_vars: OrderedDict[str, Any] = OrderedDict()

            vectice_match["cell"] = cell

            # Parse the cell content using the VariableVisitor
            tree = ast.parse(cell)
            visitor = VariableVisitor()
            visitor.visit(tree)

            # Update all_vars with variable names and values in the order they appear
            for var in visitor.variables:
                if var in local_vars and var not in all_vars:
                    all_vars[var] = local_vars[var]

            vectice_match["variables"] = all_vars
            vectice_data.append(vectice_match)
        return vectice_data

    def _get_notebook_cell_content(self) -> list[Any]:
        return list(NOTEBOOK_CELLS.values())

    def _get_cell_content(self) -> list[Any]:
        """Used by autolog cell to get the content of the cell. This is used to parse for variables."""
        cell_content = self._ip.get_parent()["content"]["code"]  # pyright: ignore[reportAttributeAccessIssue]
        if cell_content is None:
            raise ValueError("Failed to get cell content.")
        return [cell_content]

    def _get_assets(self) -> list[TModel | TDataset]:
        assets = []
        for data in self._vectice_data:
            for key in data["variables"].keys():
                # skip cell inputs/outputs
                if key.startswith("_"):
                    continue
                asset = data["variables"][key]
                try:
                    asset_information = AssetFactory.get_asset_service(key, asset, data).get_asset()
                    if asset_information is not None:
                        assets.append(asset_information)
                except VecticeException:
                    pass
        return self._deduplicate_assets(assets)

    def _deduplicate_assets(self, assets: list[dict[str, Any]]) -> list[TModel | TDataset]:
        unique_dict = {}
        result = []

        for item in assets:
            variable = item["variable"]

            if variable not in unique_dict.keys():
                # If variable is not seen before, add it to the dictionary
                unique_dict[variable] = item
                result.append(item)
            elif "dataframe" in item:
                existing_item = unique_dict[variable]
                existing_item["type"] = item["type"]

            else:
                existing_item = unique_dict[variable]
                existing_item["library"] = item["library"]

                # Merge dictionaries for the "metrics" attribute
                existing_item_metrics = existing_item["metrics"]
                item_metrics = item["metrics"]

                for key, value in item_metrics.items():
                    existing_item_metrics[key] = value

        return result

    def _get_lightgbm_info(self, model: Booster) -> tuple[str, dict[str, Any]] | tuple[None, None]:
        try:
            params = {
                key: value
                for key, value in model._get_loaded_param().items()  # pyright: ignore[reportPrivateUsage]
                if value is not None
            }
            return "lightgbm", params
        except AttributeError:
            return None, None

    def _get_model_library(self, model: ModelTypes):
        if "xgboost" in str(model.__class__):
            return "xgboost"
        if "lightgbm" in str(model.__class__):
            return "lightgbm"
        return "sklearn"

    def _get_sklearn_or_xgboost_or_lgbm_info(
        self, model: BaseEstimator
    ) -> tuple[str, dict[str, Any]] | tuple[None, None]:
        try:
            library = self._get_model_library(model)
            params = {str(key): value for key, value in model.get_params().items() if value is not None}
            return library, params
        except AttributeError:
            return None, None

    def _format_keras_params(self, model: KerasModel) -> dict[str, Any]:
        params: dict[str, Any] = {}

        for i, layer in enumerate(model.layers):
            params[f"Layer-{i}"] = {
                "name": layer.name,
                "param": layer.count_params(),
                "output shape": layer.output_shape,
            }
        params["Total # of weights"] = model.count_params()

        return params

    def _get_keras_info(self, model: KerasModel) -> tuple[str, dict[str, Any]] | tuple[None, None]:
        try:
            return "keras", self._format_keras_params(model)
        except Exception:
            return None, None

    def _log_assets(
        self,
        assets: list[TModel | TDataset],
    ):
        for asset in assets:
            try:
                if "model" in asset:
                    self._log_model(asset)
                else:
                    self._log_dataset(asset)
            except Exception as e:
                self._failed_assets.append(
                    {"reason": e, "asset": asset["variable"], "type": "Model" if "model" in asset else "Dataset"}
                )

    def _get_catboost_info(self, model: CatBoost) -> tuple[str, dict[str, Any]] | tuple[None, None]:
        try:
            params = {str(key): value for key, value in model.get_all_params().items() if value is not None}
            return "catboost", params
        except AttributeError:
            return None, None

    def _get_model_params(self, model: TModel) -> tuple[str, dict[str, Any]] | tuple[None, None]:
        if model["library"] is ModelLibrary.SKLEARN:
            return self._get_sklearn_or_xgboost_or_lgbm_info(model["model"])  # pyright: ignore[reportArgumentType]
        if model["library"] is ModelLibrary.LIGHTGBM:
            return self._get_lightgbm_info(model["model"])  # pyright: ignore[reportArgumentType]
        if model["library"] is ModelLibrary.CATBOOST:
            return self._get_catboost_info(model["model"])  # pyright: ignore[reportArgumentType]
        if model["library"] is ModelLibrary.KERAS:
            return self._get_keras_info(model["model"])  # pyright: ignore[reportArgumentType]
        return None, None

    def _check_for_single_model(self):
        model_list = [asset for asset in self._assets if "model" in asset]
        if len(model_list) > 1:
            return False
        return True

    def _get_single_model_metrics(self) -> dict:
        from vectice.autolog.asset_services.metric_service import MetricService

        # get a single models metrics for notebook function
        metrics = {}
        if not self._check_for_single_model():
            return {}
        for data in self._vectice_data:
            cell_metrics = MetricService(data["cell"])._get_model_metrics(data)  # type: ignore[reportPrivateUsage]
            if cell_metrics:
                metrics.update(cell_metrics)
        return metrics

    def _log_model(self, model: TModel):
        from vectice import Model

        temp_dir: TemporaryDirectory | None = None
        temp_file_path: str | None = None
        if model["library"] is ModelLibrary.KERAS:
            graph = None

            try:
                from keras.utils import plot_model

                temp_dir = tempfile.TemporaryDirectory()
                file_name = f"{model['variable']!s}_plot.png"
                temp_file_path = rf"{temp_dir.name}\{file_name}"
                graph = plot_model(model["model"], to_file=temp_file_path, show_shapes=True, show_layer_names=False)

                if graph is None:
                    temp_file_path = None
                    _logger.info(
                        "Unable to generate the model plot. Please check the 'plot_model' function from the Keras library is working correctly. Make sure that the graphviz and pydot packages are installed and configured properly."
                    )

            except Exception as e:
                _logger.info(
                    f"Unable to generate the model plot. Ensure that the Keras library is correctly installed and up-to-date. Error details: {e}"
                )

        library, params = self._get_model_params(model)

        algorithm = str(model["model"].__class__).split(".")[-1]
        algorithm = algorithm.replace("'>", "")
        model_name = f"{self._iteration.phase.id}-{model['variable']}"
        # safety check, if no metrics and single model, get metrics
        model_metrics = model["metrics"] if model["metrics"] else self._get_single_model_metrics()
        self._iteration_service.log_model(
            Model(
                library=library,
                technique=algorithm,
                metrics=model_metrics,
                properties=params,
                name=model_name,
                predictor=model["model"],
                attachments=temp_file_path,
            )
        )
        _logger.info(f"Model {model_name!r} logged in iteration {self._iteration.index!r}.")

        if temp_dir is not None:
            temp_dir.cleanup()

    def _log_dataset(self, dataset: TDataset) -> None:
        from vectice import Dataset, DatasetType, FileResource, NoResource

        resource = self._get_dataset_resource(dataset)
        dataset_name = f"{self._iteration.phase.id}-{dataset['variable']}"
        no_resource_dataset = Dataset(
            type=DatasetType.UNKNOWN,
            resource=NoResource(
                dataframes=dataset["dataframe"],
                origin="DATAFRAME",
                type=dataset["type"],
            ),
            name=dataset_name,
        )
        if resource:
            # TODO Dataset type ?
            vec_dataset = Dataset(
                type=DatasetType.UNKNOWN,
                resource=FileResource(
                    paths=resource,
                    dataframes=dataset["dataframe"],
                ),
                name=dataset_name,
            )
        else:
            vec_dataset = no_resource_dataset
        try:
            self._iteration_service.log_dataset(vec_dataset)
        except FileNotFoundError:
            self._iteration_service.log_dataset(no_resource_dataset)
        _logger.info(f"Dataset {dataset_name!r} logged in iteration {self._iteration.index!r}.")

    def _get_dataset_resource(self, dataset: TDataset) -> str | None:
        import re

        if not self._cell_content:
            return None
        try:
            # Avoid getting stray dataset with autolog.notebook()
            match = []
            for cell in self._cell_content:
                match += re.findall(rf"(?<={dataset['variable']} = pd.read_csv\().*[^,)\n]", cell)
            if len(match) < 1:
                return None
            # TODO update regex
            # check if read csv has comma dominated arguments
            return literal_eval(match[0].split(",")[0]) if match[0].find(",") else literal_eval(match[0])
        except TypeError:
            return None

    def _get_graphs(self) -> list[str]:
        graphs = []
        for cell in self._cell_content:
            # seaborn and matplotlib support
            graphs += re.findall(r"(?<=plt\.savefig\()[^)\n]*[^\)\n]", cell)
            # plotly support
            graphs += re.findall(r"(?<=\.write_image\()[^)\n]*[^\)\n]", cell)
        return [literal_eval(graph) for graph in graphs]
