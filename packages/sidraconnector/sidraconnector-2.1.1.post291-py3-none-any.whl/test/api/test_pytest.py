# from unittest.mock import patch, Mock

# import io
# import json
# import pytest

# from pysidra.api.controllers.modelserving.modelversion import CreateImageRequest, DeployRequest, InferenceRequest
# from test_constants import TestConstants

# from pysidra.api.auth import Authentication
# from pysidra.api.client import Client
# from pysidra.api.controllers import Constants


# def test_authentication_ok():
#     with patch(
#             "requests.request",
#             return_value=Mock(
#                 status_code=200,
#                 text=json.dumps({"access_token": "{}".format(TestConstants.TOKEN)}),
#             ),
#     ) as mock_request:
#         val = Authentication(
#             base_url=TestConstants.BASE_URL,
#             scope=TestConstants.SCOPE,
#             client_id=TestConstants.CLIENT_ID,
#             client_secret=TestConstants.CLIENT_SECRET,
#         ).get_token()
#         assert val == TestConstants.TOKEN
#         assert mock_request.call_args[0][0] == "POST"
#         assert mock_request.call_count == 1
#         assert mock_request.call_args == TestConstants.AUTH_PARAMS


# def test_authentication_fail():
#     with patch(
#             "requests.request",
#             return_value=Mock(
#                 status_code=200,
#                 text=json.dumps({"access_token": "{}".format(TestConstants.FAIL_TOKEN)}),
#             ),
#     ) as mock_request:
#         val = Authentication(
#             base_url=TestConstants.FAIL_BASE_URL,
#             scope=TestConstants.SCOPE,
#             client_id=TestConstants.CLIENT_ID,
#             client_secret=TestConstants.CLIENT_SECRET,
#         ).get_token()
#         assert val != TestConstants.TOKEN
#         assert mock_request.call_args[0][0] == "POST"
#         assert mock_request.call_count == 1
#         assert mock_request.call_args != TestConstants.AUTH_PARAMS


# @pytest.fixture(scope="session")
# def sidraclient():
#     url = TestConstants.ENDPOINT
#     token = TestConstants.TOKEN
#     return Client(url, token)


# # DATACATALOG/ATTRIBUTES
# def test_attributes_get_list(sidraclient):
#     with patch("requests.request",
#                return_value=Mock(
#                    status_code=200,
#                    raise_for_status=lambda: None,
#                    text=TestConstants.EMPTY_PAGINATION_RESPONSE)
#                ) as mock_request:
#         sidraclient.Datacatalog.Attributes.get_list()
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_ATTRIBUTES_GET_LIST
#         )


# def test_attributes_get_by_id(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Datacatalog.Attributes.get_by_id(TestConstants.ID)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert mock_request.call_args[1][
#                    "url"
#                ] == sidraclient.endpoint + Constants.URL_ATTRIBUTES_GET_BY_ID.format(
#             TestConstants.ID
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1


# # DATACATALOG/DATASTORAGEUNIT
# def test_datastorageunit_get_list(sidraclient):
#     with patch("requests.request",
#                return_value=Mock(
#                    status_code=200,
#                    raise_for_status=lambda: None,
#                    text=TestConstants.EMPTY_PAGINATION_RESPONSE)) as mock_request:
#         sidraclient.Datacatalog.DataStorageUnit.get_list()
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_DATASTORAGEUNIT_GET_LIST
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1


# def test_datastorageunit_get_by_id(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Datacatalog.DataStorageUnit.get_by_id(TestConstants.ID)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert mock_request.call_args[1][
#                    "url"
#                ] == sidraclient.endpoint + Constants.URL_DATASTORAGEUNIT_GET_BY_ID.format(
#             TestConstants.ID
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1


# # DATACATALOG/ENTITIES
# def test_entities_get_list(sidraclient):
#     with patch("requests.request",
#                return_value=Mock(
#                    status_code=200,
#                    raise_for_status=lambda: None,
#                    text=TestConstants.EMPTY_PAGINATION_RESPONSE)) as mock_request:
#         sidraclient.Datacatalog.Entities.get_list()
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_ENTITIES_GET_LIST
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1


# def test_entities_get_by_id(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Datacatalog.Entities.get_by_id(TestConstants.ID)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert mock_request.call_args[1][
#                    "url"
#                ] == sidraclient.endpoint + Constants.URL_ENTITIES_GET_BY_ID.format(
#             TestConstants.ID
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1


# def test_entities_get_pipelines(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Datacatalog.Entities.get_pipelines(idEntity=TestConstants.ID)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert mock_request.call_args[1][
#                    "url"
#                ] == sidraclient.endpoint + Constants.URL_ENTITIES_GET_PIPELINES.format(
#             TestConstants.ID
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1


# def test_entities_get_tags(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Datacatalog.Entities.get_tags(idEntity=TestConstants.ID)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert mock_request.call_args[1][
#                    "url"
#                ] == sidraclient.endpoint + Constants.URL_ENTITIES_GET_TAGS.format(
#             TestConstants.ID
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1


# def test_entities_get_attributes(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Datacatalog.Entities.get_attributes(idEntity=TestConstants.ID)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert mock_request.call_args[1][
#                    "url"
#                ] == sidraclient.endpoint + Constants.URL_ENTITIES_GET_ATTRIBUTES.format(
#             TestConstants.ID
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1


# def test_entities_set_attributes(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Datacatalog.Entities.set_attributes(
#             idEntity=TestConstants.ID, attributes=TestConstants.ATTRIBUTES_JSON
#         )
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "PUT"
#         assert mock_request.call_args[1][
#                    "url"
#                ] == sidraclient.endpoint + Constants.URL_ENTITIES_SET_ATTRIBUTES.format(
#             TestConstants.ID
#         )
#         assert len(json.loads(mock_request.call_args[1]["data"])) == len(
#             TestConstants.ATTRIBUTES_JSON
#         )


# def test_entities_get_with_attributes(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Datacatalog.Entities.get_with_attributes([TestConstants.ID])
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_ENTITIES_GET_WITH_ATTRIBUTES
#         )


# def test_entities_update_recreate_table(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Datacatalog.Entities.update_recreate_table([TestConstants.ID], True)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "PUT"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_ENTITIES_UPDATE_RECREATE_TABLE
#         )


# def test_entities_update_deployment_date(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Datacatalog.Entities.update_deployment_date([TestConstants.ID])
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "PUT"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_ENTITIES_UPDATE_DEPLOYMENT_DATE
#         )


# # DATACATALOG/PROVIDERS
# def test_providers_get_list(sidraclient):
#     with patch("requests.request",
#                return_value=Mock(
#                    status_code=200,
#                    raise_for_status=lambda: None,
#                    text=TestConstants.EMPTY_PAGINATION_RESPONSE)) as mock_request:
#         sidraclient.Datacatalog.Providers.get_list()
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_PROVIDERS_GET_LIST
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1


# def test_providers_get_by_id(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Datacatalog.Providers.get_by_id(TestConstants.ID)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert mock_request.call_args[1][
#                    "url"
#                ] == sidraclient.endpoint + Constants.URL_PROVIDERS_GET_BY_ID.format(
#             TestConstants.ID
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1


# def test_providers_get_tags(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Datacatalog.Providers.get_tags(
#             providersId=TestConstants.PROVIDERS_ID
#         )
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert mock_request.call_args[1][
#                    "url"
#                ] == sidraclient.endpoint + Constants.URL_PROVIDERS_GET_TAGS.format(
#             TestConstants.ID
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1


# # DATACATALOG/TAGS
# def test_tags_get_list(sidraclient):
#     with patch("requests.request",
#                return_value=Mock(
#                    status_code=200,
#                    raise_for_status=lambda: None,
#                    text=TestConstants.EMPTY_PAGINATION_RESPONSE)) as mock_request:
#         sidraclient.Datacatalog.Tags.get_list()
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_TAGS_GET_LIST
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1


# # OPERATIONS/ASSETSTATUS
# def test_assetstatus_get(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Operations.AssetStatus.get_status_list()
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_ASSETSTATUS_GET_STATUS_LIST
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1


# # OPERATIONS/ASSET
# def test_assets_get_list(sidraclient):
#     with patch("requests.request",
#                return_value=Mock(
#                    status_code=200,
#                    raise_for_status=lambda: None,
#                    text=TestConstants.EMPTY_PAGINATION_RESPONSE)) as mock_request:
#         sidraclient.Operations.Assets.get_list()
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_ASSETS_GET_LIST
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1


# def test_assets_get_by_id(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Operations.Assets.get_by_id(TestConstants.ID)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert mock_request.call_args[1][
#                    "url"
#                ] == sidraclient.endpoint + Constants.URL_ASSETS_GET_BY_ID.format(
#             TestConstants.ID
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1


# # OPERATIONS/SERVICE
# def test_service_get_clusters(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Operations.Service.get_clusters()
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_SERVICE_GET_CLUSTERS
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1


# def test_service_get_services(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Operations.Service.get_services()
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_SERVICE_GET_SERVICES
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1


# def test_service_get_datastorageunits(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Operations.Service.get_datastorageunits()
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_SERVICE_GET_DATASTORAGEUNITS
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1


# def test_service_get_last_errors(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Operations.Service.get_last_errors()
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_SERVICE_GET_LAST_ERRORS
#         )
#         assert len(mock_request.call_args[1]["params"]) == 2


# def test_service_get_last_warnings(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Operations.Service.get_last_warnings()
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_SERVICE_GET_LAST_WARNINGS
#         )
#         assert len(mock_request.call_args[1]["params"]) == 2


# def test_service_get_count_errors(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Operations.Service.get_count_errors(
#             offsetId=TestConstants.OFFSET_ID
#         )
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert mock_request.call_args[1][
#                    "url"
#                ] == sidraclient.endpoint + Constants.URL_SERVICE_GET_COUNT_ERRORS.format(
#             TestConstants.OFFSET_ID
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1


# def test_service_get_warnings_count(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Operations.Service.get_count_warnings(
#             offsetId=TestConstants.OFFSET_ID
#         )
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert mock_request.call_args[1][
#                    "url"
#                ] == sidraclient.endpoint + Constants.URL_SERVICE_GET_COUNT_WARNINGS.format(
#             TestConstants.OFFSET_ID
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1


# def test_service_get_log_count(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Operations.Service.get_count_log(offsetId=TestConstants.OFFSET_ID)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert mock_request.call_args[1][
#                    "url"
#                ] == sidraclient.endpoint + Constants.URL_SERVICE_GET_COUNT_LOG.format(
#             TestConstants.OFFSET_ID
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1


# def test_service_get_measure(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Operations.Service.get_measure()
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_SERVICE_GET_MEASURE
#         )
#         assert len(mock_request.call_args[1]["params"]) == 2


# def test_service_get_daily_measure(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Operations.Service.get_daily_measures(
#             measure=TestConstants.DAILY_MEASURE
#         )
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_SERVICE_GET_DAILY_MEASURES
#         )
#         assert len(mock_request.call_args[1]["params"]) == 2


# # INTEGRATION/QUERY
# def test_query_id_filter(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Integration.Query.get_id_filter(
#             idEntity=TestConstants.IDENTITY,
#             commaSeparatedColumns=TestConstants.COMMA_SEPARATED_COLUMNS,
#         )
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert mock_request.call_args[1][
#                    "url"
#                ] == sidraclient.endpoint + Constants.URL_QUERY_GET_ID_FILTER.format(
#             TestConstants.IDENTITY
#         )
#         assert len(mock_request.call_args[1]["params"]) == 4


# def test_query_prefilter(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Integration.Query.get_prefilter(
#             idEntity=TestConstants.IDENTITY,
#             commaSeparatedColumns=TestConstants.COMMA_SEPARATED_COLUMNS,
#             lastExportedAssetIds=TestConstants.LAST_EXPORTED_ASSET_IDS,
#             commaSeparatedFilterColumns=TestConstants.COMMA_SEPARATED_FILTER_COLUMNS,
#         )
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert mock_request.call_args[1][
#                    "url"
#                ] == sidraclient.endpoint + Constants.URL_QUERY_GET_PREFILTER.format(
#             TestConstants.IDENTITY
#         )
#         assert len(mock_request.call_args[1]["params"]) == 6


# def test_query_execute(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Integration.Query.get_execute(
#             databaseName=TestConstants.DATABASE_NAME,
#             tableName=TestConstants.TABLE_NAME,
#             commaSeparatedColumns=TestConstants.COMMA_SEPARATED_COLUMNS,
#         )
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_QUERY_GET_EXECUTE
#         )
#         assert len(mock_request.call_args[1]["params"]) == 6


# def test_query_get_status(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Integration.Query.get_status(
#             pollingToken=TestConstants.POLLINGTOKEN
#         )
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_QUERY_GET_STATUS
#         )
#         assert len(mock_request.call_args[1]["params"]) == 3


# def test_query_get_stream(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Integration.Query.get_stream(
#             pollingToken=TestConstants.POLLINGTOKEN
#         )
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_QUERY_GET_STREAM
#         )
#         assert len(mock_request.call_args[1]["params"]) == 2


# def test_query_get_file_columns_ok(sidraclient):
#     with patch(
#             "requests.request",
#             side_effect=[
#                 Mock(
#                     status_code=200,
#                     text=json.dumps(
#                         {"pollingToken": "{}".format(TestConstants.POLLINGTOKEN)}
#                     ),
#                 ),
#                 Mock(
#                     status_code=200,
#                     text=json.dumps(
#                         {
#                             "executionStatus": {"lifecycleState": "TERMINATED"},
#                             "sasToken": "FakeSasLink",
#                         }
#                     ),
#                 ),
#             ],
#     ) as mock_request:
#         sidraclient.Integration.Query._get_file(
#             idEntity=TestConstants.IDENTITY,
#             commaSeparatedColumns=TestConstants.COMMA_SEPARATED_COLUMNS,
#         )
#         assert mock_request.call_count == 2
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_QUERY_GET_STATUS
#         )
#         assert len(mock_request.call_args[1]["params"]) == 3
#         assert mock_request.call_args_list[0][0][0] == "GET"
#         assert mock_request.call_args_list[0][1][
#                    "url"
#                ] == sidraclient.endpoint + Constants.URL_QUERY_GET_ID_FILTER.format(
#             TestConstants.IDENTITY
#         )
#         assert len(mock_request.call_args_list[0][1]["params"]) == 4


# def test_query_get_file_columns_running(sidraclient):
#     with patch(
#             "requests.request",
#             side_effect=[
#                 Mock(
#                     status_code=200,
#                     text=json.dumps(
#                         {"pollingToken": "{}".format(TestConstants.POLLINGTOKEN)}
#                     ),
#                 ),
#                 Mock(
#                     status_code=200,
#                     text=json.dumps(
#                         {"executionStatus": {"lifecycleState": "RUNNING"}, "sasToken": []}
#                     ),
#                 ),
#                 Mock(
#                     status_code=200,
#                     text=json.dumps(
#                         {
#                             "executionStatus": {"lifecycleState": "TERMINATED"},
#                             "sasToken": "FakeSasLink",
#                         }
#                     ),
#                 ),
#             ],
#     ) as mock_request:
#         sidraclient.Integration.Query._get_file(
#             idEntity=TestConstants.IDENTITY,
#             commaSeparatedColumns=TestConstants.COMMA_SEPARATED_COLUMNS,
#         )
#         assert mock_request.call_count == 3
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_QUERY_GET_STATUS
#         )
#         assert len(mock_request.call_args[1]["params"]) == 3
#         assert mock_request.call_args_list[1][0][0] == "GET"
#         assert (
#                 mock_request.call_args_list[1][1]["url"]
#                 == sidraclient.endpoint + Constants.URL_QUERY_GET_STATUS
#         )
#         assert len(mock_request.call_args_list[1][1]["params"]) == 3
#         assert mock_request.call_args_list[0][0][0] == "GET"
#         assert mock_request.call_args_list[0][1][
#                    "url"
#                ] == sidraclient.endpoint + Constants.URL_QUERY_GET_ID_FILTER.format(
#             TestConstants.IDENTITY
#         )
#         assert len(mock_request.call_args_list[0][1]["params"]) == 4


# def test_query_get_file_columns_fail(sidraclient):
#     with patch(
#             "requests.request",
#             side_effect=[
#                 Mock(
#                     status_code=200,
#                     text=json.dumps(
#                         {"pollingToken": "{}".format(TestConstants.POLLINGTOKEN)}
#                     ),
#                 ),
#                 Mock(
#                     status_code=200,
#                     text=json.dumps(
#                         {
#                             "executionStatus": {
#                                 "lifecycleState": "TERMINATED",
#                                 "resultState": "FAILED",
#                             },
#                             "sasToken": "FakeSasLink",
#                         }
#                     ),
#                 ),
#             ],
#     ) as mock_request:
#         sidraclient.Integration.Query._get_file(
#             idEntity=TestConstants.IDENTITY,
#             commaSeparatedColumns=TestConstants.COMMA_SEPARATED_COLUMNS,
#         )
#         assert mock_request.call_count == 2
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_QUERY_GET_STATUS
#         )
#         assert len(mock_request.call_args[1]["params"]) == 3
#         assert mock_request.call_args_list[0][0][0] == "GET"
#         assert mock_request.call_args_list[0][1][
#                    "url"
#                ] == sidraclient.endpoint + Constants.URL_QUERY_GET_ID_FILTER.format(
#             TestConstants.IDENTITY
#         )
#         assert len(mock_request.call_args_list[0][1]["params"]) == 4


# def test_query_get_file(sidraclient):
#     with patch(
#             "requests.request",
#             side_effect=[
#                 Mock(status_code=200, text=json.dumps(TestConstants.ATTRIBUTES_JSON)),
#                 Mock(
#                     status_code=200,
#                     text=json.dumps(
#                         {"pollingToken": "{}".format(TestConstants.POLLINGTOKEN)}
#                     ),
#                 ),
#                 Mock(
#                     status_code=200,
#                     text=json.dumps(
#                         {
#                             "executionStatus": {"lifecycleState": "TERMINATED"},
#                             "sasToken": "FakeSasLink",
#                         }
#                     ),
#                 ),
#             ],
#     ) as mock_request:
#         sidraclient.Integration.Query._get_file(idEntity=TestConstants.IDENTITY)
#         assert mock_request.call_count == 3
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_QUERY_GET_STATUS
#         )
#         assert len(mock_request.call_args[1]["params"]) == 3
#         assert mock_request.call_args_list[1][0][0] == "GET"
#         assert mock_request.call_args_list[1][1][
#                    "url"
#                ] == sidraclient.endpoint + Constants.URL_QUERY_GET_ID_FILTER.format(
#             TestConstants.IDENTITY
#         )
#         assert len(mock_request.call_args_list[1][1]["params"]) == 4
#         assert mock_request.call_args_list[0][0][0] == "GET"
#         assert mock_request.call_args_list[0][1][
#                    "url"
#                ] == sidraclient.endpoint + Constants.URL_ENTITIES_GET_ATTRIBUTES.format(
#             TestConstants.ID
#         )
#         assert len(mock_request.call_args_list[0][1]["params"]) == 1


# def test_query_load_file(sidraclient):
#     with patch(
#             "requests.request",
#             side_effect=[
#                 Mock(status_code=200, text=json.dumps(TestConstants.ATTRIBUTES_JSON))
#             ],
#     ) as mock_request:
#         with patch("pysidra.api.controllers.integration.query.pd.read_csv") as mock_pandas:
#             with patch(
#                     "pysidra.api.controllers.integration.query.pd.concat"
#             ) as mock_concat:
#                 sidraclient.Integration.Query.load_file(
#                     idEntity=TestConstants.IDENTITY, links=TestConstants.LINKS
#                 )
#                 assert mock_request.call_count == 1
#                 assert mock_request.call_args[0][0] == "GET"
#                 assert mock_request.call_args[1][
#                            "url"
#                        ] == sidraclient.endpoint + Constants.URL_ENTITIES_GET_ATTRIBUTES.format(
#                     TestConstants.ID
#                 )
#                 assert len(mock_request.call_args_list[0][1]["params"]) == 1
#                 assert mock_pandas.call_count == 2
#                 assert mock_concat.call_count == 1


# def test_query_download_file(sidraclient):
#     with patch(
#             "requests.request",
#             side_effect=[
#                 Mock(status_code=200, text=json.dumps(TestConstants.ATTRIBUTES_JSON)),
#                 Mock(
#                     status_code=200,
#                     text=json.dumps(
#                         {"pollingToken": "{}".format(TestConstants.POLLINGTOKEN)}
#                     ),
#                 ),
#                 Mock(status_code=204, content=io.BytesIO),
#                 Mock(status_code=200, content=io.BytesIO),
#             ],
#     ) as mock_request:
#         with patch("pysidra.api.controllers.integration.query.open") as mock_open:
#             sidraclient.Integration.Query.download_file(
#                 idEntity=TestConstants.IDENTITY, fileName=TestConstants.DIRECTORY
#             )
#             assert mock_open.call_count == 1
#             assert mock_request.call_args_list[0][0][0] == "GET"
#             assert mock_request.call_args_list[0][1][
#                        "url"
#                    ] == sidraclient.endpoint + Constants.URL_ENTITIES_GET_ATTRIBUTES.format(
#                 TestConstants.ID
#             )
#             assert len(mock_request.call_args_list[0][1]["params"]) == 1
#             assert mock_request.call_args_list[1][0][0] == "GET"
#             assert mock_request.call_args_list[1][1][
#                        "url"
#                    ] == sidraclient.endpoint + Constants.URL_QUERY_GET_ID_FILTER.format(
#                 TestConstants.IDENTITY
#             )
#             assert len(mock_request.call_args_list[1][1]["params"]) == 4
#             assert mock_request.call_args_list[2][0][0] == "GET"
#             assert (
#                     mock_request.call_args_list[2][1]["url"]
#                     == sidraclient.endpoint + Constants.URL_QUERY_GET_STREAM
#             )
#             assert len(mock_request.call_args_list[2][1]["params"]) == 2
#             assert mock_request.call_args_list[2][0][0] == "GET"
#             assert (
#                     mock_request.call_args_list[2][1]["url"]
#                     == sidraclient.endpoint + Constants.URL_QUERY_GET_STREAM
#             )
#             assert len(mock_request.call_args_list[2][1]["params"]) == 2


# # INTEGRATION/INFERENCE
# def test_inference_sql_query(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Integration.Inference.sql_query(
#             query=TestConstants.QUERY,
#             connectionString=TestConstants.CONNECTIONSTRING,
#             idProvider=TestConstants.IDPROVIDER,
#             idDataStorageUnit=TestConstants.IDDATASTORAGEUNIT,
#             store=TestConstants.STORE,
#         )
#         assert mock_request.call_args[0][0] == "POST"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_INFERENCE_SQL_QUERY
#         )
#         assert len(json.loads(mock_request.call_args[1]["data"])) == 5


# def test_inference_get_datatype(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Integration.Inference.get_datatype(fileUri=TestConstants.FILEURI)
#         assert mock_request.call_args[0][0] == "POST"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_INFERENCE_GET_DATATYPE
#         )
#         assert len(json.loads(mock_request.call_args[1]["data"])) == 2


# # MODELSERVING/MODEL
# def test_modelserving_model_get_list(sidraclient):
#     with patch("requests.request",
#                return_value=Mock(
#                    status_code=200,
#                    raise_for_status=lambda: None,
#                    text=TestConstants.EMPTY_PAGINATION_RESPONSE)) as mock_request:
#         sidraclient.ModelServing.Model.get_list()
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert mock_request.call_args[1]["url"] == sidraclient.endpoint \
#                + Constants.URL_MODELCONTROLLER_GET_LIST


# def test_modelserving_model_get_by_id(sidraclient):
#     with patch("requests.request") as mock_request:
#         resp = type("", (), {})()
#         resp.status_code = 200
#         resp.raise_for_status = lambda: None
#         resp.text = json.dumps(TestConstants.MODEL.__dict__)
#         mock_request.return_value = resp
#         sidraclient.ModelServing.Model.get_by_id(TestConstants.IDMODEL)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert mock_request.call_args[1]["url"] == \
#                sidraclient.endpoint + Constants.URL_MODELCONTROLLER_GET_BY_ID.format(TestConstants.IDMODEL)
#         assert len(mock_request.call_args[1]["params"]) == 1


# def test_modelserving_model_create(sidraclient):
#     with patch("requests.request") as mock_request:
#         resp = type("", (), {})()
#         resp.status_code = 200
#         resp.raise_for_status = lambda: None
#         resp.text = json.dumps(TestConstants.MODEL.__dict__)
#         mock_request.return_value = resp
#         sidraclient.ModelServing.Model.create(model=TestConstants.MODEL)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "POST"
#         assert mock_request.call_args[1]["url"] == sidraclient.endpoint + Constants.URL_MODELCONTROLLER_CREATE


# def test_modelserving_model_update(sidraclient):
#     with patch("requests.request") as mock_request:
#         resp = type("", (), {})()
#         resp.status_code = 200
#         resp.raise_for_status = lambda: None
#         resp.text = json.dumps(TestConstants.MODEL.__dict__)
#         mock_request.return_value = resp
#         sidraclient.ModelServing.Model.update(model=TestConstants.MODEL)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "PUT"
#         assert mock_request.call_args[1]["url"] == sidraclient.endpoint \
#                + Constants.URL_MODELCONTROLLER_UPDATE.format(TestConstants.MODEL.id)


# def test_modelserving_model_patch(sidraclient):
#     with patch("requests.request") as mock_request:
#         resp = type("", (), {})()
#         resp.status_code = 200
#         resp.raise_for_status = lambda: None
#         resp.text = json.dumps(TestConstants.MODEL.__dict__)
#         mock_request.return_value = resp
#         sidraclient.ModelServing.Model.patch(modelId=TestConstants.IDMODEL, dictAttributes=TestConstants.MODEL.__dict__)
#         assert mock_request.call_count == 2
#         assert mock_request.call_args_list[0][0][0] == "GET"
#         assert mock_request.call_args[0][0] == "PUT"
#         assert mock_request.call_args[1]["url"] == sidraclient.endpoint \
#                + Constants.URL_MODELCONTROLLER_UPDATE.format(TestConstants.MODEL.id)


# def test_modelserving_model_delete_async(sidraclient):
#     with patch("requests.request") as mock_request:
#         resp = type("", (), {})()
#         resp.status_code = 200
#         resp.raise_for_status = lambda: None
#         resp.text = "[]"
#         resp.ok = True
#         mock_request.return_value = resp
#         sidraclient.ModelServing.Model.delete_async(model=TestConstants.MODEL, datastorageunitId=TestConstants.IDDATASTORAGEUNIT)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "DELETE"
#         assert mock_request.call_args[1]["url"] == sidraclient.endpoint \
#                + Constants.URL_MODELCONTROLLER_DELETE_ASYNC.format(TestConstants.MODEL.id, TestConstants.IDDATASTORAGEUNIT)
#         assert len(mock_request.call_args[1]["params"]) == 2


# def test_modelserving_model_delete(sidraclient):
#     with patch("requests.request") as mock_request:
#         resp = type("", (), {})()
#         resp.status_code = 200
#         resp.raise_for_status = lambda: None
#         resp.text = "[]"
#         resp.ok = True
#         mock_request.return_value = resp
#         sidraclient.ModelServing.Model.delete(model=TestConstants.MODEL, datastorageunitId=TestConstants.IDDATASTORAGEUNIT)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "DELETE"
#         assert mock_request.call_args[1]["url"] == sidraclient.endpoint \
#                + Constants.URL_MODELCONTROLLER_DELETE_ASYNC.format(TestConstants.MODEL.id, TestConstants.IDDATASTORAGEUNIT)
#         assert len(mock_request.call_args[1]["params"]) == 2


# # MODELSERVING/MODELVERSION
# def test_modelserving_modelversion_get_list(sidraclient):
#     with patch("requests.request",
#                return_value=Mock(
#                    status_code=200,
#                    raise_for_status=lambda: None,
#                    text=TestConstants.MV_PAGINATION_RESPONSE)) as mock_request:
#         sidraclient.ModelServing.ModelVersion.get_list()
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert mock_request.call_args[1]["url"] == sidraclient.endpoint \
#                + Constants.URL_MODELVERSIONCONTROLLER_GET_LIST


# def test_modelserving_modelversion_get_by_id(sidraclient):
#     with patch("requests.request") as mock_request:
#         resp = type("", (), {})()
#         resp.status_code = 200
#         resp.raise_for_status = lambda: None
#         resp.text = json.dumps(TestConstants.MODELVERSION.__dict__)
#         mock_request.return_value = resp
#         sidraclient.ModelServing.ModelVersion.get_by_id(identifier=TestConstants.MODELVERSION.id)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert mock_request.call_args[1]["url"] == sidraclient.endpoint \
#                + Constants.URL_MODELVERSIONCONTROLLER_GET_BY_ID.format(TestConstants.MODELVERSION.id)
#         assert len(mock_request.call_args[1]["params"]) == 1


# def test_modelserving_modelversion_create(sidraclient):
#     with patch("requests.request") as mock_request:
#         resp = type("", (), {})()
#         resp.status_code = 200
#         resp.raise_for_status = lambda: None
#         resp.text = json.dumps(TestConstants.MODELVERSION.__dict__)
#         mock_request.return_value = resp
#         sidraclient.ModelServing.ModelVersion.create(modelVersion=TestConstants.MODELVERSION)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "POST"
#         assert mock_request.call_args[1]["url"] == sidraclient.endpoint + Constants.URL_MODELVERSIONCONTROLLER_CREATE


# def test_modelserving_modelversion_update(sidraclient):
#     with patch("requests.request") as mock_request:
#         resp = type("", (), {})()
#         resp.status_code = 200
#         resp.raise_for_status = lambda: None
#         resp.text = json.dumps(TestConstants.MODELVERSION.__dict__)
#         mock_request.return_value = resp
#         sidraclient.ModelServing.ModelVersion.update(modelVersion=TestConstants.MODELVERSION)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "PUT"
#         assert mock_request.call_args[1]["url"] == sidraclient.endpoint \
#                + Constants.URL_MODELVERSIONCONTROLLER_UPDATE.format(TestConstants.MODELVERSION.id)


# def test_modelserving_modelversion_patch(sidraclient):
#     with patch("requests.request") as mock_request:
#         resp = type("", (), {})()
#         resp.status_code = 200
#         resp.raise_for_status = lambda: None
#         resp.text = json.dumps(TestConstants.MODELVERSION.__dict__)
#         mock_request.return_value = resp
#         sidraclient.ModelServing.ModelVersion.patch(modelVersionId=TestConstants.IDMODELVERSION,
#                                                     dictAttributes=TestConstants.MODELVERSION.__dict__)
#         assert mock_request.call_count == 2
#         assert mock_request.call_args_list[0][0][0] == "GET"
#         assert mock_request.call_args[0][0] == "PUT"
#         assert mock_request.call_args[1]["url"] == sidraclient.endpoint \
#                + Constants.URL_MODELVERSIONCONTROLLER_UPDATE.format(TestConstants.MODELVERSION.id)


# def test_modelserving_modelversion_delete_async(sidraclient):
#     with patch("requests.request") as mock_request:
#         resp = type("", (), {})()
#         resp.status_code = 200
#         resp.raise_for_status = lambda: None
#         resp.text = TestConstants.RESPONSE_RUNID
#         resp.ok = True
#         mock_request.return_value = resp
#         sidraclient.ModelServing.ModelVersion.delete_async(modelVersion=TestConstants.MODELVERSION,
#                                                            datastorageunitId=TestConstants.IDDATASTORAGEUNIT)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "DELETE"
#         assert mock_request.call_args[1]["url"] == sidraclient.endpoint \
#                + Constants.URL_MODELVERSIONCONTROLLER_DELETE_ASYNC \
#                    .format(TestConstants.MODELVERSION.id, TestConstants.IDDATASTORAGEUNIT)
#         assert len(mock_request.call_args[1]["params"]) == 2


# def test_modelserving_modelversion_delete(sidraclient):
#     with patch("pysidra.api.controllers.modelserving.ModelVersionController.delete_async") as mock_async:
#         with patch("pysidra.api.controllers.modelserving.ModelVersionController.wait_for_job") as mock_wait_for_job:
#             mock_async.return_value = TestConstants.JOBRUNID
#             sidraclient.ModelServing.ModelVersion.delete(modelVersion=TestConstants.MODELVERSION,
#                                                          datastorageunitId=TestConstants.IDDATASTORAGEUNIT)
#             assert mock_async.call_count == 1
#             assert mock_wait_for_job.call_count == 1


# def test_modelserving_modelversion_create_image_async(sidraclient):
#     with patch("requests.request") as mock_request:
#         resp = type("", (), {})()
#         resp.status_code = 200
#         resp.raise_for_status = lambda: None
#         resp.text = TestConstants.RESPONSE_RUNID
#         mock_request.return_value = resp
#         request = CreateImageRequest(runId=TestConstants.RUNID, idModel=TestConstants.IDMODELVERSION)
#         sidraclient.ModelServing.ModelVersion.create_image_async(datastorageunitId=TestConstants.IDDATASTORAGEUNIT, request=request)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "POST"
#         assert mock_request.call_args[1]["url"] == sidraclient.endpoint \
#                + Constants.URL_MODELVERSIONCONTROLLER_CREATE_IMAGE_ASYNC.format(TestConstants.IDDATASTORAGEUNIT)


# def test_modelserving_modelversion_create_image(sidraclient):
#     with patch("pysidra.api.controllers.modelserving.ModelVersionController.create_image_async") as mock_async:
#         with patch("pysidra.api.controllers.modelserving.ModelVersionController.wait_for_job") as mock_wait_for_job:
#             with patch("pysidra.api.controllers.modelserving.ModelVersionController.job_status") as mock_job_status:
#                 with patch("pysidra.api.controllers.modelserving.ModelVersionController.get_by_id") as mock_get_by_id:
#                     mock_async.return_value = TestConstants.JOBRUNID
#                     job_status = TestConstants.JOBSTATUS_DICT.copy()
#                     job_status["metadata"]["task"]["notebook_task"]["base_parameters"]["modelVersionId"] \
#                         = TestConstants.IDMODELVERSION
#                     mock_job_status.return_value = job_status
#                     mock_get_by_id.return_value = TestConstants.MODELVERSION
#                     request = CreateImageRequest(runId=TestConstants.RUNID, idModel=TestConstants.IDMODELVERSION)
#                     sidraclient.ModelServing.ModelVersion.create_image(datastorageunitId=TestConstants.IDDATASTORAGEUNIT,
#                                                                        request=request)
#                     assert mock_async.call_count == 1
#                     assert mock_wait_for_job.call_count == 1
#                     assert mock_job_status.call_count == 1
#                     assert mock_get_by_id.call_count == 1


# def test_modelserving_modelversion_deploy_async_by_runid(sidraclient):
#     with patch("requests.request") as mock_request:
#         resp = type("", (), {})()
#         resp.status_code = 200
#         resp.raise_for_status = lambda: None
#         resp.text = TestConstants.RESPONSE_RUNID
#         mock_request.return_value = resp
#         request = DeployRequest(runId=TestConstants.RUNID)
#         sidraclient.ModelServing.ModelVersion.deploy_async(datastorageunitId=TestConstants.IDDATASTORAGEUNIT, request=request)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "POST"
#         assert mock_request.call_args[1]["url"] == sidraclient.endpoint \
#                + Constants.URL_MODELVERSIONCONTROLLER_DEPLOY_ASYNC.format(TestConstants.IDDATASTORAGEUNIT)


# def test_modelserving_modelversion_deploy_by_runid(sidraclient):
#     with patch("pysidra.api.controllers.modelserving.ModelVersionController.deploy_async") as mock_async:
#         with patch("pysidra.api.controllers.modelserving.ModelVersionController.wait_for_job") as mock_wait_for_job:
#             with patch("pysidra.api.controllers.modelserving.ModelVersionController.job_status") as mock_job_status:
#                 with patch("pysidra.api.controllers.modelserving.ModelVersionController.get_by_id") as mock_get_by_id:
#                     mock_async.return_value = TestConstants.JOBRUNID
#                     job_status = TestConstants.JOBSTATUS_DICT.copy()
#                     job_status["metadata"]["task"]["notebook_task"]["base_parameters"]["modelVersionId"] \
#                         = TestConstants.IDMODELVERSION
#                     mock_job_status.return_value = job_status
#                     mock_get_by_id.return_value = TestConstants.MODELVERSION
#                     request = DeployRequest(runId=TestConstants.RUNID)
#                     sidraclient.ModelServing.ModelVersion.deploy(datastorageunitId=TestConstants.IDDATASTORAGEUNIT, request=request)
#                     assert mock_async.call_count == 1
#                     assert mock_wait_for_job.call_count == 1
#                     assert mock_job_status.call_count == 1
#                     assert mock_get_by_id.call_count == 1


# def test_modelserving_modelversion_deploy_async_by_modelversionid(sidraclient):
#     with patch("requests.request") as mock_request:
#         resp = type("", (), {})()
#         resp.status_code = 200
#         resp.raise_for_status = lambda: None
#         resp.text = TestConstants.RESPONSE_RUNID
#         mock_request.return_value = resp
#         request = DeployRequest(modelVersionId=TestConstants.IDMODELVERSION)
#         sidraclient.ModelServing.ModelVersion.deploy_async(datastorageunitId=TestConstants.IDDATASTORAGEUNIT, request=request)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "POST"
#         assert mock_request.call_args[1]["url"] == sidraclient.endpoint \
#                + Constants.URL_MODELVERSIONCONTROLLER_DEPLOY_ASYNC.format(TestConstants.IDDATASTORAGEUNIT)


# def test_modelserving_modelversion_deploy_by_modelversionid(sidraclient):
#     with patch("pysidra.api.controllers.modelserving.ModelVersionController.deploy_async") as mock_async:
#         with patch("pysidra.api.controllers.modelserving.ModelVersionController.wait_for_job") as mock_wait_for_job:
#             with patch("pysidra.api.controllers.modelserving.ModelVersionController.job_status") as mock_job_status:
#                 with patch("pysidra.api.controllers.modelserving.ModelVersionController.get_by_id") as mock_get_by_id:
#                     mock_async.return_value = TestConstants.JOBRUNID
#                     job_status = TestConstants.JOBSTATUS_DICT.copy()
#                     job_status["metadata"]["task"]["notebook_task"]["base_parameters"]["modelVersionId"] \
#                         = TestConstants.IDMODELVERSION
#                     mock_job_status.return_value = job_status
#                     mock_get_by_id.return_value = TestConstants.MODELVERSION
#                     request = DeployRequest(modelVersionId=TestConstants.IDMODELVERSION)
#                     sidraclient.ModelServing.ModelVersion.deploy(datastorageunitId=TestConstants.IDDATASTORAGEUNIT, request=request)
#                     assert mock_async.call_count == 1
#                     assert mock_wait_for_job.call_count == 1
#                     assert mock_job_status.call_count == 1
#                     assert mock_get_by_id.call_count == 1


# def test_modelserving_modelversion_undeploy_async(sidraclient):
#     with patch("requests.request") as mock_request:
#         resp = type("", (), {})()
#         resp.status_code = 200
#         resp.raise_for_status = lambda: None
#         resp.text = TestConstants.RESPONSE_RUNID
#         mock_request.return_value = resp
#         sidraclient.ModelServing.ModelVersion.undeploy_async(modelVersion=TestConstants.MODELVERSION,
#                                                              datastorageunitId=TestConstants.IDDATASTORAGEUNIT)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "POST"
#         assert mock_request.call_args[1]["url"] == sidraclient.endpoint \
#                + Constants.URL_MODELVERSIONCONTROLLER_UNDEPLOY_ASYNC \
#                    .format(TestConstants.IDMODELVERSION, TestConstants.IDDATASTORAGEUNIT)


# def test_modelserving_modelversion_undeploy(sidraclient):
#     with patch("pysidra.api.controllers.modelserving.ModelVersionController.undeploy_async") as mock_async:
#         with patch("pysidra.api.controllers.modelserving.ModelVersionController.wait_for_job") as mock_wait_for_job:
#             mock_async.return_value = TestConstants.JOBRUNID
#             job_status = TestConstants.JOBSTATUS_DICT.copy()
#             job_status["metadata"]["task"]["notebook_task"]["base_parameters"]["modelVersionId"] \
#                 = TestConstants.IDMODELVERSION
#             sidraclient.ModelServing.ModelVersion.undeploy(modelVersion=TestConstants.MODELVERSION,
#                                                            datastorageunitId=TestConstants.IDDATASTORAGEUNIT)
#             assert mock_async.call_count == 1
#             assert mock_wait_for_job.call_count == 1


# def test_modelserving_modelversion_inference_async(sidraclient):
#     with patch("requests.request") as mock_request:
#         resp = type("", (), {})()
#         resp.status_code = 200
#         resp.raise_for_status = lambda: None
#         resp.text = TestConstants.RESPONSE_RUNID
#         mock_request.return_value = resp
#         request = InferenceRequest(runId=TestConstants.RUNID)
#         sidraclient.ModelServing.ModelVersion.inference_async(modelVersionId=TestConstants.IDMODELVERSION,
#                                                               datastorageunitId=TestConstants.IDDATASTORAGEUNIT, request=request)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "POST"
#         assert mock_request.call_args[1]["url"] == sidraclient.endpoint \
#                + Constants.URL_MODELVERSIONCONTROLLER_INFERENCE_ASYNC \
#                    .format(TestConstants.IDMODELVERSION, TestConstants.IDDATASTORAGEUNIT)


# def test_modelserving_modelversion_inference(sidraclient):
#     with patch("pysidra.api.controllers.modelserving.ModelVersionController.inference_async") as mock_async:
#         with patch("pysidra.api.controllers.modelserving.ModelVersionController.wait_for_job") as mock_wait_for_job:
#             mock_async.return_value = TestConstants.JOBRUNID
#             job_status = TestConstants.JOBSTATUS_DICT.copy()
#             job_status["metadata"]["task"]["notebook_task"]["base_parameters"]["modelVersionId"] \
#                 = TestConstants.IDMODELVERSION
#             request = InferenceRequest(runId=TestConstants.RUNID)
#             sidraclient.ModelServing.ModelVersion.inference(modelVersionId=TestConstants.IDMODELVERSION,
#                                                             datastorageunitId=TestConstants.IDDATASTORAGEUNIT, request=request)
#             assert mock_async.call_count == 1
#             assert mock_wait_for_job.call_count == 1


# def test_modelserving_modelversion_job_status(sidraclient):
#     with patch("requests.request") as mock_request:
#         resp = type("", (), {})()
#         resp.status_code = 200
#         resp.raise_for_status = lambda: None
#         resp.text = json.dumps(TestConstants.JOBSTATUS_DICT)
#         mock_request.return_value = resp
#         sidraclient.ModelServing.ModelVersion.job_status(datastorageunitId=TestConstants.IDDATASTORAGEUNIT,
#                                                          jobRunId=TestConstants.JOBRUNID)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert mock_request.call_args[1]["url"] == sidraclient.endpoint \
#                + Constants.URL_MODELVERSIONCONTROLLER_JOB_STATUS \
#                    .format(TestConstants.FAKE_MODELVERSION_ID, TestConstants.IDDATASTORAGEUNIT, TestConstants.JOBRUNID)

# # DATACATALOG / STORAGES

# def test_datacatalog_storages_get_list(sidraclient):
#     with patch("requests.request",
#                return_value=Mock(
#                    status_code=200,
#                    raise_for_status=lambda: None,
#                    text=TestConstants.EMPTY_PAGINATION_RESPONSE)
#                ) as mock_request:
#         sidraclient.Datacatalog.Storages.get_list()
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_STORAGES_GET_LIST
#         )


# def test_datacatalog_storages_get_by_id(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Datacatalog.Storages.get_by_id(TestConstants.ID)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert mock_request.call_args[1][
#                    "url"
#                ] == sidraclient.endpoint + Constants.URL_STORAGES_GET_BY_ID.format(
#             TestConstants.ID
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1

# # DATACATALOG / STORAGEROLES

# def test_datacatalog_storageroles_get_list(sidraclient):
#     with patch("requests.request",
#                return_value=Mock(
#                    status_code=200,
#                    raise_for_status=lambda: None,
#                    text=TestConstants.EMPTY_PAGINATION_RESPONSE)
#                ) as mock_request:
#         sidraclient.Datacatalog.StorageRoles.get_list()
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert (
#                 mock_request.call_args[1]["url"]
#                 == sidraclient.endpoint + Constants.URL_STORAGEROLES_GET_LIST
#         )


# def test_datacatalog_storageroles_get_by_id(sidraclient):
#     with patch("requests.request") as mock_request:
#         sidraclient.Datacatalog.StorageRoles.get_by_id(TestConstants.ID)
#         assert mock_request.call_count == 1
#         assert mock_request.call_args[0][0] == "GET"
#         assert mock_request.call_args[1][
#                    "url"
#                ] == sidraclient.endpoint + Constants.URL_STORAGEROLES_GET_BY_ID.format(
#             TestConstants.ID
#         )
#         assert len(mock_request.call_args[1]["params"]) == 1