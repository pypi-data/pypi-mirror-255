from __future__ import annotations

from gql import gql

from vectice.api.gql_api import GqlApi, Parser
from vectice.api.json.entity_file import EntityFileOutput

_RETURNS = """
            fileName
            __typename
            """


class GqlEntityFileApi(GqlApi):
    def get_entity_file_by_id(self, id: int) -> EntityFileOutput:
        gql_query = "getEntityFileById"
        variable_types = "$id:Float!"
        kw = "id:$id"
        variables = {"id": id}
        query = GqlApi.build_query(
            gql_query=gql_query, variable_types=variable_types, returns=_RETURNS, keyword_arguments=kw, query=True
        )
        query_built = gql(query)
        response = self.execute(query_built, variables)
        output: EntityFileOutput = Parser().parse_item(response[gql_query])
        return output
