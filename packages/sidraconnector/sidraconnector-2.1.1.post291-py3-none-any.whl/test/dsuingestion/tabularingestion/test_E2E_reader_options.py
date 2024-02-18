import unittest
from test.dsuingestion.tabularingestion.test_E2E_base import TestE2EBase
from test.utils import Utils
from sidraconnector.sdk.metadata.models.builders import *
import xmlrunner
import parameterized
from parameterized import parameterized

import unittest

class TestE2EReaderOptions(TestE2EBase):
  @parameterized.expand([
  ('files/countries.csv', "csv", 1, {"header":True, "fakeProperty1":"value", "fakeProperty2":True}, False),
  ('files/countries.csv', "csv", 1, {"header":True, "sep":",", "fakeProperty1":"value", "fakeProperty2":True}, False),
  ('files/countries.csv', "csv", 1, {"header":True, "sep":";", "fakeProperty1":"value", "fakeProperty2":True}, True),
  ('files/countries.xls', "xls", 1, {"header":0, "fakeProperty1":"value"}, True),
  ('files/countries.xlsx', "xlsx", 1, {"header":True, "fakeProperty1":"value", "fakeProperty2":True}, False),
  ('files/countries.xlsm', "xlsm", 1, {"header":True, "fakeProperty1":"value", "fakeProperty2":True}, False)
  ])
  def test_not_valid_reader_options_values(self, source_file : str, source_file_extension : str, header_lines : int, reader_options :str, should_fail : bool):
    # ARRANGE
    source_file_name_no_extension = self._fixture._get_file_name_no_extension_from_path(source_file)
    ####Entity
    
    reader_properties = ReaderPropertiesBuilder().with_reader_options(reader_options).with_header_lines(header_lines).with_file_format(source_file_extension).build()
    
    attributes = []
    load_properties = AttributeLoadPropertiesBuilder().build()
    attributes.append(AttributeBuilder().with_name("Name").with_is_primary_key(False).with_load_properties(load_properties).build())
    attributes.append(AttributeBuilder().with_name("Code").with_is_primary_key(True).build())
    
    provider, entity, destination_path = self._fixture._prepare_countries_metadata(source_file, source_file_extension, entity_reader_properties = reader_properties, entity_attributes = attributes)
    #ACT
    if should_fail:
      with self.assertRaises(Exception) as context:
        self.execute_tabular_ingestion(destination_path)
    else:
        self.execute_tabular_ingestion(destination_path)
        
  
  @parameterized.expand([
    ('files/countries-serde-properties.csv', "csv", "countries-serde-properties.csv", {"delimiter": ";", "encoding": "UTF-8", "header": True, "multiLine": True }),
    ('files/countries-serde-properties2.csv', "csv", "countries-serde-properties2.csv", {"delimiter": ";", "encoding": "UTF-8", "header": True, "multiLine": True, "lineSep": "¦"}),
  ])
  def test_should_read_file_using_correct_reader_options(self, source_file_path : str, file_format :str, destination_path : str, reader_options : str):
    #ARRANGE
    expected_name1 = """Congo;
	the Democratic Republic of the"""
    expected_name2 = "Réunion"
    entity_reader_properties = ReaderPropertiesBuilder().with_reader_options(reader_options).with_file_format(file_format).build()
    provider, entity, destination_path = self._fixture._prepare_countries_metadata(source_file_path, file_format, recreate_tables = True, with_primary_key = True, entity_reader_properties = entity_reader_properties)
    
    #ACT
    self.execute_tabular_ingestion(destination_path)

    #ASSERT  
    #Data extracted is as expected
    result = self._spark.sql(f"SELECT Name FROM {provider.database_name}.{entity.table_name.lower()}")
    value = result.select("Name").collect()
    actual = value[0].asDict()["Name"]
    self.assertEqual(actual, expected_name1)
    actual = value[1].asDict()["Name"]
    self.assertEqual(actual, expected_name2)
    
  @parameterized.expand([
  ('files/countries-ANSI.csv', "csv", "countries-ANSI.csv", "ISO-8859-1", True),
  ('files/countries-ANSI.csv', "csv", "countries-ANSI.csv", "UTF-8", False),
  ('files/countries-UTF-8.csv', "csv", "countries-UTF-8.csv", "UTF-8", True)
  ])
  def test_should_read_file_using_correct_encoding(self, source_file_path : str, file_format :str, destination_path : str, encoding : str, is_correct: bool):
    #ARRANGE
    expected_name = "Réunion"
    reader_options = {"header":True, "encoding": f"{encoding}"}
    entity_reader_properties = ReaderPropertiesBuilder().with_reader_options(reader_options).with_file_format(file_format).build()
    
    provider, entity, destination_path = self._fixture._prepare_countries_metadata(source_file_path, file_format, recreate_tables = True, with_primary_key = True, entity_reader_properties = entity_reader_properties)

    #ACT
    self.execute_tabular_ingestion(destination_path)

    #ASSERT  
    #Data extracted is as expected
    result = self._spark.sql(f"SELECT Name FROM {provider.database_name}.{entity.table_name.lower()}")
    value = result.select("Name").collect()
    actual = value[0].asDict()["Name"]
    if is_correct is True:
      self.assertEqual(actual, expected_name)
    else:
      self.assertNotEqual(actual, expected_name)
      
  
  @parameterized.expand([
  ('files/countries.csv', "csv", 0, {"header":True}, 249),
  ('files/countries.csv', "csv", 0, {"header":False}, 250),
  ('files/countries.csv', "csv", 0, {}, 250),
  ('files/countries.csv', "csv", 1, {"header":True}, 249),
  ('files/countries.csv', "csv", 1, {}, 249),
  ('files/countries.csv', "csv", 1, {"header":False}, 250),
  ('files/countries.csv', "csv", 2, {"header":True}, 248),
  ('files/countries.csv', "csv", 2, {}, 250),
  ('files/countries.csv', "csv", 2, {"header":False}, 250)
  ])      
  def test_should_overwrite_header_lines_from_reader_options_value(self, source_file : str, source_file_extension : str, header_lines : int, reader_options :dict, expected_rows : int):
    
     # ARRANGE
    source_file_name_no_extension = self._fixture._get_file_name_no_extension_from_path(source_file)
    ####Entity
    
    reader_properties = ReaderPropertiesBuilder().with_reader_options(reader_options).with_header_lines(header_lines).with_file_format(source_file_extension).build()
    
    attributes = []
    load_properties = AttributeLoadPropertiesBuilder().build()
    attributes.append(AttributeBuilder().with_name("Name").with_is_primary_key(False).with_load_properties(load_properties).build())
    attributes.append(AttributeBuilder().with_name("Code").with_is_primary_key(True).build())
    
    provider, entity, destination_path = self._fixture._prepare_countries_metadata(source_file, source_file_extension, entity_reader_properties = reader_properties, entity_attributes = attributes)
    #ACT
    self.execute_tabular_ingestion(destination_path)
    
    #ASSERT  
    result = self._spark.sql(f"SELECT COUNT(*) as rows FROM {provider.database_name}.{entity.table_name.lower()}")
    value = result.select("rows").collect()
    current_rows = value[0].asDict()["rows"]
    self.assertEqual(current_rows, expected_rows)

def run_tests():

  loader = unittest.TestLoader()
  suite  = unittest.TestSuite()

  # add tests to the test suite
  suite.addTests(loader.loadTestsFromTestCase(testCaseClass=TestE2EReaderOptions))

  # initialize a runner, pass it your suite and run it
  runner = xmlrunner.XMLTestRunner(verbosity=3, descriptions=True, output='/dbfs/runtests/E2E-ReaderOptions_Report')
  result = runner.run(suite)

  # print chart
  Utils.print_pie_chart_tests(len(result.successes), len(result.failures), len(result.errors), len(result.skipped))

  assert len(result.failures) == 0
  assert len(result.errors) == 0
