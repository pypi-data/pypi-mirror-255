from asw_sdk.WebClient import WebClient


class GraphQlWebClient(WebClient):
    def __init__(self, config_manager):
        super().__init__("datatypes", config_manager, use_app_instance_session_code=True)

    def get_app_graphql_endpoint(self):
        return "/app-api/graphql"

    def query(self, graphql_query, graphql_query_type):
        graphql_query_obj = {
            "query": graphql_query
        }
        app_graphql_endpoint = self.get_app_graphql_endpoint()
        headers = {"graphqlOpType": graphql_query_type}
        return super().post_entity(app_graphql_endpoint, json_data=graphql_query_obj, headers=headers)
