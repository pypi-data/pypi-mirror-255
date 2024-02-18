from asw_sdk.GraphQlWebClient import GraphQlWebClient
from asw_sdk.ConfigurationManager import ConfigurationManager
from asw_sdk.RegisterModelProps import RegisterModelProps
import os


class MLModel:
    def __init__(self, override_config=None, overriden_config_node=None):
        self._config_manager = None
        if overriden_config_node and override_config:
            self._config_manager = ConfigurationManager(overriden_config_node, override_config)
        else:
            self._config_manager = ConfigurationManager(os.environ['PYTHON_CONFIG_NODE'])
        self._graphql_web_client = GraphQlWebClient(self._config_manager)
        self._graphql_web_client.refresh_token()

    def register_model(self, props: RegisterModelProps):
        ml_code = self._config_manager.get_ml_code()
        ml_model_api = self._config_manager.get_ml_model_api()
        group_id = self._config_manager.get_current_group_id()
        query = f"""
            query MyQuery {{
              {ml_model_api}(
                filter: {{
                  ml_code: {{ equalTo: "{ml_code}" }}
                  and: {{ group_id: {{ equalTo: "{group_id}" }} }}
                }}
              ) {{
                  nodes {{
                    ml_model_id
                    }}
              }}
            }}
            """
        all_ml_models_for_group_json = self._graphql_web_client.query(query, "query")
        if len(all_ml_models_for_group_json["data"][ml_model_api]["nodes"]) == 0:
            self.create_new_ml_model(props)
        else:
            self.update_ml_model(all_ml_models_for_group_json["data"][ml_model_api]["nodes"][0]["ml_model_id"], props)

    def get_active_model_by_group(self, group_id):
        ml_code = self._config_manager.get_ml_code()
        ml_model_api = self._config_manager.get_ml_model_api()
        query = f"""
            query MyQuery {{
                {ml_model_api}(
                    filter: {{
                        ml_code: {{ equalTo: "{ml_code}" }}
                        and: {{ group_id: {{ equalTo: "{group_id}" }} }}
                    }}
                ) {{
                    nodes {{
                        step_id
                        ml_model_id
                        ml_code
                        job_code
                        is_deleted
                        group_id
                        mlModelVersionsApis(filter: {{ is_active: {{ equalTo: true }} }}) {{
                            nodes {{
                                additional_params_json
                                hyperparameter_json
                                is_active
                                is_deleted
                                ml_model_id
                                ml_model_versions_id
                                model_location
                                run_id
                                run_through
                                target_columns_json
                                training_features_json
                                version
                                mlModelVersionMetricsByMlModelVersionsId {{
                                    nodes {{
                                        chart_type
                                        is_deleted
                                        ml_model_version_metrics_id
                                        ml_model_versions_id
                                        name
                                        value
                                    }}
                                }}
                                description
                            }}
                        }}
                    }}
                }}
            }}
            """

        return self._graphql_web_client.query(query, "query")

    def get_current_active_model(self):
        group_id = self._config_manager.get_current_group_id()
        return self.get_active_model_by_group(group_id)

    def create_new_ml_model(self, props: RegisterModelProps):
        ml_model_api = self._config_manager.get_ml_model_api()
        ml_code = self._config_manager.get_ml_code()
        ml_model_step = self._config_manager.get_currently_executing_step_name()
        run_through = props.run_through
        run_id = self._config_manager.get_current_run_id()
        training_features = props.training_features
        target_cols = props.target_cols
        group_id = self._config_manager.get_current_group_id()
        additional_params = props.additional_params
        ml_model_version_desc = props.ml_model_version_desc
        hyper_parameters_json = props.hyper_parameters_json
        is_active_string = "true" if props.is_active else "false"
        model_location = props.model_location
        metrics_json = props.metrics_json
        job_code = self._config_manager.get_job_code()
        query = f"""
            mutation MyMutation {{
              create{ml_model_api}(
                input: {{
                  {ml_model_api}: {{
                    group_id: "{group_id}"
                    is_deleted: false
                    ml_code: "{ml_code}"
                    step_id: "{ml_model_step}"
                    job_code: "{job_code}"
                    mlModelVersionsApisUsingMlModelId: {{
                      create: {{
                        additional_params_json: "{additional_params}"
                        description: "{ml_model_version_desc}"
                        hyperparameter_json: "{hyper_parameters_json}"
                        is_active: {is_active_string}
                        is_deleted: false
                        run_through: "{run_through}"
                        model_location: "{model_location}"
                        run_id: "{run_id}"
                        target_columns_json: "{target_cols}"
                        training_features_json: "{training_features}"
                        mlModelVersionMetricsApisUsingMlModelVersionsId: {{
                          create: {metrics_json}
                        }}
                      }}
                    }}
                  }}
                }}
              ) {{
                mlModelApiEdge {{
                  node {{
                    mlModelVersionsApis(last: 1) {{
                      nodes {{
                        ml_model_versions_id
                        ml_model_id
                      }}
                    }}
                  }}
                }}
              }}
            }}
            """
        inserted_ml_model = self._graphql_web_client.query(query, "mutation")
        ml_model_versions_id = \
            inserted_ml_model["data"]["create" + ml_model_api]["mlModelApiEdge"]["node"]["mlModelVersionsApis"][
                "nodes"][0][
                "ml_model_versions_id"]
        ml_model_id = \
            inserted_ml_model["data"]["create" + ml_model_api]["mlModelApiEdge"]["node"]["mlModelVersionsApis"][
                "nodes"][0][
                "ml_model_id"]
        self.update_version(ml_model_id, ml_model_versions_id)

    def update_version(self, ml_model_id, ml_model_versions_id):
        ml_model_versions_api = self._config_manager.get_ml_model_versions_api()
        latest_version_query = f"""
        query MyQuery {{
          {ml_model_versions_api}(filter: {{ ml_model_id: {{ equalTo: "{ml_model_id}" }} }}) {{
            totalCount
          }}
        }}
        """
        latest_version_id = self._graphql_web_client.query(latest_version_query, "query")
        update_version_query = f"""
        mutation MyMutation {{
        update{ml_model_versions_api}(
            input: {{patch: {{version: {latest_version_id["data"][ml_model_versions_api]["totalCount"]} }}, ml_model_versions_id: "{ml_model_versions_id}"}}
        ){{
            clientMutationId
            }}
        }}

        """
        self._graphql_web_client.query(update_version_query, "mutation")

    def update_ml_model(self, ml_model_id, props: RegisterModelProps):
        ml_model_api = self._config_manager.get_ml_model_api()
        run_through = props.run_through
        run_id = self._config_manager.get_current_run_id()
        training_features = props.training_features
        model_location = props.model_location
        target_cols = props.target_cols
        additional_params = props.additional_params
        ml_model_version_desc = props.ml_model_version_desc
        hyper_parameters_json = props.hyper_parameters_json
        is_active_string = "true" if props.is_active else "false"
        metrics_json = props.metrics_json
        query = f"""
        mutation MyMutation {{
          update{ml_model_api}(
            input: {{
              patch: {{
                is_deleted: false
                mlModelVersionsApisUsingMlModelId: {{
                  create: {{
                    additional_params_json: "{additional_params}"
                    description: "{ml_model_version_desc}"
                    hyperparameter_json: "{hyper_parameters_json}"
                    is_active: {is_active_string}
                    is_deleted: false
                    run_through: "{run_through}"
                    model_location: "{model_location}"
                    run_id: "{run_id}"
                    target_columns_json: "{target_cols}"
                    training_features_json: "{training_features}"
                    mlModelVersionMetricsApisUsingMlModelVersionsId: {{
                      create: {metrics_json}
                    }}
                  }}
                }}
              }}
              ml_model_id: "{ml_model_id}"
            }}
          ) {{
            mlModelApiEdge {{
              node {{
                mlModelVersionsApis(last: 1) {{
                  nodes {{
                    ml_model_versions_id
                  }}
                }}
              }}
            }}
          }}
        }}
        """
        inserted_ml_model = self._graphql_web_client.query(query, "mutation")
        ml_model_versions_id = \
            inserted_ml_model["data"]["update" + ml_model_api]["mlModelApiEdge"]["node"]["mlModelVersionsApis"][
                "nodes"][0][
                "ml_model_versions_id"]
        self.update_version(ml_model_id, ml_model_versions_id)


if __name__ == '__main__':
    # ml_model = MLModel(f"""{{
    #                    "TOKEN": "eyJob3N0TmFtZSI6Imh0dHBzOi8vc2Fua2V0MTk5NC5hbHBoYS5sb2NhbDo5OTk4IiwicmVmcmVzaFRva2VuIjoicl9Ncll1dzRZWGo3WnplU3V6Iiwid3NIb3N0TmFtZSI6IndzczovL3NhbmtldDE5OTQud3MuYWxwaGEubG9jYWw6OTk5OC93cyJ9",
    # "tenantDataFolder":"abc",
    #                    "nodes": {{
    #     "65ee6b4abf0743e9988255406c410280": {{
    #         "applicationDataTypeId": 120,
    #         "applicationGroupId": 15,
    #         "cittaAgent": {{
    #             "launcher": {{
    #                 "pipelineConf": {{
    #                     "executionProfileId": "ep1",
    #                     "executionProfileObjectName": "exp_object_name",
    #                     "filterName": "smm-1",
    #                     "groupId": 1,
    #                     "jobCode": "GVGWFHBMKMJUAGR",
    #                     "mlCode": "ml_code1",
    #                     "mlModelApiName": "ml_model_api",
    #                     "mlModelObjectName": "ml_model",
    #                     "mlModelVersionApi": "ml_model_versions_api",
    #                     "mlModelVersionMetricsApi": "ml_model_version_metrics_api",
    #                     "mlModelVersionMetricsObjectName": "ml_model_version_metrics",
    #                     "mlModelVersionObjectName": "ml_model_versions",
    #                     "runId": "test_runId"
    #                 }}
    #             }}
    #         }},
    #         "currentFilterId": 4094,
    #         "currentlyExecutingJobId": null,
    #         "invokingAppInstanceId": 2,
    #         "rootDagContextId": 15,
    #         "sessionCode": "zpsa_1_1_2",
    #         "versionTagId": 15
    #     }}
    # }}
    # }}""", overriden_config_node="65ee6b4abf0743e9988255406c410280")
    ml_model = MLModel()
    print(ml_model.get_current_active_model())
    # props = RegisterModelProps(model_id=None, model_location="//ss1", is_active=True
    #                            , run_through="1"
    #                            , training_features="[{name:'x',value:'1'},{name:'y',value:'2'}]"
    #                            , target_cols="['abc','cde','efg']"
    #                            , additional_params="{}"
    #                            , ml_model_version_desc="version desc 1"
    #                            , hyper_parameters_json="{name:'x',value:'1', age:20, type:'t1'}"
    #                            , metrics_json="[{ chart_type: \"line\", name: \"char_name\", value: \"[{x:100,y:100}]\", is_deleted: false }]")
    #
    # ml_model.register_model(props)
