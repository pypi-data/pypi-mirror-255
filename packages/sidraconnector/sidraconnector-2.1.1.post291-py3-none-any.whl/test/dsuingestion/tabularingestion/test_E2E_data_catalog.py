import unittest
import pandas as pd
from parameterized import parameterized, parameterized_class
from test.utils import Utils
from test.dsuingestion.tabularingestion.test_E2E_base import TestE2EBase
import sidraconnector.sdk.constants as Constants
import xmlrunner

class TestE2EDataCatalog(TestE2EBase):
  @parameterized.expand([
  ('files/countries_insert.parquet', "parquet"),
  ('files/countries_insert.csv', "csv"),
  ('files/countries_insert.xls', "xls"),
  ('files/countries_insert.xlsm', "xlsm"),
  ('files/countries_insert.xlsx', "xlsx")
  ])
  def test_data_data_catalog(self, insert_file_path, file_format):
     #ARRANGE
    provider, entity, destination_path = self._fixture._prepare_countries_metadata(insert_file_path, file_format, consolidation_mode = Constants.CONSOLIDATION_MODE_MERGE, with_data_preview = True, recreate_tables = True, with_primary_key = True)
    
    #ACT
    self.execute_tabular_ingestion(destination_path)
    
    #ASSERT
    jdbcUrl = self._dbutils.secrets.get(scope = "jdbc", key = "coreJdbcDbConnectionString").replace("yes", "true")
    result = self._spark.read \
      .format("jdbc") \
      .option("url", jdbcUrl) \
      .option("query", f"SELECT COUNT(*) as rows FROM DataPreview.{entity.table_name}").load().toPandas()
    df = pd.DataFrame(result, columns = ['rows'])

    rows_count = df['rows'].values[0]
    
    if(rows_count != Constants.DATACATALOG_SAMPLE_NUMBER_RECORDS):
      self._logger.warning(f"[E2E_DataCatalogTest][test_data_data_catalog] FAILED. Sample records: {Constants.DATACATALOG_SAMPLE_NUMBER_RECORDS}. Rows count: {rows_count}. Insert file path: {insert_file_path}, file format: {file_format}")
      
    self.assertEqual(rows_count, Constants.DATACATALOG_SAMPLE_NUMBER_RECORDS)

def run_tests():

  loader = unittest.TestLoader()
  suite  = unittest.TestSuite()

  # add tests to the test suite
  suite.addTests(loader.loadTestsFromTestCase(testCaseClass=TestE2EDataCatalog))

  # initialize a runner, pass it your suite and run it
  runner = xmlrunner.XMLTestRunner(verbosity=3, descriptions=True, output='/dbfs/runtests/E2E-DataCatalog_Report')
  result = runner.run(suite)

  # print chart
  Utils.print_pie_chart_tests(len(result.successes), len(result.failures), len(result.errors), len(result.skipped))

  assert len(result.failures) == 0
  assert len(result.errors) == 0