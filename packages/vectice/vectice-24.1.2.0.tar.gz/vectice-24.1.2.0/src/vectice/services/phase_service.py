from __future__ import annotations

import logging
import re
from textwrap import dedent
from typing import TYPE_CHECKING, ClassVar

from rich.table import Table

from vectice.api.http_error_handlers import (
    InvalidIdError,
    LastIterationNotWritableError,
    MultipleActiveIterationsError,
)
from vectice.api.json.iteration import IterationOutput, IterationStatus
from vectice.utils.common_utils import temp_print
from vectice.utils.logging_utils import get_iteration_status
from vectice.utils.vectice_ids_regex import ITERATION_VID_REG

if TYPE_CHECKING:
    from vectice.api import Client
    from vectice.models import Phase
    from vectice.models.iteration import Iteration


_logger = logging.getLogger(__name__)


class PhaseService:
    __slots__: ClassVar[list[str]] = ["_client"]

    def __init__(self, client: Client):
        self._client: Client = client

    def list_iterations(
        self, phase: Phase, only_mine: bool = False, statuses: list[IterationStatus] | None = None
    ) -> None:
        """Prints a list of iterations belonging to the phase in a tabular format, limited to the last 10 items.

        Parameters:
            only_mine: Display only the iterations where the user is the owner.
            statuses: Filter iterations on specified statuses.

        Returns:
            None

        """
        iteration_outputs = self._client.list_iterations(phase.id, only_mine, statuses)
        rich_table = Table(expand=True, show_edge=False)

        rich_table.add_column("Id", justify="left", no_wrap=True, min_width=3, max_width=20)
        rich_table.add_column("Index", justify="left", no_wrap=True, min_width=5, max_width=10)
        rich_table.add_column("Status", justify="left", no_wrap=True, min_width=3, max_width=15)
        rich_table.add_column("Owner", justify="left", no_wrap=True, min_width=5, max_width=15)

        for iteration in iteration_outputs.list:
            rich_table.add_row(
                str(iteration.id),
                str(iteration.index),
                get_iteration_status(iteration.status, iteration.starred),
                iteration.ownername,
            )

        iteration_statuses_log = (
            " | ".join(list(map(lambda status: get_iteration_status(status), statuses)))
            if statuses is not None and len(statuses) > 0
            else None
        )
        status_log = f"with status [{iteration_statuses_log}] " if iteration_statuses_log is not None else ""
        only_mine_log = "You have" if only_mine is True else "There are"
        description = f"""{only_mine_log} {iteration_outputs.total} iterations {status_log}in the phase {phase.name!r} and a maximum of 10 iterations are displayed in the table below:"""
        link = dedent(
            f"""
        # For quick access to the list of iterations in the Vectice web app, visit:
        # {self._client.auth.api_base_url}/phase/{phase.id}/iterations"""
        ).lstrip()
        temp_print(description)
        temp_print(table=rich_table)
        temp_print(link)

    def create_or_get_current_iteration(self, phase: Phase) -> Iteration | None:
        """Get or create an iteration.

        If your last updated iteration is writable (Not Started or In Progress), Vectice will return it.
        Otherwise, Vectice will create a new one and return it.
        If multiple writable iterations are found, Vectice will print a list of the iterations to complete or cancel.

        Returns:
            An iteration or None if Vectice could not determine which iteration to retrieve.

        Raises:
            VecticeException: When attempting to create an iteration but there isn't any step inside the phase.
        """
        try:
            iteration_output = self._client.get_last_iteration(phase_id=phase.id)
        except (LastIterationNotWritableError, MultipleActiveIterationsError) as e:
            _logger.warning(str(e.value))
            self.list_iterations(
                phase=phase, only_mine=True, statuses=[IterationStatus.NotStarted, IterationStatus.InProgress]
            )
            return None

        return self._build_iteration_from_output_and_log(phase=phase, iteration_output=iteration_output)

    def get_iteration_by_id_or_index(self, phase: Phase, index_or_id: int | str) -> Iteration:
        """Get an iteration.

        Fetch and return an iteration by index or id.

        Parameters:
            index: The index or id of an existing iteration.

        Returns:
            An iteration.

        Raises:
            InvalidIdError: When index is a string and not matching 'ITR-[int]'
            IterationIdError: Iteration with specified id does not exist.
            IterationIndexError: Iteration with specified index does not exist.
        """
        if isinstance(index_or_id, str):
            if re.search(ITERATION_VID_REG, index_or_id):
                iteration_output = self._client.get_iteration_by_id(index_or_id)
            else:
                raise InvalidIdError("iteration", index_or_id)
        else:
            iteration_output = self._client.get_iteration_by_index(phase_id=phase.id, index=index_or_id)

        return self._build_iteration_from_output_and_log(phase=phase, iteration_output=iteration_output)

    def create_iteration(self, phase: Phase) -> Iteration:
        """Create a new iteration.

        Create and return an iteration.

        Returns:
            An iteration.
        """
        from vectice.models.iteration import Iteration

        iteration_output = self._client.create_iteration(phase_id=phase.id)
        logging_output = dedent(
            f"""
        New Iteration number {iteration_output.index!r} created.

        For quick access to the Iteration in the Vectice web app, visit:
        {self._client.auth.api_base_url}/browse/iteration/{iteration_output.id}"""
        ).lstrip()
        _logger.info(logging_output)

        iteration = Iteration(iteration_output, phase, self._client)
        return iteration

    def get_active_iteration_or_create(self, phase: Phase) -> Iteration:
        """Get latest active iteration or create one.

        Get or create and return an iteration.

        Parameters:
            phase: The iteration's phase.

        Returns:
            An iteration.
        """
        iteration_output = self._client.get_active_iteration_or_create(phase.id)
        return self._build_iteration_from_output_and_log(phase=phase, iteration_output=iteration_output)

    def _build_iteration_from_output_and_log(self, phase: Phase, iteration_output: IterationOutput) -> Iteration:
        from vectice.models.iteration import Iteration

        iteration = Iteration(iteration_output, phase, self._client)
        base_log = dedent(f"Iteration number {iteration.index!r} successfully retrieved.")
        if iteration_output.status in [IterationStatus.Completed, IterationStatus.Abandoned]:
            base_log += dedent(
                f"""
                WARN: Iteration is {iteration.status}."""
            )

        logging_output = dedent(
            f"""
                {base_log}

                For quick access to the Iteration in the Vectice web app, visit:
                {self._client.auth.api_base_url}/browse/iteration/{iteration.id}"""
        ).lstrip()
        _logger.info(logging_output)
        return iteration
