#TESTS

#	SOURCE				|	MODE			|	DELTA TABLE (from Entity) 							| Operation | Destination format (Entity.IdTableFormat)
#=================================================================================================================================================
#	Parquet-Full load	|	Snapshot(Append)|	True												|	Insert
#	Parquet-Incremental	|	Merge			|	False(Only for the Full load - Snapshot combination)|	Update
#	Excel file			|					|														|	Delete
#	CSV file			|

import unittest
import time
from sidraconnector.sdk.metadata.models.builders import AttributeBuilder
from test.dsuingestion.tabularingestion.test_E2E_base import TestE2EBase
from test.dsuingestion.tabularingestion.utils import Utils as E2EUtils
from test.utils import Utils
import sidraconnector.sdk.constants as Constants
import xmlrunner
import parameterized
from parameterized import parameterized


class TestE2EConsolidationModeSnapshot(TestE2EBase):
  @parameterized.expand([
  ('files/countries_insert.parquet', "parquet", 249),
  ('files/countries_insert.csv', "csv", 249),
  ('files/countries_insert.xls', "xls", 249),
  ('files/countries_insert.xlsm', "xlsm", 249),
  ('files/countries_insert.xlsx', "xlsx", 249)
  ])
  def test_insert(self, source_file_path, file_format, expected_rows):
      #ARRANGE
      provider, entity, destination_path = self._fixture._prepare_countries_metadata(source_file_path, file_format, recreate_tables = True, with_primary_key = True, consolidation_mode = Constants.CONSOLIDATION_MODE_SNAPSHOT)
      #Data table is created
      self.assertTrue(E2EUtils.get_table(self._spark, provider.database_name, entity.table_name.lower()))
           
      #ACT
      #Insert
      self.execute_tabular_ingestion(destination_path)
        
      #ASSERT
      #Asset is created
      assets = self._fixture._asset_service.get_recent_entity_assets(entity.id)
      self.assertTrue(assets)#Check that assets is not empty array, so an asset has been created for the entity
   
      #Data is extracted
      self._spark.catalog.setCurrentDatabase(provider.database_name)
      result = self._spark.sql(f"SELECT COUNT(*) as rows FROM {entity.table_name.lower()}")
      value = result.select("rows").collect()
      count = value[0].asDict()["rows"]
        
      if(count != expected_rows):
          self._logger.warning(f"""[E2E_ConsolidationModeSnapshotTest][test_insert] FAILED. Expected errors: {expected_rows}. Current errors: {count}. Source file path: {source_file_path}, file format: {file_format}""")
      
      self.assertEqual(count, expected_rows)
    
  @parameterized.expand([
  ("parquet 2 assets",'files/countries_insert.parquet', "parquet", "countries.parquet", 2, 498),
  ("parquet 5 assets",'files/countries_insert.parquet', "parquet", "countries.parquet", 5, 1245),
  ("csv 2 assets",'files/countries_insert.csv', "csv", "countries.csv", 2, 498),
  ("csv 5 assets",'files/countries_insert.csv', "csv", "countries.csv", 5, 1245)]) 
  def test_multiple_insert_full_load_same_content_different_date(self, _, source_file_path : str, file_format :str, destination_path : str, iterations : int, expected_rows : int):
     #ARRANGE
    provider, entity, destination_path = self._fixture._prepare_countries_metadata(source_file_path, file_format, recreate_tables = True, with_primary_key = True, consolidation_mode = Constants.CONSOLIDATION_MODE_SNAPSHOT)

    #ACT
    counter = 0
    while counter < iterations:
      destination_path = self._fixture.get_full_storage_destination_path(source_file_path, entity, provider.provider_name)
      self._fixture.move_file_to_execution_storage(source_file_path, destination_path)
      self.execute_tabular_ingestion(destination_path)
      time.sleep(2)
      counter += 1

    #ASSERT
    #Asset is created
    assets = self._fixture._asset_service.get_recent_entity_assets(entity.id)
    self.assertTrue(assets)#Check that assets is not empty array, so an asset has been created for the entity
    self.assertTrue(len(assets) == iterations)
    
    #Data is extracted
    self._spark.catalog.setCurrentDatabase(provider.database_name)
    result = self._spark.sql(f"SELECT COUNT(*) as rows FROM {entity.table_name.lower()}")
    value = result.select("rows").collect()
    count = value[0].asDict()["rows"]
    
    if(count != expected_rows):
      self._logger.warning(f"""[E2E_ConsolidationModeSnapshotTest][test_multiple_insert_full_load_same_content_different_date] FAILED. Expected errors: {expected_rows}. Current errors: {count}. Source file path: {source_file_path}, file format: {file_format}, destination path: {destination_path}, iterations: {iterations}""")
      
    self.assertEqual(count, expected_rows)
    
    #different sources
    self._spark.catalog.setCurrentDatabase(provider.database_name)
    result = self._spark.sql(f"SELECT COUNT(DISTINCT {Constants.ATTRIBUTE_NAME_ASSET_ID}) as rows FROM {entity.table_name.lower()}")
    value = result.select("rows").collect()
    count = value[0].asDict()["rows"]
    self.assertEqual(count, iterations)
    
  @parameterized.expand([
  ('files/countries_insert.parquet', "parquet", "countries.parquet", 249),
  ('files/countries_insert.csv', "csv", "countries.csv", 249),
  ('files/countries_insert.xls', "xls", "countries.xls",   249),
  ('files/countries_insert.xlsm', "xlsm", "countries.xlsm", 249),
  ('files/countries_insert.xlsx', "xlsx", "countries.xlsx",  249)
  ])
  def test_multiple_insert_full_load_same_content_same_date(self, source_file_path, file_format, destination_file_name, expected_rows):
    #ARRANGE
    provider, entity, destination_path = self._fixture._prepare_countries_metadata(source_file_path, file_format, destination_file_name = destination_file_name, recreate_tables = True, with_primary_key = True, consolidation_mode = Constants.CONSOLIDATION_MODE_SNAPSHOT)
     
    #ACT
    #Insert
    self.execute_tabular_ingestion(destination_path)
    
    time.sleep(2)
    self._fixture.move_file_to_execution_storage(source_file_path, destination_path)
    #Insert same file
    self.execute_tabular_ingestion(destination_path)
   
    #ASSERT
    #Data is extracted
    self._spark.catalog.setCurrentDatabase(provider.database_name)
    result = self._spark.sql(f"SELECT COUNT(*) as rows FROM {entity.table_name.lower()}")
    value = result.select("rows").collect()
    count = value[0].asDict()["rows"]
    if(count != expected_rows):
      self._logger.warning(f"[E2E_ConsolidationModeSnapshotTest][test_multiple_insert_full_load_same_content_same_date] FAILED. Expected errors: {expected_rows}. Actual errors: {count}. Source file path: {source_file_path}, file format: {file_format}, destination file name: {destination_file_name}")
      
    self.assertEqual(count, expected_rows)

  @parameterized.expand([
  ('files/countries_insert.parquet', "parquet", "countries.parquet", "files/countries_update.parquet", 300),
  ('files/countries_insert.csv', "csv", "countries.csv", 'files/countries_update.csv', 300),
  ('files/countries_insert.xls', "xls", "countries.xls",  'files/countries_update.xls', 300),
  ('files/countries_insert.xlsm', "xlsm", "countries.xlsm",  'files/countries_update.xlsm', 300),
  ('files/countries_insert.xlsx', "xlsx", "countries.xlsx",  'files/countries_update.xlsx', 300)
  ])
  def test_update(self, source_file_path, file_format, destination_file_name, update_source, expected_rows):
    #ARRANGE
    provider, entity, destination_path = self._fixture._prepare_countries_metadata(source_file_path, file_format, destination_file_name = destination_file_name, recreate_tables = True, with_primary_key = True, consolidation_mode = Constants.CONSOLIDATION_MODE_SNAPSHOT)
     
    #ACT
    #Insert
    self.execute_tabular_ingestion(destination_path)
    
    #Update
    destination_path = self._fixture.get_full_storage_destination_path(destination_file_name, entity, provider.provider_name) #Update date
    self._fixture.move_file_to_execution_storage(update_source, destination_path)
    self.execute_tabular_ingestion(destination_path)
   
    #ASSERT
    #Data is extracted
    self._spark.catalog.setCurrentDatabase(provider.database_name)
    result = self._spark.sql(f"SELECT COUNT(*) as rows FROM {entity.table_name.lower()}")
    value = result.select("rows").collect()
    count = value[0].asDict()["rows"]
    
    if(count != expected_rows):
      self._logger.warning(f"[E2E_ConsolidationModeSnapshotTest][test_update] FAILED. Expected errors: {expected_rows}. Actual errors: {count}. Source file path: {source_file_path}, file format: {file_format}, destination file name: {destination_file_name}, update source: {update_source}")
      
    self.assertEqual(count, expected_rows)
    
    
  @parameterized.expand([
  ('files/countries_insert.parquet', "parquet", "countries.parquet", "files/countries_update.parquet", 300),
  ('files/countries_insert.csv', "csv", "countries.csv", 'files/countries_update.csv', 300),
  ('files/countries_insert.xls', "xls", "countries.xls",  'files/countries_update.xls', 300),
  ('files/countries_insert.xlsm', "xlsm", "countries.xlsm",  'files/countries_update.xlsm', 300),
  ('files/countries_insert.xlsx', "xlsx", "countries.xlsx",  'files/countries_update.xlsx', 300)
  ])
  def test_no_metadata_and_partition_fields(self, source_file_path, file_format, destination_file_name, update_source, expected_rows):
    #ARRANGE
    attributes = []
    attribute_builder = AttributeBuilder()
    attributes.append(attribute_builder.with_name("Name").with_is_primary_key(False).build())
    attributes.append(attribute_builder.with_name("Code").with_is_primary_key(False).build())
    provider, entity, destination_path = self._fixture._prepare_countries_metadata(source_file_path, file_format, destination_file_name = destination_file_name, recreate_tables = True, with_primary_key = True, entity_attributes = attributes, consolidation_mode = Constants.CONSOLIDATION_MODE_SNAPSHOT)
     
    #ACT
    #Insert
    self.execute_tabular_ingestion(destination_path)
    
    #Update
    destination_path = self._fixture.get_full_storage_destination_path(destination_file_name, entity, provider.provider_name) #Update date
    self._fixture.move_file_to_execution_storage(update_source, destination_path)
    self.execute_tabular_ingestion(destination_path)
   
    #ASSERT
    #Data is extracted
    self._spark.catalog.setCurrentDatabase(provider.database_name)
    result = self._spark.sql(f"SELECT COUNT(*) as rows FROM {entity.table_name.lower()}")
    value = result.select("rows").collect()
    count = value[0].asDict()["rows"]
    
    if(count != expected_rows):
      self._logger.warning(f"[E2E_ConsolidationModeSnapshotTest][test_no_metadata_and_partition_fields] FAILED. Expected errors: {expected_rows}. Actual errors: {count}. Source file path: {source_file_path}, file format: {file_format}, destination file name: {destination_file_name}, update source: {update_source}")
      
    self.assertEqual(count, expected_rows)
  
  @parameterized.expand([
  ('files/countries_insert.parquet', "parquet", 249),
  ])
  def test_insert_with_assets_is_full_extract(self, source_file_path, file_format, expected_rows):
     #ARRANGE
    provider, entity, destination_path = self._fixture._prepare_countries_metadata(source_file_path, file_format, recreate_tables = True, with_primary_key = True, consolidation_mode = Constants.CONSOLIDATION_MODE_SNAPSHOT)
    #Data table is created
    self.assertTrue(E2EUtils.get_table(self._spark, provider.database_name, entity.table_name.lower()))  
    
    #ACT
    #Insert
    self.execute_tabular_ingestion(destination_path, assetIsFullExtract = True)
    
    #ASSERT
    #Asset is created
    assets = self._fixture._asset_service.get_recent_entity_assets(entity.id)
    self.assertTrue(assets) #Check that assets is not empty array, so an asset has been created for the entity
   
    #Data is extracted
    self._spark.catalog.setCurrentDatabase(provider.database_name)
    result = self._spark.sql(f"SELECT COUNT(*) as rows FROM {entity.table_name.lower()}")
    value = result.select("rows").collect()
    count = value[0].asDict()["rows"]
    
    if(count != expected_rows):
      self._logger.warning(f"""[E2E_ConsolidationModeSnapshotTest][test_insert_with_assets_is_full_extract] FAILED. Expected errors: {expected_rows}. Current errors: {count}. Source file path: {source_file_path}, file format: {file_format}""")
      
    self.assertEqual(count, expected_rows)  



class TestE2EConsolidationModeMerge(TestE2EBase):
  @parameterized.expand([
  ('files/countries_insert.parquet', "parquet", 249),
  ('files/countries_insert.csv', "csv", 249),
  ('files/countries_insert.xls', "xls", 249),
  ('files/countries_insert.xlsm', "xlsm", 249),
  ('files/countries_insert.xlsx', "xlsx", 249)
  ])
  def test_insert(self, source_file_path, file_format, expected_rows):
    #ARRANGE
    provider, entity, destination_path = self._fixture._prepare_countries_metadata(source_file_path, file_format, recreate_tables = True, with_primary_key = True, consolidation_mode = Constants.CONSOLIDATION_MODE_MERGE)
    #Data table is created
    self.assertTrue(E2EUtils.get_table(self._spark, provider.database_name, entity.table_name.lower()))
    
    #ACT
    #Insert
    self.execute_tabular_ingestion(destination_path)
    
    #ASSERT
    #Asset is created
    assets = self._fixture._asset_service.get_recent_entity_assets(entity.id)
    self.assertTrue(assets)#Check that assets is not empty array, so an asset has been created for the entity
   
    #Data is extracted
    self._spark.catalog.setCurrentDatabase(provider.database_name)
    result = self._spark.sql(f"SELECT COUNT(*) as rows FROM {entity.table_name.lower()}")
    value = result.select("rows").collect()
    count = value[0].asDict()["rows"]
    
    if(count != expected_rows):
      self._logger.warning(f"[E2E_ConsolidationModeMergeTest][test_insert] FAILED. Expected errors: {expected_rows}. Actual errors: {count}. Source file path: {source_file_path}, file format: {file_format}")
      
    self.assertEqual(count, expected_rows)
    
  @parameterized.expand([
   ("parquet 2 assets",'files/countries_insert.parquet', "parquet", "countries.parquet", 2, 249),
   ("parquet 5 assets",'files/countries_insert.parquet', "parquet", "countries.parquet", 5, 249),
   ("csv 2 assets",'files/countries_insert.csv', "csv", "countries.csv", 2, 249),
   ("csv 5 assets",'files/countries_insert.csv', "csv", "countries.csv", 5, 249),
  ])  
  def test_multiple_insert_full_load_same_content_different_date(self, _, source_file_path : str, file_format :str, destination_path : str, iterations : int, expected_rows : int):
    #ARRANGE
    provider, entity, destination_path = self._fixture._prepare_countries_metadata(source_file_path, file_format, recreate_tables = True, with_primary_key = True, consolidation_mode = Constants.CONSOLIDATION_MODE_MERGE)

    #ACT
    counter = 0
    while counter < iterations:
      destination_path = self._fixture.get_full_storage_destination_path(source_file_path, entity, provider.provider_name)
      self._fixture.move_file_to_execution_storage(source_file_path, destination_path)
      self.execute_tabular_ingestion(destination_path)
      time.sleep(2)
      counter += 1

    #ASSERT
    #Asset is created
    assets = self._fixture._asset_service.get_recent_entity_assets(entity.id)
    self.assertTrue(assets)#Check that assets is not empty array, so an asset has been created for the entity
    self.assertTrue(len(assets) == iterations)
    
    #Data is extracted
    self._spark.catalog.setCurrentDatabase(provider.database_name)
    result = self._spark.sql(f"SELECT COUNT(*) as rows FROM {entity.table_name.lower()}")
    value = result.select("rows").collect()
    count = value[0].asDict()["rows"]
    
    if(count != expected_rows):
      self._logger.warning(f"[E2E_ConsolidationModeMergeTest][test_multiple_insert_full_load_same_content_different_date] FAILED. Expected errors: {expected_rows}. Actual errors: {count}. Source file path: {source_file_path}, file format: {file_format}, destination path {destination_path}")

    self.assertEqual(count, expected_rows)
    
    #different sources
    self._spark.catalog.setCurrentDatabase(provider.database_name)
    result = self._spark.sql(f"SELECT COUNT(DISTINCT {Constants.ATTRIBUTE_NAME_ASSET_ID}) as rows FROM {entity.table_name.lower()}")
    value = result.select("rows").collect()
    count = value[0].asDict()["rows"]
    self.assertEqual(count, 1)
    
  @parameterized.expand([
   ("parquet 2 assets",'files/countries_insert.parquet', "parquet", "countries.parquet", 2, 249),
   ("parquet 5 assets",'files/countries_insert.parquet', "parquet", "countries.parquet", 5, 249),
   ("csv 2 assets",'files/countries_insert.csv', "csv", "countries.csv", 2, 249),
   (" csv 5 assets",'files/countries_insert.csv', "csv", "countries.csv", 5, 249),
  ])  
  def test_multiple_insert_full_load_same_content_same_date(self, _, source_file_path : str, file_format :str, destination_file_name : str, iterations : int, expected_rows : int):
    #ARRANGE
    provider, entity, destination_path = self._fixture._prepare_countries_metadata(source_file_path, file_format, destination_file_name = destination_file_name, recreate_tables = True, with_primary_key = True, consolidation_mode = Constants.CONSOLIDATION_MODE_MERGE)
     
    #ACT
    #Insert
    self.execute_tabular_ingestion(destination_path)
    
    time.sleep(2)
    self._fixture.move_file_to_execution_storage(source_file_path, destination_path)
    #Insert same file
    self.execute_tabular_ingestion(destination_path)
   
    #ASSERT
    #Data is extracted
    self._spark.catalog.setCurrentDatabase(provider.database_name)
    result = self._spark.sql(f"SELECT COUNT(*) as rows FROM {entity.table_name.lower()}")
    value = result.select("rows").collect()
    count = value[0].asDict()["rows"]

    if(count != expected_rows):
      self._logger.warning(f"[E2E_ConsolidationModeMergeTest][test_multiple_insert_full_load_same_content_same_date] FAILED. Expected errors: {expected_rows}. Actual errors: {count}. Source file path: {source_file_path}, file format: {file_format}, destination file name {destination_file_name}")

    self.assertEqual(count, expected_rows)
    
  @parameterized.expand([
  ('files/countries_insert.parquet', "parquet", "countries.parquet", "files/countries_update.parquet", 249),
  ('files/countries_insert.csv', "csv", "countries.csv", 'files/countries_update.csv', 249),
  ('files/countries_insert.xls', "xls", "countries.xls",  'files/countries_update.xls', 249),
  ('files/countries_insert.xlsm', "xlsm", "countries.xlsm",  'files/countries_update.xlsm', 249),
  ('files/countries_insert.xlsx', "xlsx", "countries.xlsx",  'files/countries_update.xlsx', 249)
  ])
  def test_update(self, source_file_path, file_format, destination_file_name, update_source, expected_rows):
    #ARRANGE
    provider, entity, destination_path = self._fixture._prepare_countries_metadata(source_file_path, file_format, consolidation_mode = Constants.CONSOLIDATION_MODE_MERGE, destination_file_name = destination_file_name, recreate_tables = True, with_primary_key = True)
     
    #ACT
    #Insert
    self.execute_tabular_ingestion(destination_path)
    
    #Update
    destination_path = self._fixture.get_full_storage_destination_path(destination_file_name, entity, provider.provider_name) #Update date
    self._fixture.move_file_to_execution_storage(update_source, destination_path)
    self.execute_tabular_ingestion(destination_path)
   
    #ASSERT
    #Data is extracted
    self._spark.catalog.setCurrentDatabase(provider.database_name)
    result = self._spark.sql(f"SELECT COUNT(*) as rows FROM {entity.table_name.lower()}")
    value = result.select("rows").collect()
    count = value[0].asDict()["rows"]
    
    if(count != expected_rows):
      self._logger.warning(f"[E2E_ConsolidationModeMergeTest][test_update] FAILED. Expected errors: {expected_rows}. Current errors: {count}. Source file path: {source_file_path}, file format: {file_format}, destination file name {destination_file_name}, update source: {update_source}")
      
    self.assertEqual(count, expected_rows)
  
  
def run_tests():
  # initialize the test suite
  loader = unittest.TestLoader()
  suite  = unittest.TestSuite()

  # add tests to the test suite
  suite.addTests(loader.loadTestsFromTestCase(testCaseClass=TestE2EConsolidationModeSnapshot))
  suite.addTests(loader.loadTestsFromTestCase(testCaseClass=TestE2EConsolidationModeMerge))

  # initialize a runner, pass it your suite and run it
  runner = xmlrunner.XMLTestRunner(verbosity=3, descriptions=True, output='/dbfs/runtests/E2E-ConsolidationMode_Report')
  result = runner.run(suite)

  # print chart
  Utils.print_pie_chart_tests(len(result.successes), len(result.failures), len(result.errors), len(result.skipped))

  assert len(result.failures) == 0
  assert len(result.errors) == 0