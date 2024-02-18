from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, BinaryIO, NoReturn

from vectice.api.http_error_handlers import InvalidReferenceError, VecticeException
from vectice.api.json import AttachmentOutput, ModelVersionOutput, PagedResponse
from vectice.api.json.dataset_version import DatasetVersionOutput
from vectice.api.json.json_to_class import json_to_class
from vectice.api.rest_api import HttpError, RestApi
from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation
from vectice.models.representation.model_version_representation import ModelVersionRepresentation

if TYPE_CHECKING:
    from io import BytesIO

    from requests import Response


MODEL_VERSION = "model version"
DATASET_VERSION = "dataset version"


_logger = logging.getLogger(__name__)


class AttachmentApi(RestApi):
    def _generate_model_url_and_id(self, model_version: ModelVersionOutput) -> tuple[str, str | None]:
        try:
            model_name = model_version.model.name
            version_name = model_version.name
            url = self._build_url(version=model_version.id, file_type="modelversion")
            model_repr = f"Model(name='{model_name}', version='{version_name}')"
            return url, model_repr
        except HttpError as e:
            self._handle_http_error(e, model_version)

    def _generate_dataset_url_and_id(self, dataset_version: DatasetVersionOutput) -> tuple[str, str | None]:
        try:
            dataset_name = dataset_version.dataset.name
            version_name = dataset_version.name
            url = self._build_url(version=dataset_version.id, file_type="datasetversion")
            dataset_repr = f"Dataset(name='{dataset_name}', version='{version_name}')"
            return url, dataset_repr
        except HttpError as e:
            self._handle_http_error(e, dataset_version)

    def _generate_version_url_and_id(
        self, version: ModelVersionOutput | DatasetVersionOutput
    ) -> tuple[str, str | None]:
        if isinstance(version, ModelVersionOutput):
            return self._generate_model_url_and_id(version)

        return self._generate_dataset_url_and_id(version)

    @staticmethod
    def _build_url(version: str, file_type: str) -> str:
        return f"/api/entityfiles/{file_type}/{version}"

    def post_attachment(
        self, files: list[tuple[str, tuple[str, BinaryIO]]], version: ModelVersionOutput | DatasetVersionOutput
    ) -> list[AttachmentOutput]:
        entity_files = []
        url, asset_repr = self._generate_version_url_and_id(version)
        if len(files) == 1:
            filename = files[0][1][0]
            try:
                response = self._post_attachments(url, files)
                if response:
                    entity_files.append(response.json())
                _logger.debug(f"Attachment with name: {filename} successfully attached to {asset_repr}.")
            except HttpError as e:
                self._handle_http_error(e, version, filename)
        elif len(files) > 1:
            for file in files:
                try:
                    response = self._post_attachments(url, [file])
                    if response:
                        entity_files.append(response.json())
                except HttpError as e:
                    self._handle_http_error(e, version, file[1][0])

                filenames = ", ".join([f[1][0] for f in files])
                _logger.debug(f"Attachments with names: {filenames} successfully attached to {asset_repr}.")
        return json_to_class(entity_files, AttachmentOutput)

    def post_model_predictor(self, model_type: str, model_content: BytesIO, model_version: ModelVersionOutput) -> None:
        url, model_repr = self._generate_model_url_and_id(model_version)
        url += f"?modelFramework={model_type}"
        attachment = ("file", ("model_pickle", model_content))
        self._post_attachments(url, [attachment])
        _logger.debug(f"Model {model_type} successfully attached to {model_repr}.")

    def _identify_object(
        self, code_version_id: int | None = None, iteration_id: str | None = None
    ) -> tuple[str, str | int]:
        if iteration_id:
            return "iteration", iteration_id
        elif code_version_id:
            return "codeversion", code_version_id
        else:
            raise ValueError("No ID was provided for create attachment.")

    def create_attachments(
        self,
        files: list[tuple[str, tuple[str, Any]]],
        code_version_id: int | None = None,
        iteration_id: str | None = None,
        step_name: str | None = None,
    ) -> list[AttachmentOutput]:
        parent_object, object_id = self._identify_object(code_version_id, iteration_id)
        entity_files = []
        query_param = f"?stepName={step_name}" if step_name else ""
        url = f"/api/entityfiles/{parent_object}/{object_id}{query_param}"
        try:
            for file in files:
                response = self._post_attachments(url, [file])
                if response:
                    entity_files.append(response.json())
            _logger.debug(
                f"Attachments with names: {[f[1][0] for f in files]} successfully attached to {parent_object} {object_id}."
            )
            return json_to_class(entity_files, AttachmentOutput)
        except HttpError as e:
            self._httpErrorHandler.handle_get_http_error(e, parent_object, object_id)

    def get_code_version_attachment(self, code_version_id: int, file_id: int) -> Response:
        try:
            return self._get_attachment(f"/api/entityfiles/codeversion/{code_version_id}/{file_id}")
        except HttpError as e:
            self._handle_code_version_error(e, code_version_id)

    def list_attachments(self, version: ModelVersionOutput | DatasetVersionOutput) -> PagedResponse[AttachmentOutput]:
        try:
            url, _ = self._generate_version_url_and_id(version)
            if url is None:  # pyright: ignore[reportUnnecessaryComparison]
                raise InvalidReferenceError(MODEL_VERSION, version.id)
            attachments = self._list_attachments(url)
        except HttpError as e:
            self._handle_http_error(e, version)
        return PagedResponse(
            item_cls=AttachmentOutput,
            total=len(attachments),
            page={},
            items=attachments,
        )

    def list_version_representation_attachments(
        self, version: ModelVersionRepresentation | DatasetVersionRepresentation
    ) -> PagedResponse[AttachmentOutput]:
        try:
            url_type = "modelversion" if isinstance(version, ModelVersionRepresentation) else "datasetversion"
            url = self._build_url(version=version.id, file_type=url_type)
            attachments = self._list_attachments(url)
        except HttpError as e:
            self._handle_http_error(e, version)

        return PagedResponse(
            item_cls=AttachmentOutput,
            total=len(attachments),
            page={},
            items=attachments,
        )

    def _handle_http_error(
        self,
        error: HttpError,
        version: ModelVersionOutput | DatasetVersionOutput | ModelVersionRepresentation | DatasetVersionRepresentation,
        file: str | None = None,
    ) -> NoReturn:
        ref_type = (
            MODEL_VERSION
            if isinstance(version, ModelVersionOutput) or isinstance(version, ModelVersionRepresentation)
            else DATASET_VERSION
        )
        if error.code == 413 and file is not None:
            raise VecticeException(f"{ref_type}: {file} exceeds the maximum size of 100MB.")
        self._httpErrorHandler.handle_get_http_error(error, ref_type, version.id)

    def _handle_code_version_error(self, error: HttpError, code_version_id: int) -> NoReturn:
        self._httpErrorHandler.handle_get_http_error(error, "code version", code_version_id)
