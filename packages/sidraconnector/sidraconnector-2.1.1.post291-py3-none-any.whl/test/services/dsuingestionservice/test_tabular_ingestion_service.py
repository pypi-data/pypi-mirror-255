import unittest
import xmlrunner
from parameterized import parameterized, parameterized_class
from sidraconnector.sdk.metadata.models.builders import AttributeBuilder, EntityBuilder, ProviderBuilder, LoadPropertiesBuilder, AttributeLoadPropertiesBuilder
from sidraconnector.sdk.databricks.dsuingestion.models.fielddefinition import FieldDefinition
from sidraconnector.sdk.databricks.dsuingestion.tabularingestionservice import TabularIngestionService
from sidraconnector.sdk.storage.utils import Utils as StorageUtils
from sidraconnector.sdk.log.logging import Logger
import sidraconnector.sdk.constants as Constants
from test.utils import Utils as TestUtils
from pyspark.sql import SparkSession

class TestTabularIngestionService(unittest.TestCase):
  _spark = SparkSession.builder.getOrCreate()
  _logger = Logger(_spark, 'Test_DSUIngestion_E2E')   
  _logger.set_level('DEBUG')

  def _assert_are_equals_field_definition(self, actual_field_definitions, expected_field_definitions):
    self.assertEqual(len(actual_field_definitions), len(expected_field_definitions))
    for index in range(len(actual_field_definitions)):
      self.assertEqual(actual_field_definitions[index].name, expected_field_definitions[index].name)
      self.assertEqual(actual_field_definitions[index].expression, expected_field_definitions[index].expression)
      self.assertEqual(actual_field_definitions[index].type, expected_field_definitions[index].type)

  def test_should_get_non_calculated_attribute_names(self):
    # Arrange
    attribute1 = AttributeBuilder().with_name('Attribute1').with_order(1).with_is_primary_key(True).build()
    attribute2 = AttributeBuilder().with_name('Attribute2').with_order(2).with_is_calculated(True).build()
    attribute3 = AttributeBuilder().with_name('Attribute3').with_order(3).with_is_partition_column(True).build()
    attribute4 = AttributeBuilder().with_name('Attribute4').with_order(4).with_is_calculated(True).with_is_partition_column(True).build()
    attributes = [attribute1, attribute2, attribute3, attribute4]
    entity = EntityBuilder().with_attributes(attributes).build()
    service = TabularIngestionService(self._spark, self._logger, 'asset_uri', 'id_asset', False)
    service.entity = entity
    
    # Act
    actual = service.get_non_calculated_field_names()
    
    # Assert
    expected = ['Attribute1','Attribute3', Constants.ATTRIBUTE_NAME_IS_DELETED]
    self.assertEqual(actual, expected)
    
  @parameterized.expand([
    ('TableNameSuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuerLong96SuuuuuuuuuuuuuuuuuuuuuperLong128'
        , None, 'TableNameSuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuerLong96' ),
    ('TableNameSuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuerLong96SuuuuuuuuuuuuuuuuuuuuperLong127'
        , '', 'TableNameSuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuerLong96' ),
    ('TableNameSuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuerLong96SuuuuuuuuuuuuuuuuuuuuuuperLong129'
        , '', 'TableNameSuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuerLong96' ),
    ('TableNameSuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuerLong96' 
        , '', 'TableNameSuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuerLong96' ),
    ('TableNameSuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuerLong90SuuuuuuuuuuuuuuuuuuuuuuuuuuuperLong128'
        , 'suffix', 'TableNameSuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuerLong90'),
    ('TableNameSuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuerLong90SuuuuuuuuuuuuuuuuuuuuuperLong122'  
        , 'suffix', 'TableNameSuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuerLong90'),
    ('TableNameSuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuerLong90SuuuuuuuuuuuuuuuuuuuuuuuuuuuuperLong129'
        , 'suffix', 'TableNameSuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuerLong90'),
    ('TableNameSuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuerLong90gggggg'
        , 'suffix', 'TableNameSuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuerLong90'),
    ('TableNameSuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuerLong90'
        , 'suffix', 'TableNameSuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuerLong90'),
    ('TableNameSuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuerLong90'
        , None, 'TableNameSuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuerLong90')    
  ])  
  def test_should_get_valid_name_when_get_staging_table_name(self, entity_table_name, suffix, new_name):
    # Arrange
    entity = EntityBuilder().with_table_name(entity_table_name).build()
    service = TabularIngestionService(self._spark, self._logger, 'asset_uri', 'id_asset', False)
    service.entity = entity
    
    # Act
    actual = service._get_staging_table_name(suffix)
    
    # Assert
    expected = f'{new_name}{service.identifier_temp_table}{suffix}' if suffix is not None else f'{new_name}{service.identifier_temp_table}'
    self.assertEqual(actual, expected)    
    
  def test_should_get_queries_to_drop_staging_tables(self):
    # Arrange
    database_name = 'bug137356'
    table_name = 'AdventureWorks_SalesLT_Customer'
    provider = ProviderBuilder().with_database_name(database_name).build()
    entity = EntityBuilder().with_table_name(table_name).build()
    service = TabularIngestionService(self._spark, self._logger, 'asset_uri', 'id_asset', False)
    service.provider = provider
    service.entity = entity
    
    # Act
    actual = service._get_queries_to_drop_staging_tables()
    
    # Assert
    expected = [f'DROP TABLE IF EXISTS {table_name}{service.identifier_temp_table}_tmpView', f'DROP TABLE IF EXISTS {table_name}{service.identifier_temp_table}']
    self.assertEqual(actual, expected)
    
  @parameterized.expand([('https://storage.blob.core.windows.net/database/table/2022/05/17/filename.parquet', 'wasbs://database@storage.blob.core.windows.net/table/2022/05/17/filename.parquet')
  , ('wasb://database@storagea.blob.core.windows.net/table/2022/05/27/file.csv.gz', 'wasbs://database@storagea.blob.core.windows.net/table/2022/05/27/file.csv.gz')                      
  ])
  def test_should_get_wasbs_version_from_http_uri(self, https_url, expected_wasbs):
    # Arrange
    
    # Act
    storageUtils = StorageUtils(self._spark)
    actual = storageUtils.https_to_wasbs(https_url)
    
    # Assert
    self.assertEqual(actual, expected_wasbs)       
    
  @parameterized.expand([('string', None, None, False, 's.`Name`')
    ,('int', None, None, False, "CASE WHEN CAST(s.`Name` AS INT) <=> CAST(s.`Name` AS DECIMAL(38,18)) THEN s.`Name` ELSE 'NaN' END")
    ,('string', 'Old', 'New', False, "REGEXP_REPLACE(s.`Name`,'Old','New')")
    ,('string', None, None, True, 'TRIM(s.`Name`)')
    ,('string', 'Old', 'New', True, "REGEXP_REPLACE(TRIM(s.`Name`),'Old','New')")
  ])
  def test_should_get_the_field_with_transformations(self, databricks_type, replaced_text, replacement_text, need_trim, expected):
    # Arrange
    load_properties = AttributeLoadPropertiesBuilder().with_replaced_text(replaced_text).with_replacement_text(replacement_text).with_need_trim(need_trim).build()
    attribute = AttributeBuilder().with_name('Name').with_databricks_type(databricks_type).with_load_properties(load_properties).build()
    
    # Act
    service = TabularIngestionService(self._spark, self._logger, 'asset_uri', 'id_asset', False)
    actual = service._get_field_expression(attribute)
    
    # Assert
    self.assertEqual(actual, expected) 
    
  @parameterized.expand([
    ('TRIM(s.`Name`)', None, False, [])
    ,('TRIM(s.`Name`)', r'\N', False, ["WHEN TRIM(s.`Name`) = '\\N' THEN NULL"])
    ,('TRIM(s.`Name`)', None, True, ["WHEN TRIM(s.`Name`) = '' THEN NULL"])
    ,('TRIM(s.`Name`)', r'\N', True, ["WHEN TRIM(s.`Name`) = '\\N' OR TRIM(s.`Name`) == '' THEN NULL"])
  ])
  def test_should_get_the_field_null_validations(self, field_text, null_text, treat_empty_as_null, expected):
    # Arrange   
    service = TabularIngestionService(self._spark, self._logger, 'asset_uri', 'id_asset', False)
    
    # Act
    actual = service._get_statements_for_null_verifications(field_text, null_text, treat_empty_as_null)
    
    # Assert
    self.assertEqual(actual, expected)    
    
  @parameterized.expand([
    (Constants.ATTRIBUTE_NAME_LOAD_DATE, True, None)
    ,('Name', False, FieldDefinition('`Name_SidraRaw`', "s.`Name`", None))
  ])
  def test_should_get_raw_field_for_select_statement(self, name, is_calculated, expected):
    # Arrange
    attribute = AttributeBuilder().with_name(name).with_is_calculated(is_calculated).build()    
    service = TabularIngestionService(self._spark, self._logger, 'asset_uri', 'id_asset', False)

    # Act
    actual = service._get_raw_field_for_select_statement(attribute)

    # Assert
    if expected is None:
      self.assertEquals(actual, expected)
    else:
      self.assertEqual(actual.name, expected.name)
      self.assertEqual(actual.expression, expected.expression)
      self.assertEqual(actual.type, expected.type)
    
  @parameterized.expand([
    (Constants.ATTRIBUTE_NAME_LOAD_DATE, 'CURRENT_TIMESTAMP()', 'TIMESTAMP', FieldDefinition(f'`{Constants.ATTRIBUTE_NAME_LOAD_DATE}`', 'CURRENT_TIMESTAMP()', 'TIMESTAMP'))
    ,(Constants.ATTRIBUTE_NAME_PASSED_VALIDATION,'FALSE','BOOLEAN', FieldDefinition(f'`{Constants.ATTRIBUTE_NAME_PASSED_VALIDATION}`', 'FALSE', 'BOOLEAN'))
    ,(Constants.ATTRIBUTE_NAME_IS_DELETED, Constants.ATTRIBUTE_NAME_IS_DELETED,'BOOLEAN', FieldDefinition(f'`{Constants.ATTRIBUTE_NAME_IS_DELETED}`', Constants.ATTRIBUTE_NAME_IS_DELETED, 'BOOLEAN'))
    ,(Constants.ATTRIBUTE_NAME_FILE_DATE, Constants.ATTRIBUTE_NAME_FILE_DATE,'DATE', FieldDefinition(f'`{Constants.ATTRIBUTE_NAME_FILE_DATE}`', "'2022-05-24'", None))
    ,(Constants.ATTRIBUTE_NAME_ASSET_ID, Constants.ATTRIBUTE_NAME_ASSET_ID, 'INT', FieldDefinition(f'`{Constants.ATTRIBUTE_NAME_ASSET_ID}`', "42", None))
    ,('Name', None, 'STRING', FieldDefinition('`Name_SidraProc`', 'TRIM(s.`Name`)', 'STRING'))
  ])
  def test_should_get_processed_field_for_select_statement(self, name, special_format, dbricks_type, expected):
    # Arrange
    asset_id = '42'
    asset_date = '2022-05-24'
    expression = expected.expression if special_format is None else special_format
    is_calculated = True if special_format is not None else False
    properties = AttributeLoadPropertiesBuilder().with_special_format(special_format).build()
    attribute = AttributeBuilder().with_name(name).with_load_properties(properties).with_databricks_type(dbricks_type).with_is_calculated(is_calculated).build()    

    # Act
    service = TabularIngestionService(self._spark, self._logger, 'asset_uri', asset_id, False)
    service.asset_date = asset_date
    actual = service._get_processed_field_for_select_statement(attribute, expression)

    # Assert
    self.assertEqual(actual.name, expected.name)
    self.assertEqual(actual.expression, expected.expression)
    self.assertEqual(actual.type, expected.type)    
    
  def test_should_return_fields_for_staging_table(self):
    # Arrange
    provider = ProviderBuilder().build()
    attributes = self.initialize_attributes()
    load_properties = LoadPropertiesBuilder().with_null_text(None).build()
    entity = EntityBuilder().with_load_properties(load_properties).with_attributes(attributes).build()      
    asset_id = '42'
    asset_date = '2022-05-24' 
    service = TabularIngestionService(self._spark, self._logger, 'asset_uri', asset_id, False)
    service.provider = provider
    service.entity = entity
    service.asset_date = asset_date

    # Act
    actual_fields = service._get_fields_for_staging_table()

    # Assert
    # PassedValidation is excluded 
    expected_fields = [ FieldDefinition('`Id_SidraProc`', "CASE WHEN CAST(s.`Id` AS INT) <=> CAST(s.`Id` AS DECIMAL(38,18)) THEN s.`Id` ELSE 'NaN' END", 'INT')
      , FieldDefinition('`Id_SidraRaw`', 's.`Id`', None)
      , FieldDefinition('`Name_SidraProc`', 'TRIM(s.`Name`)', 'STRING')
      , FieldDefinition('`Name_SidraRaw`', 's.`Name`', None)
      , FieldDefinition('`FieldEmpty_SidraProc`', "CASE WHEN s.`FieldEmpty` = '' THEN NULL  ELSE s.`FieldEmpty` END", 'STRING')
      , FieldDefinition('`FieldEmpty_SidraRaw`', 's.`FieldEmpty`', None)   
      , FieldDefinition('`FieldReplace_SidraProc`', "REGEXP_REPLACE(s.`FieldReplace`,'1','true')", 'STRING')
      , FieldDefinition('`FieldReplace_SidraRaw`', 's.`FieldReplace`', None)   
      , FieldDefinition('`FieldValidationText_SidraProc`', 's.`FieldValidationText`', 'STRING')
      , FieldDefinition('`FieldValidationText_SidraRaw`', 's.`FieldValidationText`', None)                          
      , FieldDefinition('`IsSomething_SidraProc`', 's.`IsSomething`', 'BOOLEAN')
      , FieldDefinition('`IsSomething_SidraRaw`', 's.`IsSomething`', None)      
      , FieldDefinition(f'`{Constants.ATTRIBUTE_NAME_LOAD_DATE}`', "CURRENT_TIMESTAMP()", 'TIMESTAMP')
      , FieldDefinition(f'`{Constants.ATTRIBUTE_NAME_IS_DELETED}`', Constants.ATTRIBUTE_NAME_IS_DELETED, 'BOOLEAN')
      , FieldDefinition(f'`{Constants.ATTRIBUTE_NAME_FILE_DATE}`', f"'{asset_date}'", None)
      , FieldDefinition(f'`{Constants.ATTRIBUTE_NAME_ASSET_ID}`', f"{asset_id}", None)
    ]    
    self._assert_are_equals_field_definition(actual_fields, expected_fields)
    
  def test_when_null_text_for_entity_is_defined_should_return_fields_for_staging_table(self):
    # Arrange
    provider = ProviderBuilder().build()
    attributes = self.initialize_attributes()
    load_properties = LoadPropertiesBuilder().with_null_text("\\N").build()
    entity = EntityBuilder().with_load_properties(load_properties).with_attributes(attributes).build()      
    asset_id = '42'
    asset_date = '2022-05-24' 
    service = TabularIngestionService(self._spark, self._logger, 'asset_uri', asset_id, False)
    service.asset_date = asset_date
    service.provider = provider
    service.entity = entity

    # Act
    actual_fields = service._get_fields_for_staging_table()
    
    # Assert
    # PassedValidation is excluded 
    expected_fields = [ FieldDefinition('`Id_SidraProc`', "CASE WHEN CASE WHEN CAST(s.`Id` AS INT) <=> CAST(s.`Id` AS DECIMAL(38,18)) THEN s.`Id` ELSE 'NaN' END = '\\N' THEN NULL  ELSE CASE WHEN CAST(s.`Id` AS INT) <=> CAST(s.`Id` AS DECIMAL(38,18)) THEN s.`Id` ELSE 'NaN' END END", 'INT')         
      , FieldDefinition('`Id_SidraRaw`', 's.`Id`', None)
      , FieldDefinition('`Name_SidraProc`', "CASE WHEN TRIM(s.`Name`) = '\\N' THEN NULL  ELSE TRIM(s.`Name`) END", 'STRING')
      , FieldDefinition('`Name_SidraRaw`', 's.`Name`', None)
      , FieldDefinition('`FieldEmpty_SidraProc`', "CASE WHEN s.`FieldEmpty` = '\\N' OR s.`FieldEmpty` == '' THEN NULL  ELSE s.`FieldEmpty` END", 'STRING')
      , FieldDefinition('`FieldEmpty_SidraRaw`', 's.`FieldEmpty`', None)   
      , FieldDefinition('`FieldReplace_SidraProc`', "CASE WHEN REGEXP_REPLACE(s.`FieldReplace`,'1','true') = '\\N' THEN NULL  ELSE REGEXP_REPLACE(s.`FieldReplace`,'1','true') END", 'STRING')
      , FieldDefinition('`FieldReplace_SidraRaw`', 's.`FieldReplace`', None)   
      , FieldDefinition('`FieldValidationText_SidraProc`', "CASE WHEN s.`FieldValidationText` = '\\N' THEN NULL  ELSE s.`FieldValidationText` END", 'STRING')
      , FieldDefinition('`FieldValidationText_SidraRaw`', 's.`FieldValidationText`', None)   
      , FieldDefinition('`IsSomething_SidraProc`', "CASE WHEN s.`IsSomething` = '\\N' THEN NULL  ELSE s.`IsSomething` END", 'BOOLEAN')
      , FieldDefinition('`IsSomething_SidraRaw`', 's.`IsSomething`', None)
      , FieldDefinition(f'`{Constants.ATTRIBUTE_NAME_LOAD_DATE}`', "CURRENT_TIMESTAMP()", 'TIMESTAMP')
      , FieldDefinition(f'`{Constants.ATTRIBUTE_NAME_IS_DELETED}`', Constants.ATTRIBUTE_NAME_IS_DELETED, 'BOOLEAN')
      , FieldDefinition(f'`{Constants.ATTRIBUTE_NAME_FILE_DATE}`', f"'{asset_date}'", None)
      , FieldDefinition(f'`{Constants.ATTRIBUTE_NAME_ASSET_ID}`', f"{asset_id}", None)
    ]    
    self._assert_are_equals_field_definition(actual_fields, expected_fields)
  
    
  def test_should_truncate_table_if_table_is_not_partitioned_by_asset_id(self):
    # Arrange
    col1 = AttributeBuilder().with_name('Id').with_order(1).with_databricks_type('INT') \
      .with_is_primary_key(True) \
      .with_load_properties(AttributeLoadPropertiesBuilder().build()).build()    
    col2_properties = AttributeLoadPropertiesBuilder().with_special_format(Constants.ATTRIBUTE_NAME_FILE_DATE).build()
    col2 = AttributeBuilder().with_name(Constants.ATTRIBUTE_NAME_FILE_DATE).with_order(2).with_databricks_type('DATE') \
      .with_is_calculated(True).with_is_metadata(True).with_is_partition_column(True) \
      .with_load_properties(col2_properties).build()
    provider = ProviderBuilder().with_database_name("DBName").build()
    attributes = [col1, col2]
    entity = EntityBuilder().with_table_name("TBName").with_load_properties(LoadPropertiesBuilder().build()).with_attributes(attributes).build()     
    asset_id = 42
    service = TabularIngestionService(self._spark, self._logger, 'asset_uri', asset_id, False)
    service.provider = provider
    service.entity = entity    
    
    # Act
    actual = service._get_truncate_old_partition_from_same_file_statements()
                                                         
    # Assert
    expected = ["TRUNCATE TABLE `DBName`.`TBName`"]
    self.assertEqual(actual, expected)
  
  @parameterized.expand([(0,),(3,)])
  def test_should_delete_partition_if_table_is_partitioned_by_asset_id_and_is_delta_format(self, table_format):
    # Arrange
    col1 = AttributeBuilder().with_name('Id').with_order(1).with_databricks_type('INT') \
      .with_is_primary_key(True) \
      .with_load_properties(AttributeLoadPropertiesBuilder().build()).build()    
    col2_properties = AttributeLoadPropertiesBuilder().with_special_format(Constants.ATTRIBUTE_NAME_ASSET_ID).build()
    col2 = AttributeBuilder().with_name(Constants.ATTRIBUTE_NAME_ASSET_ID).with_order(2).with_databricks_type('INT') \
      .with_is_calculated(True).with_is_metadata(True).with_is_partition_column(True) \
      .with_load_properties(col2_properties).build()
  
    provider = ProviderBuilder().with_database_name("DBName").build()
    attributes = [col1, col2]
    load_properties = LoadPropertiesBuilder().with_id_table_format(table_format).build()
    entity = EntityBuilder().with_table_name("TBName").with_load_properties(load_properties).with_attributes(attributes).build()     
    asset_id = '42'
    service = TabularIngestionService(self._spark, self._logger, 'asset_uri', asset_id, False)
    service.provider = provider
    service.entity = entity    
    
    # Act
    actual = service._get_truncate_old_partition_from_same_file_statements()
                                                         
    # Assert
    if table_format == 3:
      expected = [f"DELETE FROM `DBName`.`TBName` WHERE `{Constants.ATTRIBUTE_NAME_ASSET_ID}`=42"]
    else:
      expected = []
    self.assertEqual(actual, expected)  
    
  def test_should_get_statements_to_insert_data_into_final_table_for_delta_tables(self):
    # Arrange
    provider = ProviderBuilder().with_database_name("DBName").build()
    attributes = self.initialize_attributes()
    load_properties = LoadPropertiesBuilder().with_id_table_format(3).build()
    entity = EntityBuilder().with_table_name("TBName").with_load_properties(load_properties).with_attributes(attributes).build()     
    asset_id = '42'
    asset_date = '2022-06-08'
    service = TabularIngestionService(self._spark, self._logger, 'asset_uri', asset_id, False)
    service.asset_date = asset_date
    service.provider = provider
    service.entity = entity
    
    # Act
    actual = service._get_insert_snapshot_data_into_final_table_statement()
    
    # Assert
    expected = f"""INSERT INTO TABLE `DBName`.`TBName` PARTITION (`{Constants.ATTRIBUTE_NAME_FILE_DATE}`,`{Constants.ATTRIBUTE_NAME_ASSET_ID}`) (`Id`,`Name`,`FieldEmpty`,`FieldReplace`,`FieldValidationText`,`IsSomething`,`{Constants.ATTRIBUTE_NAME_LOAD_DATE}`,`{Constants.ATTRIBUTE_NAME_PASSED_VALIDATION}`,`{Constants.ATTRIBUTE_NAME_IS_DELETED}`,`{Constants.ATTRIBUTE_NAME_FILE_DATE}`,`{Constants.ATTRIBUTE_NAME_ASSET_ID}`) 
SELECT `Id_SidraProc`,`Name_SidraProc`,`FieldEmpty_SidraProc`,`FieldReplace_SidraProc`,`FieldValidationText_SidraProc`,`IsSomething_SidraProc`,`{Constants.ATTRIBUTE_NAME_LOAD_DATE}`,`{Constants.ATTRIBUTE_NAME_PASSED_VALIDATION}`,`{Constants.ATTRIBUTE_NAME_IS_DELETED}`,`{Constants.ATTRIBUTE_NAME_FILE_DATE}`,`{Constants.ATTRIBUTE_NAME_ASSET_ID}`
FROM TBName{service.identifier_temp_table}_tmpView"""
    self.maxDiff = None
    self.assertEqual(actual, expected) 
    
  def test_should_get_statements_to_insert_data_into_final_table_for_non_delta_tables(self):
    # Arrange
    provider = ProviderBuilder().with_database_name("DBName").build()
    attributes = self.initialize_attributes()
    load_properties = LoadPropertiesBuilder().with_id_table_format(0).build()
    entity = EntityBuilder().with_table_name("TBName").with_load_properties(load_properties).with_attributes(attributes).build()     
    asset_id = '42'
    asset_date = '2022-06-08'
    service = TabularIngestionService(self._spark, self._logger, 'asset_uri', asset_id, False)
    service.provider = provider
    service.entity = entity
    service.asset_date = asset_date
    
    # Act
    actual = service._get_insert_snapshot_data_into_final_table_statement()
    
    # Assert
    expected = f"""INSERT OVERWRITE TABLE `DBName`.`TBName` PARTITION (`{Constants.ATTRIBUTE_NAME_FILE_DATE}`='2022-06-08',`{Constants.ATTRIBUTE_NAME_ASSET_ID}`='42') (`Id`,`Name`,`FieldEmpty`,`FieldReplace`,`FieldValidationText`,`IsSomething`,`{Constants.ATTRIBUTE_NAME_LOAD_DATE}`,`{Constants.ATTRIBUTE_NAME_PASSED_VALIDATION}`,`{Constants.ATTRIBUTE_NAME_IS_DELETED}`) 
SELECT `Id_SidraProc`,`Name_SidraProc`,`FieldEmpty_SidraProc`,`FieldReplace_SidraProc`,`FieldValidationText_SidraProc`,`IsSomething_SidraProc`,`{Constants.ATTRIBUTE_NAME_LOAD_DATE}`,`{Constants.ATTRIBUTE_NAME_PASSED_VALIDATION}`,`{Constants.ATTRIBUTE_NAME_IS_DELETED}`
FROM TBName{service.identifier_temp_table}_tmpView"""
    self.maxDiff = None
    self.assertEqual(actual, expected)     
    
  def test_should_get_statements_to_insert_data_into_final_table_for_non_delta_tables_with_non_standard_partition_columns(self):
    # Arrange
    provider = ProviderBuilder().with_database_name("DBName").build()
    attributes = self.initialize_attributes()
    col_properties = AttributeLoadPropertiesBuilder().with_special_format(Constants.ATTRIBUTE_NAME_ASSET_ID).build()
    non_standard_partition_column = AttributeBuilder().with_name('PartitionField').with_order(11).with_databricks_type('INT') \
      .with_is_partition_column(True) \
      .with_load_properties(col_properties).build()
    attributes.append(non_standard_partition_column)
    load_properties = LoadPropertiesBuilder().with_id_table_format(0).build()
    entity = EntityBuilder().with_table_name("TBName").with_load_properties(load_properties).with_attributes(attributes).build()     
    asset_id = '42'
    asset_date = '2022-06-08'
    service = TabularIngestionService(self._spark, self._logger, 'asset_uri', asset_id, False)
    service.provider = provider
    service.entity = entity
    service.asset_date = asset_date
    
    # Act
    actual = service._get_insert_snapshot_data_into_final_table_statement()
    
    # Assert
    expected = f"""INSERT OVERWRITE TABLE `DBName`.`TBName` PARTITION (`{Constants.ATTRIBUTE_NAME_FILE_DATE}`='2022-06-08',`{Constants.ATTRIBUTE_NAME_ASSET_ID}`='42',`PartitionField`) (`Id`,`Name`,`FieldEmpty`,`FieldReplace`,`FieldValidationText`,`IsSomething`,`{Constants.ATTRIBUTE_NAME_LOAD_DATE}`,`{Constants.ATTRIBUTE_NAME_PASSED_VALIDATION}`,`{Constants.ATTRIBUTE_NAME_IS_DELETED}`,`PartitionField`) 
SELECT `Id_SidraProc`,`Name_SidraProc`,`FieldEmpty_SidraProc`,`FieldReplace_SidraProc`,`FieldValidationText_SidraProc`,`IsSomething_SidraProc`,`{Constants.ATTRIBUTE_NAME_LOAD_DATE}`,`{Constants.ATTRIBUTE_NAME_PASSED_VALIDATION}`,`{Constants.ATTRIBUTE_NAME_IS_DELETED}`,`PartitionField`
FROM TBName{service.identifier_temp_table}_tmpView"""
    self.maxDiff = None
    self.assertEqual(actual, expected) 
    
  def test_should_raise_exception_if_there_is_not_asset_id_defined(self):
    # Arrange
    asset_id = None
    asset_date = '2022-06-08'    
    service = TabularIngestionService(self._spark, self._logger, 'asset_uri', asset_id, False)
       
    # Act/Assert
    with self.assertRaises(Exception) as context:
      service.set_metadata_information()

    expected = 'Unable to retrieve the metadata for the asset because there is not asset id defined'
    self.assertIn(expected, str(context.exception))
    
  def test_merge(self):
    # Arrange
    provider = ProviderBuilder().with_database_name("DBName").build()
    attributes = self.initialize_attributes()
    load_properties = LoadPropertiesBuilder().with_id_table_format(0).build()
    entity = EntityBuilder().with_table_name("TBName").with_load_properties(load_properties).with_attributes(attributes).build()     
    asset_id = '42'
    asset_date = '2022-06-08'
    service = TabularIngestionService(self._spark, self._logger, 'asset_uri', asset_id, False)
    service.provider = provider
    service.entity = entity
    service.asset_date = asset_date
    staging_table_name = service._get_staging_table_name(Constants.TABLE_TEMP_JOIN_SUFFIX)
    
    # Act
    
    actual = service._get_insert_merge_data_into_final_table()
    
    # Assert    
    expected = f"""
MERGE INTO `DBName`.`TBName` AS t
USING (
  SELECT `Id_SidraProc`, `Name_SidraProc`, `FieldEmpty_SidraProc`, `FieldReplace_SidraProc`, `FieldValidationText_SidraProc`, `IsSomething_SidraProc`, `{Constants.ATTRIBUTE_NAME_LOAD_DATE}`, `{Constants.ATTRIBUTE_NAME_PASSED_VALIDATION}`, `{Constants.ATTRIBUTE_NAME_IS_DELETED}`, `{Constants.ATTRIBUTE_NAME_FILE_DATE}`, `{Constants.ATTRIBUTE_NAME_ASSET_ID}`
  FROM {staging_table_name}
  ) s ON s.`Id_SidraProc` = t.Id
  
WHEN MATCHED THEN UPDATE SET
  t.`Name` = CASE s.{Constants.ATTRIBUTE_NAME_IS_DELETED} WHEN True THEN t.`Name` else s.`Name_SidraProc` END, t.`FieldEmpty` = CASE s.{Constants.ATTRIBUTE_NAME_IS_DELETED} WHEN True THEN t.`FieldEmpty` else s.`FieldEmpty_SidraProc` END, t.`FieldReplace` = CASE s.{Constants.ATTRIBUTE_NAME_IS_DELETED} WHEN True THEN t.`FieldReplace` else s.`FieldReplace_SidraProc` END, t.`FieldValidationText` = CASE s.{Constants.ATTRIBUTE_NAME_IS_DELETED} WHEN True THEN t.`FieldValidationText` else s.`FieldValidationText_SidraProc` END, t.`IsSomething` = CASE s.{Constants.ATTRIBUTE_NAME_IS_DELETED} WHEN True THEN t.`IsSomething` else s.`IsSomething_SidraProc` END, t.`{Constants.ATTRIBUTE_NAME_LOAD_DATE}` = CASE s.{Constants.ATTRIBUTE_NAME_IS_DELETED} WHEN True THEN t.`{Constants.ATTRIBUTE_NAME_LOAD_DATE}` else s.`{Constants.ATTRIBUTE_NAME_LOAD_DATE}` END, t.`{Constants.ATTRIBUTE_NAME_PASSED_VALIDATION}` = CASE s.{Constants.ATTRIBUTE_NAME_IS_DELETED} WHEN True THEN t.`{Constants.ATTRIBUTE_NAME_PASSED_VALIDATION}` else s.`{Constants.ATTRIBUTE_NAME_PASSED_VALIDATION}` END, t.`{Constants.ATTRIBUTE_NAME_FILE_DATE}` = CASE s.{Constants.ATTRIBUTE_NAME_IS_DELETED} WHEN True THEN t.`{Constants.ATTRIBUTE_NAME_FILE_DATE}` else s.`{Constants.ATTRIBUTE_NAME_FILE_DATE}` END, t.`{Constants.ATTRIBUTE_NAME_IS_DELETED}` = s.`{Constants.ATTRIBUTE_NAME_IS_DELETED}`,t.`{Constants.ATTRIBUTE_NAME_ASSET_ID}` = s.`{Constants.ATTRIBUTE_NAME_ASSET_ID}`
WHEN NOT MATCHED THEN INSERT
  (Id, Name, FieldEmpty, FieldReplace, FieldValidationText, IsSomething, {Constants.ATTRIBUTE_NAME_LOAD_DATE}, {Constants.ATTRIBUTE_NAME_PASSED_VALIDATION}, {Constants.ATTRIBUTE_NAME_IS_DELETED}, {Constants.ATTRIBUTE_NAME_FILE_DATE}, {Constants.ATTRIBUTE_NAME_ASSET_ID})
VALUES
  (s.`Id_SidraProc`, s.`Name_SidraProc`, s.`FieldEmpty_SidraProc`, s.`FieldReplace_SidraProc`, s.`FieldValidationText_SidraProc`, s.`IsSomething_SidraProc`, s.`{Constants.ATTRIBUTE_NAME_LOAD_DATE}`, s.`{Constants.ATTRIBUTE_NAME_PASSED_VALIDATION}`, s.`{Constants.ATTRIBUTE_NAME_IS_DELETED}`, s.`{Constants.ATTRIBUTE_NAME_FILE_DATE}`, s.`{Constants.ATTRIBUTE_NAME_ASSET_ID}`)"""
    
    self.maxDiff = None
    self.assertEqual(actual, expected)    
    
  def test_should_return_an_error_if_an_attribute_is_calculated_and_is_not_metadata_and_there_is_not_a_definition_of_how_it_is_calculated(self):
    # Arrange
    attributes = self.initialize_attributes()
    # Attribute that it is neither partition column nor metadata column but it is calculated and there is not special_format defined
    attributes[1].is_calculated = True
    load_properties = LoadPropertiesBuilder().build()
    entity = EntityBuilder().with_load_properties(load_properties).with_attributes(attributes).build()    
    asset_id = '42'
    asset_date = '2022-05-24'
    service = TabularIngestionService(self._spark, self._logger, 'asset_uri', asset_id, False)
    service.entity = entity
    service.asset_date = asset_date 
    
    # Act/Assert
    with self.assertRaises(Exception) as context:
      service._get_fields_for_staging_table()
    
    error_message = f"[Tabular Ingestion] The attribute 'Name' is not a metadata attribute and it is defined as calculated without a definition of how it is calculated."
    self.assertTrue(error_message in str(context.exception))     
  
  def test_should_return_expected_merge_statement_for_calculated_fields(self):
    # Arrange
    provider = ProviderBuilder().with_database_name("DBName").build()
    attributes = self.initialize_attributes()
    # Attribute that it is neither partition column nor metadata column but it is calculated
    attributes[1].is_calculated = True    
    load_properties = LoadPropertiesBuilder().with_id_table_format(0).build()
    entity = EntityBuilder().with_table_name("TBName").with_load_properties(load_properties).with_attributes(attributes).build()     
    asset_id = '42'
    asset_date = '2022-06-08'
    service = TabularIngestionService(self._spark, self._logger, 'asset_uri', asset_id, False)
    service.provider = provider
    service.entity = entity
    service.asset_date = asset_date
    staging_table_name = service._get_staging_table_name(Constants.TABLE_TEMP_JOIN_SUFFIX)
    
    # Act
    
    actual = service._get_insert_merge_data_into_final_table()
    
    # Assert    
    expected = f"""
MERGE INTO `DBName`.`TBName` AS t
USING (
  SELECT `Id_SidraProc`, `Name`, `FieldEmpty_SidraProc`, `FieldReplace_SidraProc`, `FieldValidationText_SidraProc`, `IsSomething_SidraProc`, `{Constants.ATTRIBUTE_NAME_LOAD_DATE}`, `{Constants.ATTRIBUTE_NAME_PASSED_VALIDATION}`, `{Constants.ATTRIBUTE_NAME_IS_DELETED}`, `{Constants.ATTRIBUTE_NAME_FILE_DATE}`, `{Constants.ATTRIBUTE_NAME_ASSET_ID}`
  FROM {staging_table_name}
  ) s ON s.`Id_SidraProc` = t.Id
  
WHEN MATCHED THEN UPDATE SET
  t.`Name` = CASE s.{Constants.ATTRIBUTE_NAME_IS_DELETED} WHEN True THEN t.`Name` else s.`Name` END, t.`FieldEmpty` = CASE s.{Constants.ATTRIBUTE_NAME_IS_DELETED} WHEN True THEN t.`FieldEmpty` else s.`FieldEmpty_SidraProc` END, t.`FieldReplace` = CASE s.{Constants.ATTRIBUTE_NAME_IS_DELETED} WHEN True THEN t.`FieldReplace` else s.`FieldReplace_SidraProc` END, t.`FieldValidationText` = CASE s.{Constants.ATTRIBUTE_NAME_IS_DELETED} WHEN True THEN t.`FieldValidationText` else s.`FieldValidationText_SidraProc` END, t.`IsSomething` = CASE s.{Constants.ATTRIBUTE_NAME_IS_DELETED} WHEN True THEN t.`IsSomething` else s.`IsSomething_SidraProc` END, t.`{Constants.ATTRIBUTE_NAME_LOAD_DATE}` = CASE s.{Constants.ATTRIBUTE_NAME_IS_DELETED} WHEN True THEN t.`{Constants.ATTRIBUTE_NAME_LOAD_DATE}` else s.`{Constants.ATTRIBUTE_NAME_LOAD_DATE}` END, t.`{Constants.ATTRIBUTE_NAME_PASSED_VALIDATION}` = CASE s.{Constants.ATTRIBUTE_NAME_IS_DELETED} WHEN True THEN t.`{Constants.ATTRIBUTE_NAME_PASSED_VALIDATION}` else s.`{Constants.ATTRIBUTE_NAME_PASSED_VALIDATION}` END, t.`{Constants.ATTRIBUTE_NAME_FILE_DATE}` = CASE s.{Constants.ATTRIBUTE_NAME_IS_DELETED} WHEN True THEN t.`{Constants.ATTRIBUTE_NAME_FILE_DATE}` else s.`{Constants.ATTRIBUTE_NAME_FILE_DATE}` END, t.`{Constants.ATTRIBUTE_NAME_IS_DELETED}` = s.`{Constants.ATTRIBUTE_NAME_IS_DELETED}`,t.`{Constants.ATTRIBUTE_NAME_ASSET_ID}` = s.`{Constants.ATTRIBUTE_NAME_ASSET_ID}`
WHEN NOT MATCHED THEN INSERT
  (Id, Name, FieldEmpty, FieldReplace, FieldValidationText, IsSomething, {Constants.ATTRIBUTE_NAME_LOAD_DATE}, {Constants.ATTRIBUTE_NAME_PASSED_VALIDATION}, {Constants.ATTRIBUTE_NAME_IS_DELETED}, {Constants.ATTRIBUTE_NAME_FILE_DATE}, {Constants.ATTRIBUTE_NAME_ASSET_ID})
VALUES
  (s.`Id_SidraProc`, s.`Name`, s.`FieldEmpty_SidraProc`, s.`FieldReplace_SidraProc`, s.`FieldValidationText_SidraProc`, s.`IsSomething_SidraProc`, s.`{Constants.ATTRIBUTE_NAME_LOAD_DATE}`, s.`{Constants.ATTRIBUTE_NAME_PASSED_VALIDATION}`, s.`{Constants.ATTRIBUTE_NAME_IS_DELETED}`, s.`{Constants.ATTRIBUTE_NAME_FILE_DATE}`, s.`{Constants.ATTRIBUTE_NAME_ASSET_ID}`)"""
    
    self.maxDiff = None
    self.assertEqual(actual, expected)     
    
  def test_should_get_statements_to_insert_data_into_final_table_for_delta_tables_and_using_calculated_fields(self):
    # Arrange
    provider = ProviderBuilder().with_database_name("DBName").build()
    attributes = self.initialize_attributes()
    # Attribute that it is neither partition column nor metadata column but it is calculated
    attributes[1].is_calculated = True      
    load_properties = LoadPropertiesBuilder().with_id_table_format(3).build()
    entity = EntityBuilder().with_table_name("TBName").with_load_properties(load_properties).with_attributes(attributes).build()     
    asset_id = '42'
    asset_date = '2022-06-08'
    service = TabularIngestionService(self._spark, self._logger, 'asset_uri', asset_id, False)
    service.provider = provider
    service.entity = entity
    service.asset_date = asset_date
    
    # Act
    actual = service._get_insert_snapshot_data_into_final_table_statement()
    
    # Assert
    expected = f"""INSERT INTO TABLE `DBName`.`TBName` PARTITION (`{Constants.ATTRIBUTE_NAME_FILE_DATE}`,`{Constants.ATTRIBUTE_NAME_ASSET_ID}`) (`Id`,`Name`,`FieldEmpty`,`FieldReplace`,`FieldValidationText`,`IsSomething`,`{Constants.ATTRIBUTE_NAME_LOAD_DATE}`,`{Constants.ATTRIBUTE_NAME_PASSED_VALIDATION}`,`{Constants.ATTRIBUTE_NAME_IS_DELETED}`,`{Constants.ATTRIBUTE_NAME_FILE_DATE}`,`{Constants.ATTRIBUTE_NAME_ASSET_ID}`) 
SELECT `Id_SidraProc`,`Name`,`FieldEmpty_SidraProc`,`FieldReplace_SidraProc`,`FieldValidationText_SidraProc`,`IsSomething_SidraProc`,`{Constants.ATTRIBUTE_NAME_LOAD_DATE}`,`{Constants.ATTRIBUTE_NAME_PASSED_VALIDATION}`,`{Constants.ATTRIBUTE_NAME_IS_DELETED}`,`{Constants.ATTRIBUTE_NAME_FILE_DATE}`,`{Constants.ATTRIBUTE_NAME_ASSET_ID}`
FROM TBName{service.identifier_temp_table}_tmpView"""
    self.maxDiff = None
    self.assertEqual(actual, expected)

  def initialize_attributes(self):
       col1 = AttributeBuilder().with_name('Id').with_order(1).with_databricks_type('INT') \
        .with_is_primary_key(True) \
        .with_load_properties(AttributeLoadPropertiesBuilder().build()).build()

       col2_properties = AttributeLoadPropertiesBuilder().with_need_trim(True).with_is_nullable(True).with_max_len(30).build()
       col2 = AttributeBuilder().with_name('Name').with_order(2) \
        .with_load_properties(col2_properties).build()
        
       col3 = AttributeBuilder().with_name('FieldEmpty').with_order(3) \
        .with_load_properties(AttributeLoadPropertiesBuilder().with_treat_empty_as_null(True).build()).build()

       col4_properties = AttributeLoadPropertiesBuilder().with_replaced_text('1') \
        .with_replacement_text('true').build()
       col4 = AttributeBuilder().with_name('FieldReplace').with_order(4) \
        .with_load_properties(col4_properties).build()
        
       col5_properties = AttributeLoadPropertiesBuilder().with_validation_text("`FieldValidationText_SidraProc` LIKE 'PREFIX_%'").build()
       col5 = AttributeBuilder().with_name('FieldValidationText').with_order(5) \
        .with_load_properties(col5_properties).build()    
        
       col6 = AttributeBuilder().with_name('IsSomething').with_order(6).with_databricks_type('BOOLEAN') \
        .with_load_properties(AttributeLoadPropertiesBuilder().build()).build()
        
       col7_properties = AttributeLoadPropertiesBuilder().with_special_format("CURRENT_TIMESTAMP()").build()
       col7 = AttributeBuilder().with_name(Constants.ATTRIBUTE_NAME_LOAD_DATE).with_order(7).with_databricks_type('TIMESTAMP') \
        .with_is_calculated(True).with_is_metadata(True) \
        .with_load_properties(col7_properties).build()    
        
       col8_properties = AttributeLoadPropertiesBuilder().with_is_nullable(True).build()
       col8 = AttributeBuilder().with_name(Constants.ATTRIBUTE_NAME_PASSED_VALIDATION).with_order(8).with_databricks_type('BOOLEAN') \
        .with_is_calculated(True).with_is_metadata(True) \
        .with_load_properties(col8_properties).build()
        
       col9_properties = AttributeLoadPropertiesBuilder().with_special_format(Constants.ATTRIBUTE_NAME_IS_DELETED).build()
       col9 = AttributeBuilder().with_name(Constants.ATTRIBUTE_NAME_IS_DELETED).with_order(9).with_databricks_type('BOOLEAN') \
        .with_is_calculated(True).with_is_metadata(True) \
        .with_load_properties(col9_properties).build()    
        
       col10_properties = AttributeLoadPropertiesBuilder().with_special_format(Constants.ATTRIBUTE_NAME_FILE_DATE).build()
       col10 = AttributeBuilder().with_name(Constants.ATTRIBUTE_NAME_FILE_DATE).with_order(10).with_databricks_type('DATE') \
        .with_is_calculated(True).with_is_metadata(True).with_is_partition_column(True) \
        .with_load_properties(col10_properties).build()
        
       col11_properties = AttributeLoadPropertiesBuilder().with_special_format(Constants.ATTRIBUTE_NAME_ASSET_ID).build()
       col11 = AttributeBuilder().with_name(Constants.ATTRIBUTE_NAME_ASSET_ID).with_order(11).with_databricks_type('INT') \
        .with_is_calculated(True).with_is_metadata(True).with_is_partition_column(True) \
        .with_load_properties(col11_properties).build()    

       attributes = [col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11]
       return attributes

def run_tests():
  loader = unittest.TestLoader()
  suite  = unittest.TestSuite()

  # add tests to the test suite
  suite.addTests(loader.loadTestsFromTestCase(testCaseClass=TestTabularIngestionService))

  # initialize a runner, pass it your suite and run it
  runner = xmlrunner.XMLTestRunner(verbosity=3, descriptions=True, output='/runtests/TabularIngestionService_Report')
  result = runner.run(suite)

  # print chart
  TestUtils.print_pie_chart_tests(len(result.successes), len(result.failures), len(result.errors), len(result.skipped))

  assert len(result.failures) == 0
  assert len(result.errors) == 0
