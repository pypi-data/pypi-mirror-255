import unittest
import sidraconnector.sdk.constants as Constants
from sidraconnector.sdk.log.logging import Logger
from sidraconnector.sdk.metadata.assetservice import AssetService
from sidraconnector.sdk.metadata.entityservice import EntityService
from sidraconnector.sdk.metadata.providerservice import ProviderService
from sidraconnector.sdk.metadata.models import *
from sidraconnector.sdk.api.sidra.core.utils import Utils as CoreApiUtils
import SidraCoreApiPythonClient
from test.fixture import Fixture
import xmlrunner
from parameterized import parameterized, parameterized_class
from datetime import datetime, timedelta
from sidraconnector.sdk.metadata.models.builders import *
from test.common import Common
from test.utils import Utils as TestUtils
from pyspark.sql import SparkSession


class TestMetadataService(unittest.TestCase):
  _spark = SparkSession.builder.getOrCreate()
  _logger = Logger(_spark, 'Test_DSUIngestion_E2E')
  _logger.set_level('DEBUG')
  _description = "test for metadata service"
  _storage_container = 'dsuingestiontestmetadataservice'
  _fixture = Fixture(_spark, _logger, _storage_container)
  

  @classmethod 
  def tearDown(self):
    self._fixture.cleanup()   

  # Test functions should start with 'test' to be discovered by unittest
  def test_should_get_provider_info_when_get_provider(self):
    # Arrange
    given_provider = self._fixture.create_default_provider(self._description)

    # Act
    service = ProviderService(self._spark)
    provider_model = service.get_provider_model(given_provider.id)
        
    # Assert
    self.assertEqual(provider_model.id, given_provider.id)
    self.assertEqual(provider_model.database_name, given_provider.database_name)   
    
  def test_should_get_entity_with_attributes_when_get_entity(self):
    # Arrange
    given_provider = self._fixture.create_default_provider(self._description)
    
    load_properties = LoadPropertiesBuilder().with_data_preview(True).with_pii_detection(True).build()
    attributes = Common.initialize_attributes()
    suffix = self._fixture.get_suffix()
    table_name = f"TestMetadataService{suffix}"
    entity_name = f"TestMetadataService{suffix}"  
    entity = EntityBuilder().with_name(entity_name).with_table_name(table_name).with_id_provider(given_provider.id).with_load_properties(load_properties).with_attributes(attributes).build()
    given_entity = self._fixture.create_entity(entity)
    
    # Act
    service = EntityService(self._spark)
    entity_model = service.get_entity_model_with_attribute_and_attribute_format(given_entity.id)
        
    # Assert
    self.assertEqual(entity_model.id, given_entity.id)
    self.assertEqual(entity_model.id_provider, given_entity.id_provider)
    self.assertEqual(entity_model.table_name, given_entity.table_name)
    self.assertEqual(entity_model.load_properties.generate_delta_table, given_entity.generate_delta_table)
    self.assertEqual(entity_model.load_properties.id_table_format, given_entity.id_table_format)
    self.assertEqual(entity_model.reader_properties.file_format, given_entity.format)
    self.assertEqual(entity_model.load_properties.consolidation_mode, 'Snapshot')
    self.assertEqual(entity_model.load_properties.data_preview, True)
    self.assertEqual(entity_model.load_properties.pii_detection, True)
    self.assertEqual(entity_model.load_properties.pii_detection_language, 'en')
    self.assertEqual(entity_model.load_properties.has_encryption, False)
    self.assertEqual(len(entity_model.attributes), len(attributes))
    self.assertEqual(entity_model.attributes[0].name, Constants.ATTRIBUTE_NAME_LOAD_DATE)
    self.assertEqual(entity_model.attributes[0].order, 1)
    self.assertEqual(entity_model.attributes[0].is_primary_key, False)
    self.assertEqual(entity_model.attributes[0].is_calculated, True)
    self.assertEqual(entity_model.attributes[0].is_partition_column, False)
    self.assertEqual(entity_model.attributes[0].is_metadata, True)
    self.assertEqual(entity_model.attributes[0].databricks_type, 'TIMESTAMP')
    self.assertEqual(entity_model.attributes[0].load_properties.special_format, "CURRENT_TIMESTAMP()")
    
  def test_should_not_fail_when_get_entity_without_additional_properties(self):
    # Arrange
    given_provider = self._fixture.create_default_provider(self._description)
   
    reader_properties = ReaderPropertiesBuilder().with_reader_options(None).build()
    load_properties = LoadPropertiesBuilder().with_consolidation_mode(None).with_data_preview(None).with_pii_detection(None).with_pii_detection_language(None).with_has_encryption(None).build()
    suffix = self._fixture.get_suffix()
    table_name = f"TestMetadataService{suffix}"
    entity_name = f"TestMetadataService{suffix}"  
    entity = EntityBuilder().with_name(entity_name).with_table_name(table_name).with_id_provider(given_provider.id).with_load_properties(load_properties).with_reader_properties(reader_properties).build()
    given_entity = self._fixture.create_entity(entity)
    self.assertEqual(given_entity.additional_properties, '{}')
        
    # Act
    service = EntityService(self._spark)
    entity = service.get_entity_model_with_attribute_and_attribute_format(given_entity.id)
        
    # Assert
    expected_consolidation_mode = 'Snapshot'
    expected_data_preview = True
    expected_pii_detection = False
    expected_pii_detection_language = 'en'           
    self.assertEqual(entity.load_properties.consolidation_mode, expected_consolidation_mode)
    self.assertEqual(entity.load_properties.data_preview, expected_data_preview)
    self.assertEqual(entity.load_properties.pii_detection, expected_pii_detection)
    self.assertEqual(entity.load_properties.pii_detection_language, expected_pii_detection_language)      

  def test_should_register_an_asset_and_update_its_info(self):
    # Arrange
    source_file = 'files/countries.parquet'
    
    given_provider = self._fixture.create_default_provider("Metadata Service Test")

    suffix_entity = self._fixture.get_suffix()  
    table_name = f"TestMetadataService{suffix_entity}"
    entity_name = f"TestMetadataService{suffix_entity}"  
    entity = EntityBuilder().with_id_provider(given_provider.id).with_name(table_name).with_table_name(table_name).with_regular_expression('countries_((?<year>\d{4})(?<month>\d{2})(?<day>\d{2})).parquet').build()
    given_entity = self._fixture.create_entity(entity)

    current_date = datetime.now()
    suffix_file = current_date.strftime('%Y%m%d')
    date_path = current_date.strftime('%Y/%m/%d')
    destination_file = f'{given_entity.provider_name}/{given_entity.name}/countries_{suffix_file}.parquet'
    self._fixture.move_file_to_execution_storage(source_file, destination_file)
    
    asset_uri = self._fixture._storage_fixture.get_destination_file_absolute_uri(destination_file)
    service = AssetService(self._spark)
    
    # Act
    actual = service.register_asset(asset_uri)

    # Assert
    self.assertEqual(actual.source_uri, asset_uri)
    expected_destination_uri = f'https://{self._fixture._storage_fixture.destination_storage_account}.blob.core.windows.net/{given_provider.database_name}/{given_entity.name}/{date_path}/countries_{suffix_file}_id{actual.asset_id}.parquet'
    self.assertEqual(actual.destination_uri, expected_destination_uri)
    
    # Arrange
    # The destination file should exist to update the information of the asset and it is not done yet then we simulate the destionation_uri
    actual.destination_uri = actual.source_uri  
    
    # Act
    result = service.register_info(actual)

    # Assert
    self.assertEqual(actual.asset_id, result.requested_parameters['assetId'])
    
    # Arrange
    entities_count = 1024
    
    # Act
    service.update_asset_loaded(actual.asset_id, entities_count)
    
    # Assert
    actual_asset = service.get_asset(actual.asset_id)
    self.assertEqual(actual_asset.entities, entities_count)
    self.assertEqual(actual_asset.id_status, 2)    
    
  @parameterized.expand([
    (None,)
    ,("",)
  ])
  def test_should_not_fail_when_get_entity_with_null_or_empty_additional_properties_field(self, additional_properties):
    # Arrange
    given_provider = self._fixture.create_default_provider(self._description)
    entity = EntityBuilder().with_id_provider(given_provider.id).with_name("my_table").with_table_name("my_table").with_regular_expression("^file.parquet").with_additional_properties(additional_properties).build()

    service = EntityService(self._spark)
    entity_response = service.create_or_get_entity(entity)
    self._fixture._entities.append(entity_response)
              
    # Act
    entity = service.get_entity_model_with_attribute_and_attribute_format(entity_response.id)
        
    # Assert    
    self.assertEqual(entity.load_properties.consolidation_mode, Constants.DEFAULT_CONSOLIDATION_MODE)
    self.assertEqual(entity.load_properties.data_preview, Constants.DEFAULT_DATA_PREVIEW)
    self.assertEqual(entity.load_properties.pii_detection, Constants.DEFAULT_PII_DETECTION)
    self.assertEqual(entity.load_properties.pii_detection_language, Constants.DEFAULT_PII_DETECTION_LANGUAGE)    
    self.assertEqual(entity.reader_properties.reader_options, {})        
    
  @parameterized.expand([
    ('{"dataPreview": true, "isPIIDetectionEnabled": true}', True)
    ,('{"dataPreview": "True", "isPIIDetectionEnabled": "true"}', True)
    ,('{"dataPreview": false, "isPIIDetectionEnabled": false}', False)
    ,('{"dataPreview": "False", "isPIIDetectionEnabled": "false"}', False)
  ])
  def test_should_load_correctly_boolean_fields_from_additional_properties(self, additional_properties, expected_result):
    # Arrange
    given_provider = self._fixture.create_default_provider(self._description)
     
    entity_dto = {
      "idProvider": given_provider.id,
      "name": "my_table",
      "tableName": "my_table",    
      "description": None,
      "regularExpression": "^file.parquet",
      "startValidDate": "2022-07-04T16:09:42.513Z",
      "endValidDate": None,
      "serde": None,
      "serdeProperties": None,
      "encoding": None,
      "headerLines": 0,
      "fieldDelimiter": None,
      "idTableFormat": None,
      "nullText": "string",
      "format": "parquet",
      "reCreateTableOnDeployment": True,
      "filesPerDrop": 1,
      "rowDelimiter": None,
      "sourcePath": "[schema].[my_table]",
      "generateDeltaTable": False,
      "lastUpdated": "2022-07-04T16:09:42.513Z",
      "lastDeployed": None,
      "additionalProperties": additional_properties,  
    }
    sidra_core_api_client = CoreApiUtils(self._spark).get_SidraCoreApiClient()
    metadata_entity_api_instance = SidraCoreApiPythonClient.MetadataEntitiesEntityApi(sidra_core_api_client)
    entity_response =  metadata_entity_api_instance.api_metadata_entities_post(body=entity_dto)
    self._fixture._entities.append(entity_response)

    service = EntityService(self._spark)
                 
    # Act
    entity = service.get_entity_model_with_attribute_and_attribute_format(entity_response.id)
        
    # Assert    
    self.assertEqual(entity.load_properties.data_preview, expected_result)
    self.assertEqual(entity.load_properties.pii_detection, expected_result)

def run_tests():

  loader = unittest.TestLoader()
  suite  = unittest.TestSuite()

  # add tests to the test suite
  suite.addTests(loader.loadTestsFromTestCase(testCaseClass=TestMetadataService))

  # initialize a runner, pass it your suite and run it
  runner = xmlrunner.XMLTestRunner(verbosity=3, descriptions=True, output='/dbfs/runtests/MetadataService_Report')
  result = runner.run(suite)

  # print chart
  TestUtils.print_pie_chart_tests(succeed=len(result.successes), failed=len(result.failures), errors=len(result.errors), skipped=len(result.skipped))

  # ensure job failed if there are issues
  assert len(result.failures) == 0
  assert len(result.errors) == 0
