from __future__ import annotations

from io import BufferedReader, IOBase
from typing import TYPE_CHECKING

from PIL.Image import Image

from vectice.api.http_error_handlers import VecticeException
from vectice.api.json.iteration import IterationStepArtifactInput, IterationStepArtifactType
from vectice.utils.common_utils import (
    check_string_sanity,
    get_image_or_file_variables,
    set_dataset_attachments,
    set_model_attachments,
)

if TYPE_CHECKING:
    from vectice.api.client import Client
    from vectice.models.dataset import Dataset
    from vectice.models.iteration import Iteration
    from vectice.models.model import Model


class IterationService:
    def __init__(self, iteration: Iteration, client: Client):
        self._client = client
        self._iteration = iteration

    def log_image_or_file(self, asset: str | IOBase | Image, section: str | None = None):
        _, filename = self._create_image_or_file_artifact(asset, section)
        return filename

    def log_comment(self, asset: int | float | str, section: str | None = None):
        if isinstance(asset, str):
            check_string_sanity(asset)
        artifact_inp: list[IterationStepArtifactInput] = [IterationStepArtifactInput(type="Comment", text=str(asset))]
        self._client.add_iteration_artifacts(iteration_id=self._iteration.id, artifacts=artifact_inp, section=section)

    def log_model(self, asset: Model, section: str | None = None):
        code_version_id = self._get_code_version_id()
        model_data = self._client.register_model(
            model=asset,
            phase=self._iteration.phase,
            iteration=self._iteration,
            code_version_id=code_version_id,
            section=section,
        )
        attachments_output, success_pickle = set_model_attachments(self._client, asset, model_data.model_version)
        return model_data, attachments_output, success_pickle

    def log_dataset(self, asset: Dataset, section: str | None = None):
        code_version_id = self._get_code_version_id()
        dataset_output = self._client.register_dataset_from_source(
            dataset=asset,
            iteration_id=self._iteration.id,
            code_version_id=code_version_id,
            section=section,
        )
        attachments_output = set_dataset_attachments(self._client, asset, dataset_output.dataset_version)
        return dataset_output, attachments_output

    def _create_image_or_file_artifact(
        self, value: str | IOBase | Image, section: str | None = None
    ) -> tuple[IterationStepArtifactInput, str]:
        is_image_or_file, filename = get_image_or_file_variables(value)
        try:
            artifact, *_ = self._client.create_iteration_attachments(
                files=[("file", (filename, is_image_or_file))], iteration_id=self._iteration.id, step_name=section
            )
            if isinstance(is_image_or_file, BufferedReader):
                is_image_or_file.close()
            return (
                IterationStepArtifactInput(id=artifact.fileId, type=IterationStepArtifactType.EntityFile.name),
                filename,
            )
        except VecticeException as error:
            raise error
        except Exception as error:
            raise ValueError("Check the provided image.") from error

    def _get_code_version_id(self):
        # TODO: cyclic imports
        from vectice import code_capture
        from vectice.models.git_version import check_code_source, inform_if_git_repo

        if code_capture:
            return check_code_source(self._client, self._iteration.phase.project.id)
        else:
            inform_if_git_repo()
            return None
