# from pysidra.api.models.modelserving import Model, ModelVersion


# class TestConstants:
#     EMPTY_PAGINATION_RESPONSE = "{\"totalItems\":0, \"items\":[]}"
#     MV_PAGINATION_RESPONSE = '{"totalItems":1, "items":[{"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6", ' \
#                              '"model": {}, "idModel": "3fa85f64-5717-4562-b3fc-2c963f66afa6",' \
#                              '"experimentId": "exp_id","runId": "run_id","versionNumber": 0,"metrics": "{}",' \
#                              '"lastTrained": "2020-04-09T09:50:51.506Z","imageName": "im_name",' \
#                              '"deploymentName": "dep_name","endPoint": "url","status": 0,"enabled": true,' \
#                              '"notes": "{}"}]}'
#     PROVIDERS_IDS = [1, 2, 3]
#     SKIP = 1
#     ID = 1
#     PROVIDERS_ID = 1
#     OFFSET_ID = 1
#     DAILY_MEASURE = "validationErrors"
#     IDENTITY = 1
#     COMMA_SEPARATED_COLUMNS = "col1,col2,col3"
#     LAST_EXPORTED_ASSET_IDS = [1, 2, 3]
#     COMMA_SEPARATED_FILTER_COLUMNS = "col1,col2,col3"
#     DATABASE_NAME = "test_database"
#     TABLE_NAME = "test_table"
#     POLLINGTOKEN = 1
#     ENDPOINT = "test_endpoint"
#     TOKEN = "test_token"
#     FAIL_TOKEN = "fail_test_token"
#     BASE_URL = "test_base_url"
#     FAIL_BASE_URL = "fail_test_base_url"
#     SCOPE = "test_scope"
#     CLIENT_ID = "test_client_id"
#     CLIENT_SECRET = "test_client_secret"
#     AUTH_PARAMS = (
#         ("POST",),
#         {
#             "data":{'grant_type': 'client_credentials', 'scope': SCOPE,  'client_id': CLIENT_ID,  'client_secret': CLIENT_SECRET },
#             "headers": {"Content-Type": "application/x-www-form-urlencoded"},
#             "params": {"api-version": "1.0"},
#             "url": "{}".format(BASE_URL),
#         },
#     )
#     QUERY = "SELECT * FROM [DataIngestion].[Pipeline]"
#     CONNECTIONSTRING = "Data Source=Data_Source;Initial Catalog=Initial_Catalog;Persist Security Info=False;User ID=User_ID;Password=Password;Pooling=False;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=60"
#     IDPROVIDER = 1
#     IDDATASTORAGEUNIT = 1
#     STORE = "False"
#     FILEURI = "fileUri"
#     ATTRIBUTES_JSON = [
#         {
#             "id": 90,
#             "sqlType": "uniqueidentifier",
#             "isMetadata": "false",
#             "isPartitionColumn": "false",
#             "isCalculated": "false",
#             "order": 1,
#             "isPrimaryKey": "true",
#             "treatEmptyAsNull": "false",
#             "specialFormat": "null",
#             "replacementText": "null",
#             "replacedText": "null",
#             "removeQuotes": "false",
#             "needTrim": "true",
#             "isNullable": "false",
#             "maxLen": "null",
#             "hiveType": "STRING",
#             "name": "CrmId",
#             "idEntity": 11,
#             "validationText": "null",
#             "description": "null",
#             "sourceName": "null",
#         },
#         {
#             "id": 91,
#             "sqlType": "nvarchar",
#             "isMetadata": "false",
#             "isPartitionColumn": "false",
#             "isCalculated": "false",
#             "order": 2,
#             "isPrimaryKey": "false",
#             "treatEmptyAsNull": "false",
#             "specialFormat": "null",
#             "replacementText": "null",
#             "replacedText": "null",
#             "removeQuotes": "false",
#             "needTrim": "true",
#             "isNullable": "true",
#             "maxLen": 50,
#             "hiveType": "STRING",
#             "name": "Name",
#             "idEntity": 11,
#             "validationText": "null",
#             "description": "null",
#             "sourceName": "null",
#         },
#         {
#             "id": 92,
#             "sqlType": "nvarchar",
#             "isMetadata": "false",
#             "isPartitionColumn": "false",
#             "isCalculated": "false",
#             "order": 3,
#             "isPrimaryKey": "false",
#             "treatEmptyAsNull": "false",
#             "specialFormat": "null",
#             "replacementText": "null",
#             "replacedText": "null",
#             "removeQuotes": "false",
#             "needTrim": "true",
#             "isNullable": "true",
#             "maxLen": 10,
#             "hiveType": "STRING",
#             "name": "CurrencySymbol",
#             "idEntity": 11,
#             "validationText": "null",
#             "description": "null",
#             "sourceName": "null",
#         },
#         {
#             "id": 93,
#             "sqlType": "decimal(10,5)",
#             "isMetadata": "false",
#             "isPartitionColumn": "false",
#             "isCalculated": "false",
#             "order": 4,
#             "isPrimaryKey": "false",
#             "treatEmptyAsNull": "false",
#             "specialFormat": "null",
#             "replacementText": "null",
#             "replacedText": "null",
#             "removeQuotes": "false",
#             "needTrim": "false",
#             "isNullable": "false",
#             "maxLen": "null",
#             "hiveType": "decimal(10,5)",
#             "name": "ExchangeRate",
#             "idEntity": 11,
#             "validationText": "null",
#             "description": "null",
#             "sourceName": "null",
#         },
#         {
#             "id": 94,
#             "sqlType": "INT",
#             "isMetadata": "true",
#             "isPartitionColumn": "false",
#             "isCalculated": "true",
#             "order": 5,
#             "isPrimaryKey": "false",
#             "treatEmptyAsNull": "false",
#             "specialFormat": "BLOCK__OFFSET__INSIDE__FILE",
#             "replacementText": "null",
#             "replacedText": "null",
#             "removeQuotes": "false",
#             "needTrim": "false",
#             "isNullable": "false",
#             "maxLen": "null",
#             "hiveType": "INT",
#             "name": "SourceByteOffset",
#             "idEntity": 11,
#             "validationText": "null",
#             "description": "null",
#             "sourceName": "null",
#         },
#         {
#             "id": 95,
#             "sqlType": "DATETIME2",
#             "isMetadata": "true",
#             "isPartitionColumn": "false",
#             "isCalculated": "true",
#             "order": 6,
#             "isPrimaryKey": "false",
#             "treatEmptyAsNull": "false",
#             "specialFormat": "CURRENT_TIMESTAMP()",
#             "replacementText": "null",
#             "replacedText": "null",
#             "removeQuotes": "false",
#             "needTrim": "false",
#             "isNullable": "false",
#             "maxLen": "null",
#             "hiveType": "STRING",
#             "name": "SidraLoadDate",
#             "idEntity": 11,
#             "validationText": "null",
#             "description": "null",
#             "sourceName": "null",
#         },
#         {
#             "id": 96,
#             "sqlType": "BIT",
#             "isMetadata": "true",
#             "isPartitionColumn": "false",
#             "isCalculated": "true",
#             "order": 7,
#             "isPrimaryKey": "false",
#             "treatEmptyAsNull": "false",
#             "specialFormat": "FALSE",
#             "replacementText": "null",
#             "replacedText": "null",
#             "removeQuotes": "false",
#             "needTrim": "false",
#             "isNullable": "false",
#             "maxLen": "null",
#             "hiveType": "BOOLEAN",
#             "name": "SidraPassedValidation",
#             "idEntity": 11,
#             "validationText": "null",
#             "description": "null",
#             "sourceName": "null",
#         },
#         {
#             "id": 97,
#             "sqlType": "DATE",
#             "isMetadata": "true",
#             "isPartitionColumn": "true",
#             "isCalculated": "true",
#             "order": 8,
#             "isPrimaryKey": "false",
#             "treatEmptyAsNull": "false",
#             "specialFormat": "SidraFileDate",
#             "replacementText": "null",
#             "replacedText": "null",
#             "removeQuotes": "false",
#             "needTrim": "false",
#             "isNullable": "false",
#             "maxLen": "null",
#             "hiveType": "DATE",
#             "name": "SidraFileDate",
#             "idEntity": 11,
#             "validationText": "null",
#             "description": "null",
#             "sourceName": "null",
#         },
#         {
#             "id": 98,
#             "sqlType": "INT",
#             "isMetadata": "true",
#             "isPartitionColumn": "true",
#             "isCalculated": "true",
#             "order": 9,
#             "isPrimaryKey": "false",
#             "treatEmptyAsNull": "false",
#             "specialFormat": "SidraIdAsset",
#             "replacementText": "null",
#             "replacedText": "null",
#             "removeQuotes": "false",
#             "needTrim": "false",
#             "isNullable": "false",
#             "maxLen": "null",
#             "hiveType": "INT",
#             "name": "SidraIdAsset",
#             "idEntity": 11,
#             "validationText": "null",
#             "description": "null",
#             "sourceName": "null",
#         },
#     ]
#     LINKS = ["link1", "link2"]
#     DIRECTORY = "test_directory"
#     # Model
#     IDMODEL = '4b004c64-fe47-46e9-9d95-d579f1e05a4f'
#     MODEL = Model(**{
#         "id": IDMODEL,
#         "name": "Model name",
#         "description": "Description"
#     })
#     # ModelVersion
#     FAKE_MODELVERSION_ID = '00000000-0000-0000-0000-000000000000'
#     IDMODELVERSION = '9215787c-66a4-4108-9fae-806552c310fb'
#     EXPERIMENTID = "1234567890"
#     RUNID = "1234567890abcdefghijklmn"
#     MODELVERSION = ModelVersion(**{
#         "id": IDMODELVERSION,
#         "idModel": IDMODEL,
#         "experimentId": EXPERIMENTID,
#         "runId": RUNID
#     })
#     JOBRUNID = 1234
#     RESPONSE_RUNID = "{\"run_id\": 1234}"
#     JOBSTATUS_DICT = {"metadata": {
#                         "job_id": 0,
#                         "run_id": 0,
#                         "state": {
#                           "life_cycle_state": 0,
#                           "result_state": 0,
#                           "state_message": "message"
#                         },
#                         "task": {
#                           "notebook_task": {
#                             "notebook_path": "path",
#                             "base_parameters": {}
#                           }
#                         }
#                       },
#                       "notebook_output": {
#                         "result": "",
#                         "truncated": True
#                       },
#                       "error": ""
#                     }
