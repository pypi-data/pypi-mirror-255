# pyright: reportUnboundVariable=false
# this file is deprecated so we don't want to make changes because of type analysis
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import vectice
from vectice.api.json.iteration import (
    IterationStatus,
    IterationStepArtifact,
)
from vectice.api.json.step import StepType
from vectice.utils.deprecation import deprecate

if TYPE_CHECKING:
    from vectice import Connection
    from vectice.models import Iteration, Phase, Project, Workspace
    from vectice.models.model import Model
    from vectice.models.step_dataset import StepDataset
    from vectice.models.step_model import StepModel
    from vectice.models.step_number import StepNumber
    from vectice.models.step_string import StepString

_logger = logging.getLogger(__name__)

MISSING_DATASOURCE_ERROR_MESSAGE = "Cannot create modeling dataset. Missing %s data source."


class Step:
    """Model a Vectice step.

    Steps define the logical sequence of steps required to complete
    the phase along with their expected outcomes.

    Steps belong to an Iteration. The steps created under a Phase are
    Step Definitions that are then re-used in Iterations.

    ```tree
    phase 1
        step definition 1
        step definition 2
        step definition 3
    ```

    ```tree
    iteration 1 of phase 1
        step 1
        step 2
        step 3
    ```

    If steps are added to a phase after iterations have been created
    and completed, these steps won't appear in these iterations.

    NOTE: **Phases and Steps Definitions are created in the Vectice App,
    Iterations are created from the Vectice Python API.**

    To access the step and assign a value, you must use the "slug" of the step:
    the slug is the name of the step, transformed to fit Python's naming rules,
    and prefixed with `step_`. For example, a step called "Clean Dataset" can
    be accessed with `my_iteration.step_clean_dataset`.

    Therefore, to assign a value to a step:

    ```python
    my_clean_dataset = ...
    my_iteration.step_clean_dataset = my_clean_dataset
    ```

    You can assign a [`Model`][vectice.models.model.Model],
    [`Dataset`][vectice.models.dataset.Dataset], comments or files to any step.
    """

    def __init__(
        self,
        id: int,
        iteration: Iteration,
        name: str,
        index: int,
        slug: str,
        description: str | None = None,
        artifacts: list[IterationStepArtifact] | None = None,
        step_type: StepType = StepType.Step,
    ):
        self._id = id
        self._iteration: Iteration = iteration
        self._name = name
        self._index = index
        self._description = description
        self._client = self._iteration._client  # pyright: ignore[reportPrivateUsage]
        self._artifacts = artifacts or []
        self._slug = slug
        self._type: StepType = step_type
        self._model: Model | None = None

        self._iteration_read_only = self._iteration._status in {  # pyright: ignore[reportPrivateUsage]
            IterationStatus.Completed,
            IterationStatus.Abandoned,
        }
        if self._iteration_read_only:
            _logger.debug(f"Step {self.name}, iteration is {self._iteration.status} and is read-only!")

    def __repr__(self):
        return f"Step(name={self.name!r}, slug={self.slug!r}, id={self.id!r})"

    def __eq__(self, other: object):
        if not isinstance(other, Step):
            return NotImplemented
        return self.id == other.id

    @deprecate(
        warn_at="23.4",
        fail_at="24.1",
        remove_at="24.2",
        reason="This method is deprecated. Please use iteration.log() instead",
    )
    def __iadd__(self, value: Any):
        ...

    @deprecate(
        warn_at="23.4",
        fail_at="24.1",
        remove_at="24.2",
        reason="This method is deprecated. Please use iteration.log() instead",
    )
    def step_factory_and_update(self, value: Any) -> Step | StepString | StepNumber | StepDataset | StepModel:
        return self

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> int:
        """The step's id.

        Returns:
            The step's id.
        """
        return self._id

    @id.setter
    def id(self, step_id: int):
        self._id = step_id

    @property
    def index(self) -> int:
        """The step's index.

        Returns:
            The step's index.
        """
        return self._index

    @property
    def slug(self) -> str:
        """The step's slug.

        Returns:
            The step's slug.
        """
        return self._slug

    @property
    def properties(self) -> dict:
        """The step's name, id, and index.

        Returns:
            A dictionary containing the `name`, `id` and `index` items.
        """
        return {"name": self.name, "id": self.id, "index": self.index}

    @property
    def artifacts(self) -> list[IterationStepArtifact]:
        return self._artifacts

    @artifacts.setter
    def artifacts(self, artifacts: list[IterationStepArtifact]):
        self._artifacts = artifacts

    @property
    def connection(self) -> Connection:
        """The connection to which this step belongs.

        Returns:
            The connection to which this step belongs.
        """
        return self._iteration.connection

    @property
    def workspace(self) -> Workspace:
        """The workspace to which this step belongs.

        Returns:
            The workspace to which this step belongs.
        """
        return self._iteration.workspace

    @property
    def project(self) -> Project:
        """The project to which this step belongs.

        Returns:
            The project to which this step belongs.
        """
        return self._iteration.project

    @property
    def phase(self) -> Phase:
        """The phase to which this step belongs.

        Returns:
            The phase to which this step belongs.
        """
        return self._iteration.phase

    @property
    def iteration(self) -> Iteration:
        """The iteration to which this step belongs.

        Returns:
            The iteration to which this step belongs.
        """
        return self._iteration

    def _get_code_version_id(self):
        # TODO: cyclic imports
        from vectice.models.git_version import check_code_source, inform_if_git_repo

        if vectice.code_capture:
            return check_code_source(self._client, self.project.id)
        else:
            inform_if_git_repo()
            return None

    @property
    def model(self) -> Model | None:
        return self._model
