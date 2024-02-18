import unittest
from test.dsuingestion.tabularingestion.test_E2E_base import TestE2EBase
from test.dsuingestion.tabularingestion.utils import Utils as Utils
from test.utils import Utils as TestUtils
import sidraconnector.sdk.constants as Constants
import xmlrunner
from parameterized import parameterized, parameterized_class

class TestE2ERegisteredAsset(TestE2EBase):
  @parameterized.expand([
  ('files/countries_insert.parquet', "parquet", 249),
  ('files/countries_insert.csv', "csv", 249),
  ('files/countries_insert.xls', "xls", 249),
  ('files/countries_insert.xlsm', "xlsm", 249),
  ('files/countries_insert.xlsx', "xlsx", 249)])
  def test_insert(self, source_file_path, file_format, expected_rows):
    #ARRANGE
    provider, entity, destination_path = self._fixture._prepare_countries_metadata(source_file_path, file_format, recreate_tables = True, with_primary_key = True, consolidation_mode = Constants.CONSOLIDATION_MODE_SNAPSHOT)
    #Data table is created
    self.assertTrue(Utils.get_table(self._spark, provider.database_name, entity.table_name.lower()))
    full_source_path = self._storage_fixture.get_destination_file_absolute_uri(destination_path)
    registered_asset =  self._fixture._asset_service.register_asset(full_source_path)
    self._logger.info(f"REGISTERED ASSET: {registered_asset}")
    #Asset is created
    assets = self._fixture._asset_service.get_recent_entity_assets(entity.id)
    self.assertTrue(assets)#Check that assets is not empty array, so an asset has been created for the entity
       
    #ACT
    #Insert
    self.execute_tabular_ingestion(destination_path, assetId=registered_asset.asset_id)
        
    #ASSERT
    #Data is extracted
    self._spark.catalog.setCurrentDatabase(provider.database_name)
    result = self._spark.sql(f"SELECT COUNT(*) as rows FROM {entity.table_name.lower()}")
    value = result.select("rows").collect()
    count = value[0].asDict()["rows"]
    self.assertEqual(count, expected_rows)
    
def run_tests():
  loader = unittest.TestLoader()
  suite  = unittest.TestSuite()
  # add tests to the test suite
  suite.addTests(loader.loadTestsFromTestCase(testCaseClass=TestE2ERegisteredAsset))
  # initialize a runner, pass it your suite and run it
  runner = xmlrunner.XMLTestRunner(verbosity=3, descriptions=True, output='/dbfs/runtests/E2E-RegisteredAsset_Report')
  result = runner.run(suite)
  # print chart
  TestUtils.print_pie_chart_tests(len(result.successes), len(result.failures), len(result.errors), len(result.skipped))
  
  assert len(result.failures) == 0
  assert len(result.errors) == 0