import json
import unittest
from sidraconnector.sdk.databricks.reader.readerservice import ReaderService
from sidraconnector.sdk.databricks.utils import Utils as DatabricksUtils
from sidraconnector.sdk.metadata.models.builders import EntityBuilder, ReaderPropertiesBuilder
from sidraconnector.sdk.log.logging import Logger
from test.fixture import AzureStorageFixture
import xmlrunner
from parameterized import parameterized


from test.utils import Utils as TestUtils
from pyspark.sql import SparkSession

class TestDsuIngestionReaderService(unittest.TestCase):
  _spark = SparkSession.builder.getOrCreate()
  _logger = Logger(_spark,'Test_DSUIngestion_E2E')
  _logger.set_level('DEBUG')
  _storage_container = 'dsuingestion'
  _dbutils = DatabricksUtils(_spark).get_db_utils()
  _storage_account = _dbutils.secrets.get(scope='resources', key='additional_storage_account_name')
  _fixture = AzureStorageFixture(_spark, _logger, _storage_container)
 
  @classmethod
  def tearDownClass(cls):
    cls._fixture.teardown()
    
  def tearDown(self):
    self._fixture.cleanup()

  def test_should_read_parquet_file(self):
    # Arrange
    filename = 'files/countries.parquet'
    destination_filename = self._fixture.copy_file_from_testing_resources(filename, filename) # Same source and destination filename
    wasbs_filename = f'wasbs://{self._storage_container}@{self._storage_account}.blob.core.windows.net/{filename}'
    entity = EntityBuilder().build()    
      
    # Act
    service = ReaderService(self._spark, self._logger)
    df = service._spark_generic_reader(wasbs_filename, entity)
    
    # Assert
    self.assertTrue(df.count() != 0)

  @parameterized.expand([
    (None, None, {"inferSchema":False}),
    (0, None, {"inferSchema": False, "header": False}),
    (1, None, {"inferSchema": False, "header": True}),   
    (0, '{"delimiter": "\\u0009"}', {"inferSchema": False, "header": False, "delimiter": '\u0009'}),
    (1, '{"encoding": "UTF-8"}', {"inferSchema": False, "header": True, "encoding": 'UTF-8'}),
    (1, '{"separatorChar": "\\u002c", "escapeChar": "\\u0002"}', {"inferSchema": False, "header": True, "separatorChar": "\u002c", "escapeChar": "\u0002"}),
    (0, '{"delimiter": "\\u0009", "encoding": "UTF-8", "separatorChar": "\\u002c"}', {"inferSchema": False, "header": False, "delimiter": '\u0009', "encoding": 'UTF-8', "separatorChar": "\u002c"}),
    (42, None, {"inferSchema": False, "header": False}),
    (42, '{"delimiter": ","}', {"inferSchema": False, "header": False, "delimiter": ','}),
    (None, '{"header": true}', {"inferSchema": False, "header": True}),
    (1, '{"header": false}', {"inferSchema": False, "header": False}), # Value in reader_options if exists overwrite the one in specific field
    (0, '{"header": true}', {"inferSchema": False, "header": True}), # Value in reader_options if exists overwrite the one in specific field
    (3, '{"header": true}', {"inferSchema": False, "header": False}), # Header is true but there are 3 lines, we read the file as no header and remove the lines later
    (3, '{"header": false}', {"inferSchema": False, "header": False}), # Value in reader_options if exists overwrite the one in specific field
  ])
  def test_should_return_csv_reader_options(self, header_lines, reader_options, expected_result):
    # Arrange
    reader_options_json = json.loads('{}') if reader_options is None else json.loads(reader_options)
    reader_properties = ReaderPropertiesBuilder().with_header_lines(header_lines).with_reader_options(reader_options_json).build()
    entity = EntityBuilder().with_reader_properties(reader_properties).build()
    
    # Act
    service = ReaderService(self._spark, self._logger)
    actual = service._get_csv_reader_options(entity)
    
    # Assert
    self.maxDiff = None
    self.assertEqual(actual, expected_result)
  
  @parameterized.expand([
    ('files/countries.csv', 1, None, 249),
    ('files/countries.csv', 5, '{"header": true}', 245),
    ('files/countries.csv', 5, '{"header": false}', 250),
    ('files/countries.csv', 1, '{"separatorChar": "\\u002c"}', 249),
    ('files/countries.csv', None, '{"header": true}', 249),
    ('files/countriesColumnsWithSpaces.csv', 1, None, 249),
  ])
  def test_should_read_csv_file(self, filename, header_lines, reader_options, expected_total_lines):
    # Arrange
    reader_options_json = json.loads('{}') if reader_options is None else json.loads(reader_options)
    self._fixture.copy_file_from_testing_resources(filename, filename) # Same source and destination filename
    wasbs_filename = f'wasbs://{self._storage_container}@{self._storage_account}.blob.core.windows.net/{filename}'
    reader_properties = ReaderPropertiesBuilder().with_header_lines(header_lines).with_reader_options(reader_options_json).with_file_format('csv').build()     
    entity = EntityBuilder().with_reader_properties(reader_properties).build()
      
    # Act
    service = ReaderService(self._spark, self._logger)
    df = service._spark_csv_reader(wasbs_filename, entity)
    
    # Assert
    self.assertEqual(df.count(), expected_total_lines)
    
  @parameterized.expand([('null', 0),(0, 1),(3, 4)])
  def test_should_read_xls_file(self, header_index, total_header_lines):
    # Arrange
    total_lines = 250
    filename = 'files/countries.xls'
    self._fixture.copy_file_from_testing_resources(filename, filename) # Same source and destination filename
    wasbs_filename = f'wasbs://{self._storage_container}@{self._storage_account}.blob.core.windows.net/{filename}'    
    reader_options_json = json.loads(f'{{"header":{header_index}}}')    
    reader_properties = ReaderPropertiesBuilder().with_file_format('xls').with_reader_options(reader_options_json).build()
    entity = EntityBuilder().with_reader_properties(reader_properties).build()

    # Act
    service = ReaderService(self._spark, self._logger)
    df = service._pandas_excel_reader(wasbs_filename, entity)
                        
    # Assert
    self.assertIsNotNone(df)
    self.assertEqual(df.count(), total_lines-total_header_lines)  
    
  @parameterized.expand([('files/countries.xlsx', 'xlsx')
                         ,('files/countries.xlsm', 'xlsm')])
  def test_should_read_xlsx_and_xlsm_file(self, filename, file_format):
    # Arrange
    total_lines = 250
    self._fixture.copy_file_from_testing_resources(filename, filename) # Same source and destination filename
    wasbs_filename = f'wasbs://{self._storage_container}@{self._storage_account}.blob.core.windows.net/{filename}'       
    reader_options_json = json.loads('{"header": true}')
    reader_properties = ReaderPropertiesBuilder().with_reader_options(reader_options_json).with_file_format(file_format).build()
    entity = EntityBuilder().with_reader_properties(reader_properties).build()

    # Act
    service = ReaderService(self._spark, self._logger)
    df = service._spark_generic_reader(wasbs_filename, entity, 'com.crealytics.spark.excel')
                        
    # Assert
    self.assertIsNotNone(df)
    self.assertEqual(df.count(), total_lines-1)   
    
  # Old serde properties definition was:
  # - For xlsx and xlsm: '"header" = True'
  # - For xls: 'header=0'
  # - For csv: 'header=True'
  @parameterized.expand([
     ('files/countries.xlsx', 'xlsx', '{"header": true}')
    ,('files/countries.xlsm', 'xlsm', '{"header": false}')
    ,('files/countries.xls',  'xls',  '{"header": 0}')
    ,('files/countries.csv',  'csv',  '{"header": true}')
    ,('files/countries.parquet', 'parquet', None)
  ])
  def test_should_read_file(self, filename, file_format, reader_options):
    # Arrange
    self._fixture.copy_file_from_testing_resources(filename, filename) # Same source and destination filename
    wasbs_filename = f'wasbs://{self._storage_container}@{self._storage_account}.blob.core.windows.net/{filename}'  
    reader_options_json = json.loads('{}') if reader_options is None else json.loads(reader_options)
    reader_properties = ReaderPropertiesBuilder().with_file_format(file_format).with_reader_options(reader_options_json).build()
    entity = EntityBuilder().with_reader_properties(reader_properties).build()

    # Act
    service = ReaderService(self._spark, self._logger)
    df = service.read_file(wasbs_filename, entity)
                        
    # Assert
    self.assertIsNotNone(df)
    self.assertTrue(df.count() != 0)
    
  @parameterized.expand([
     ('files/countries.xlsx', 'xlsx')
    ,('files/countries.xlsm', 'xlsm')
    ,('files/countries.csv',  'csv')
    ,('files/countries.parquet', 'parquet')
  ])    
  def test_not_fail_if_there_are_unexpected_properties_int_reader_options_using_spark(self, filename, fileformat):   
    # Arrange
    self._fixture.copy_file_from_testing_resources(filename, filename) # Same source and destination filename
    wasbs_filename = f'wasbs://{self._storage_container}@{self._storage_account}.blob.core.windows.net/{filename}'  
    reader_options_json = json.loads('{"nokey": 1}')
    reader_properties = ReaderPropertiesBuilder().with_file_format(fileformat).with_reader_options(reader_options_json).build()
    entity = EntityBuilder().with_reader_properties(reader_properties).build()
    
    # Act
    service = ReaderService(self._spark, self._logger)
    df = service.read_file(wasbs_filename, entity)
    
    # Assert
    self.assertIsNotNone(df)
    self.assertTrue(df.count() != 0)
    
  @parameterized.expand([
    ('files/countries.xls',  'xls')    
  ])    
  def test_fail_if_there_are_unexpected_properties_int_reader_options_using_pandas(self, filename, fileformat):   
    # Arrange
    self._fixture.copy_file_from_testing_resources(filename, filename) # Same source and destination filename
    wasbs_filename = f'wasbs://{self._storage_container}@{self._storage_account}.blob.core.windows.net/{filename}' 
    reader_options_json = json.loads('{"nokey": 1}')
    reader_properties = ReaderPropertiesBuilder().with_file_format(fileformat).with_reader_options(reader_options_json).build()
    entity = EntityBuilder().with_reader_properties(reader_properties).build()
    
    # Act/Assert
    service = ReaderService(self._spark, self._logger)
    with self.assertRaises(Exception) as context:
      service.read_file(wasbs_filename, entity)
    
    error_message = f"got an unexpected keyword argument 'nokey'"
    self.assertTrue(error_message in str(context.exception)) 


def run_tests():
  loader = unittest.TestLoader()
  suite  = unittest.TestSuite()

  # add tests to the test suite
  suite.addTests(loader.loadTestsFromTestCase(testCaseClass=TestDsuIngestionReaderService))

  # initialize a runner, pass it your suite and run it
  runner = xmlrunner.XMLTestRunner(verbosity=3, descriptions=True, output='/dbfs/runtests/ReaderService_Report')
  result = runner.run(suite)

  # print chart
  TestUtils.print_pie_chart_tests(len(result.successes), len(result.failures), len(result.errors), len(result.skipped))

  # ensure job failed if there are issues
  assert len(result.failures) == 0
  assert len(result.errors) == 0
