from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any

from vectice.api.json.json_type import TJSON
from vectice.api.json.paged_response import PagedResponse
from vectice.api.json.step import PhaseOutput

if TYPE_CHECKING:
    from vectice.api.json.step import StepOutput


class IterationStatus(Enum):
    NotStarted = "NotStarted"
    InProgress = "InProgress"
    InReview = "InReview"
    Abandoned = "Abandoned"
    Completed = "Completed"


class IterationStepArtifactType(Enum):
    ModelVersion = "ModelVersion"
    DataSetVersion = "DataSetVersion"
    EntityFile = "EntityFile"
    JobRun = "JobRun"
    Comment = "Comment"


class IterationStepArtifact(TJSON):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @property
    def text(self) -> int | float | str | None:
        if self.get("text"):
            text = self["text"]
            if isinstance(text, float):
                return float(text)
            elif isinstance(text, int):
                return int(text)
            return str(text)
        return None

    @property
    def dataset_version_id(self) -> str | None:
        if self.get("datasetVersion"):
            return str(self["datasetVersion"]["vecticeId"])
        elif self.get("datasetVersionId"):
            return str(self["datasetVersionId"])
        else:
            return None

    @property
    def model_version_id(self) -> str | None:
        if self.get("modelVersion"):
            return str(self["modelVersion"]["vecticeId"])
        elif self.get("modelVersionId"):
            return str(self["modelVersionId"])
        else:
            return None

    @property
    def entity_file_id(self) -> int | None:
        if self.get("entityFileId"):
            return int(self["entityFileId"])
        else:
            return None

    @property
    def type(self) -> IterationStepArtifactType:
        return IterationStepArtifactType(self["type"])


class IterationStepArtifactInput(dict):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @property
    def id(self) -> int | str | None:
        if self.get("id"):
            return int(self["id"]) if isinstance(self["id"], int) else str(self["id"])
        return None

    @property
    def text(self) -> int | float | str | None:
        if self.get("text"):
            text = self["text"]
            if isinstance(text, float):
                return float(text)
            elif isinstance(text, int):
                return int(text)
            return str(text)
        return None

    @property
    def type(self) -> str:
        return str(self["type"])

    @property
    def dataset_version_id(self) -> str | None:
        if self.get("datasetVersionId"):
            return str(self["datasetVersionId"])
        else:
            return None

    @property
    def model_version_id(self) -> str | None:
        if self.get("modelVersionId"):
            return str(self["modelVersionId"])
        else:
            return None

    @property
    def entity_file_id(self) -> int | None:
        if self.get("entityFileId"):
            return int(self["entityFileId"])
        else:
            return None


class IterationInput(TJSON):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)


class IterationOutput(TJSON):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._phase: PhaseOutput | None = None
        if "phase" in self:
            self._phase = PhaseOutput(**self["phase"])

    @property
    def id(self) -> str:
        return str(self["vecticeId"])

    @property
    def index(self) -> int:
        return int(self["index"])

    @property
    def sections(self) -> PagedResponse[StepOutput]:
        from vectice.api.gql_api import Parser

        return Parser().parse_paged_response(self["sections"])

    @property
    def steps(self) -> list[StepOutput]:
        from vectice.api.json.step import StepOutput

        steps_json = self["steps"]
        steps = [StepOutput(step) for step in steps_json]
        return steps

    @property
    def alias(self) -> str:
        return str(self["alias"])

    @property
    def status(self) -> IterationStatus:
        return IterationStatus(self["status"])

    @property
    def phase(self) -> PhaseOutput | None:
        return self._phase

    @property
    def starred(self) -> bool:
        return bool(self["starred"])

    @property
    def ownername(self) -> str:
        return str(self["owner"]["name"])

    @property
    def artifacts_count(self) -> int:
        return int(self["paginatedArtifacts"]["total"])


class IterationContextInput(TJSON):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @property
    def id(self) -> str:
        return str(self["iterationId"])

    @property
    def section(self) -> str | None:
        if self.get("stepName"):
            return str(self["stepName"])
        return None
