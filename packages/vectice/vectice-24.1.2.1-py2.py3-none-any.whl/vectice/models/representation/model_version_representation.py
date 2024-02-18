from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from vectice.api.json.model_version import ModelVersionStatus
from vectice.api.json.model_version_representation import ModelVersionRepresentationOutput, ModelVersionUpdateInput

_logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from vectice.api.client import Client


class ModelVersionRepresentation:
    def __init__(self, output: ModelVersionRepresentationOutput, client: "Client"):
        self.id = output.id
        self.project_id = output.project_id
        self.name = output.name
        self.status = output.status
        self.description = output.description
        self.technique = output.technique
        self.library = output.library
        self._client = client
        self.model_name = output.model_name

    def update(self, status: str | None = None) -> None:
        """Update the status of the Model Version from the API.

        Parameters:
            status: The new status of the model. Accepted values are EXPERIMENTATION, STAGING, PRODUCTION and RETIRED.

        Returns:
            None
        """
        if status is None:
            _logger.warning("No status update provided. Nothing to update.")
            return

        try:
            status_enum = ModelVersionStatus(status.strip().upper())
        except ValueError as err:
            accepted_statuses = ", ".join([f"{status_enum.value!r}" for status_enum in ModelVersionStatus])
            raise ValueError(f"'{status}' is an invalid value. Please use [{accepted_statuses}].") from err

        model_input = ModelVersionUpdateInput(status=status_enum.value)
        self._client.update_model(self.id, model_input)
        old_status = self.status.value
        self.status = status_enum
        _logger.info(f"Model version {self.id!r} transitioned from {old_status!r} to {self.status.value!r}.")
