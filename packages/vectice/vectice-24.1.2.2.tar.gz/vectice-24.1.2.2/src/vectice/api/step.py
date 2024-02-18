from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from gql import gql

from vectice.utils.api_utils import INDEX_ORDERED, PAGINATE_OUTPUT, get_page_input

if TYPE_CHECKING:
    from vectice.api.json import IterationStepArtifactInput, StepOutput

from gql.transport.exceptions import TransportQueryError

from vectice.api.gql_api import GqlApi, Parser
from vectice.api.json.paged_response import PagedResponse
from vectice.api.json.step import StepType

_logger = logging.getLogger(__name__)

_RETURNS_WITH_LIST = """
                    index
                    description
                    slug
                    paginatedArtifacts {
                        items {
                            id
                        }
                        total
                    }
                    __typename

            """

_RETURNS_WITH_STEPS = """
                    id
                    index
                    name
                    description
                    stepType
                    slug
                    paginatedArtifacts {
                        items {
                            entityFileId
                            modelVersion {
                                vecticeId
                            }
                            datasetVersion {
                                vecticeId
                            }
                            text
                            type
                        }
                    }
                    __typename

            """


_RETURNS = """
                id
                index
                name
                description
                stepType
                slug
                paginatedArtifacts {
                    items {
                        entityFileId
                        modelVersion {
                            vecticeId
                        }
                        datasetVersion {
                            vecticeId
                        }
                        text
                        type
                    }
                }
                __typename
            """


_ADD_ARTIFACT_RETURNS = """
                id
                __typename
"""


class StepApi(GqlApi):
    def list_steps(self, iteration_id: str, populate: bool = True) -> PagedResponse[StepOutput]:
        gql_query = "getIterationStepList"
        variable_types = "$parentId:VecticeId!,$order:ListOrderInput,$page:PageInput,$filters:IterationStepFiltersInput"
        kw = "parentId:$parentId,order:$order,page:$page,filters:$filters"
        variables = {
            "parentId": iteration_id,
            "order": INDEX_ORDERED,
            "page": get_page_input() if not populate else get_page_input(1, 100),
            "filters": {"isVisible": None},
        }
        _returns = _RETURNS_WITH_STEPS if populate is True else _RETURNS_WITH_LIST
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=PAGINATE_OUTPUT.format(_returns),
            keyword_arguments=kw,
            query=True,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            step_output: PagedResponse[StepOutput] = Parser().parse_paged_response(response[gql_query])
            return step_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration", iteration_id)

    def add_iteration_step_artifact(self, data: IterationStepArtifactInput, step_id: int) -> StepOutput:
        gql_query = "addIterationStepArtifact"
        variable_types = "$id:Float!,$data:IterationStepArtifactInput!"
        variables = {"id": step_id, "data": data}
        kw = "id:$id, data:$data"
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_ADD_ARTIFACT_RETURNS,
            keyword_arguments=kw,
            query=False,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            step_output: StepOutput = Parser().parse_item(response[gql_query])
            return step_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "step", step_id)

    def update_iteration_step_artifact(
        self,
        step_id: int,
        step_type: StepType,
        artifacts: list[IterationStepArtifactInput] | None = None,
    ) -> StepOutput:
        gql_query = "updateIterationStepContent"
        variable_types = "$id:Float!,$data:IterationStepUpdateInput!"
        variables: dict[str, Any] = {
            "id": step_id,
            "data": {
                "stepType": step_type.value,
            },
        }
        if artifacts:
            variables["data"]["artifacts"] = artifacts
        kw = "id:$id, data:$data"
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS,
            keyword_arguments=kw,
            query=False,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            step_output: StepOutput = Parser().parse_item(response[gql_query])
            return step_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "step", step_id)

    def get_step(self, step: str, iteration_id: str) -> StepOutput:
        if isinstance(step, str) and iteration_id:  # pyright: ignore[reportUnnecessaryIsInstance]
            gql_query = "getStepByName"
            variable_types = "$name:String!,$parentId:VecticeId!"
            variables = {"name": step, "parentId": iteration_id}
            kw = "name:$name,parentId:$parentId"
        else:
            raise ValueError("Missing parameters: string and parent id required.")
        query = GqlApi.build_query(
            gql_query=gql_query, variable_types=variable_types, returns=_RETURNS, keyword_arguments=kw, query=True
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            step_output: StepOutput = Parser().parse_item(response[gql_query])
            return step_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "step", step)
