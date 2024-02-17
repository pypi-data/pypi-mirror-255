from __future__ import annotations

import logging
import mimetypes
import os
import pickle  # nosec
import re
from contextlib import contextmanager
from io import BufferedReader, BytesIO, IOBase
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Union

from gql.transport.exceptions import TransportQueryError
from PIL import Image, ImageFile
from rich.console import Console
from rich.table import Table

from vectice.api.http_error_handlers import VecticeException
from vectice.api.json.iteration import IterationStatus
from vectice.api.json.step import StepOutput, StepType
from vectice.models.attachment_container import AttachmentContainer

if TYPE_CHECKING:
    from vectice.api.client import Client
    from vectice.api.json import AttachmentOutput
    from vectice.api.json.dataset_version import DatasetVersionOutput
    from vectice.api.json.model_version import ModelVersionOutput
    from vectice.models.dataset import Dataset
    from vectice.models.iteration import Iteration
    from vectice.models.model import Model
    from vectice.models.step import Step


@contextmanager
def hide_logs(package: str):
    old_level = logging.getLogger(package).level
    try:
        logging.getLogger(package).setLevel(logging.ERROR)
        yield
    finally:
        logging.getLogger(package).setLevel(old_level)


def check_read_only(iteration: Iteration):
    """Check if an iteration is completed or cancelled.

    Refreshing the iteration is necessary because in a Jupyter notebook
    its status could have changed on the backend.

    Parameters:
        iteration: The iteration to check.

    Raises:
        RuntimeError: When the iteration is read-only (completed or cancelled).
    """
    refresh_iteration = iteration._phase.iteration(iteration.index)  # pyright: ignore[reportPrivateUsage]
    if refresh_iteration._status in {  # pyright: ignore[reportPrivateUsage]
        IterationStatus.Completed,
        IterationStatus.Abandoned,
    }:
        raise RuntimeError(f"The Iteration is {refresh_iteration.status} and is read-only.")


def get_step_type(
    step_output: StepOutput,
    iteration: Iteration,
) -> Step:
    # TODO: cyclic imports
    from vectice.models.step import Step
    from vectice.models.step_dataset import StepDataset
    from vectice.models.step_image import StepImage
    from vectice.models.step_model import StepModel
    from vectice.models.step_number import StepNumber
    from vectice.models.step_string import StepString

    artifacts = step_output.artifacts
    step = Step(
        id=step_output.id,
        iteration=iteration,
        name=step_output.name,
        index=step_output.index,
        slug=step_output.slug,
        description=step_output.description,
        artifacts=artifacts,
        step_type=StepType.Step,
    )

    def _get_number(text: int | float | str):
        try:
            return float(text)
        except ValueError:
            return text

    if (
        artifacts is not None  # pyright: ignore[reportUnnecessaryIsInstance, reportUnnecessaryComparison]
        and len(artifacts) >= 1  # pyright: ignore[reportUnnecessaryIsInstance, reportUnnecessaryComparison]
    ):
        artifact = artifacts[len(artifacts) - 1]
        if artifact.dataset_version_id is not None:
            return StepDataset(step, artifact)
        if artifact.model_version_id is not None:
            return StepModel(step, artifact)
        if artifact.entity_file_id:
            image = _get_image_info(iteration, artifact.entity_file_id)
            return step if image is None else StepImage(step, image)
        if artifact.text:
            str_or_float = _get_number(artifact.text)
            return (
                StepNumber(step, str_or_float)
                if isinstance(str_or_float, float)
                else StepString(step, str(str_or_float))
            )
    return step


def _get_image_info(iteration: Iteration, entity_file_id: int):
    try:
        image = iteration._client.get_entity_file_by_id(entity_file_id)  # pyright: ignore[reportPrivateUsage]
        return image.file_name
    except TransportQueryError:
        return None


def check_image_path(path: str) -> bool:
    if _check_for_comment(path):
        return False
    try:
        check_path = Path(path).exists()
    except OSError:
        return False
    _, ext = os.path.splitext(path)
    pillow_extensions = {exten for exten in Image.registered_extensions()}
    if not check_path and ext in pillow_extensions:
        raise ValueError("Check the file path.")
    if ext not in pillow_extensions:
        return False
    return True


def check_file_path(path: str) -> bool:
    if _check_for_comment(path):
        return False
    try:
        check_image_path(path)
    except ValueError:
        raise ValueError("Check the file path.") from None
    _, ext = os.path.splitext(path)
    mime_type = mimetypes.guess_type(path)[0]
    if not mime_type and ext not in [".parquet", ".ipynb"]:
        return False
    return True


def _check_for_comment(path: str) -> bool:
    _, ext = os.path.splitext(path)
    if ext:
        return False
    return True


def _validate_image_or_file(path: str) -> BufferedReader:
    try:
        return open(path, "rb")
    except FileNotFoundError:
        raise ValueError(f"The provided file {path!r} cannot be opened. Check its format and permissions.") from None


def get_image_or_file_variables(value: str | IOBase | Image.Image) -> tuple[BufferedReader | IOBase | BytesIO, str]:
    if isinstance(value, IOBase):
        image = value
        filename = os.path.basename(value.name)  # type: ignore[attr-defined]
        return image, filename
    if isinstance(value, str):
        image = _validate_image_or_file(value)
        filename = os.path.basename(image.name)
        return image, filename
    if isinstance(value, Image.Image):  # pyright: ignore[reportUnnecessaryIsInstance]
        previous_load_truncated_images = ImageFile.LOAD_TRUNCATED_IMAGES
        previous_max_image_pixels = Image.MAX_IMAGE_PIXELS
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        Image.MAX_IMAGE_PIXELS = None
        in_mem_file = BytesIO()
        value.save(in_mem_file, format=value.format)
        in_mem_file.seek(0)
        filename = os.path.basename(value.filename)  # type: ignore #TODO I doubt filename really exists in PIL: https://stackoverflow.com/questions/45087638/get-image-filename-from-image-pil
        ImageFile.LOAD_TRUNCATED_IMAGES = previous_load_truncated_images
        Image.MAX_IMAGE_PIXELS = previous_max_image_pixels
        return in_mem_file, filename

    raise ValueError("Unsupported image provided.")


def temp_print(string: str | None = None, table: Table | None = None) -> None:
    console = Console(width=120)
    if string:
        print(string)
        print()
    if table:
        console.print(table)
        print()


def convert_keys_to_camel_case(input_dict: Dict[str, Any]) -> Dict[str, Union[Any, Dict[str, Any]]]:
    camel_case_dict: Dict[str, Union[Any, Dict[str, Any]]] = {}

    for key, value in input_dict.items():
        camel_case_key = re.sub(r"_([a-z])", lambda match: match.group(1).upper(), key)
        if isinstance(value, dict):
            value = convert_keys_to_camel_case(value)
        camel_case_dict[camel_case_key] = value

    return camel_case_dict


def format_attachments(attachments: str | list[str]) -> list[str]:
    list_attachments = (
        [attachment for attachment in set(attachments)] if isinstance(attachments, list) else [attachments]
    )
    for attachment in list_attachments:
        if not isinstance(attachment, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise ValueError(
                f"Argument 'attachments' with type '{type(attachment)}' is invalid, only str are supported."
            )
    return list_attachments


def check_string_sanity(value: str):
    if value == "":
        raise VecticeException("Cannot assign an empty comment. Please provide a valid comment")


def ensure_correct_project_id_from_representation_objs(project_id: str, value: Any):
    from vectice.models.representation.dataset_representation import DatasetRepresentation
    from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation
    from vectice.models.representation.model_representation import ModelRepresentation
    from vectice.models.representation.model_version_representation import ModelVersionRepresentation

    if (
        isinstance(value, DatasetRepresentation)
        or isinstance(value, DatasetVersionRepresentation)
        or isinstance(value, ModelRepresentation)
        or isinstance(value, ModelVersionRepresentation)
    ) and value.project_id != project_id:
        raise VecticeException("Assigning an asset coming from another project is forbidden")


def set_model_attachments(
    client: Client, model: Model, model_version: ModelVersionOutput
) -> tuple[list[AttachmentOutput] | None, bool]:
    logging.getLogger("vectice.models.attachment_container").propagate = True
    attachments = None
    if model.attachments:
        container = AttachmentContainer(model_version, client)
        attachments = container.add_attachments(model.attachments)

    success_pickle: bool = False
    if model.predictor is not None:
        try:
            model_content = _serialize_model(model.predictor)
            model_type_name = type(model.predictor).__name__
            container = AttachmentContainer(model_version, client)
            container.add_serialized_model(model_type_name, model_content)
            success_pickle = True
        except Exception:
            success_pickle = False

    return attachments, success_pickle


def set_dataset_attachments(client: Client, dataset: Dataset, dataset_version: DatasetVersionOutput):
    logging.getLogger("vectice.models.attachment_container").propagate = True
    attachments = None
    if dataset.attachments:
        container = AttachmentContainer(dataset_version, client)
        attachments = container.add_attachments(dataset.attachments)
    return attachments


def _serialize_model(model: Any) -> bytes:
    return pickle.dumps(model)
