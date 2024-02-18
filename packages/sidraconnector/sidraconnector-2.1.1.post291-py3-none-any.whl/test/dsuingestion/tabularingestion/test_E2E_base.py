import unittest
from datetime import datetime
from sidraconnector.sdk.log.logging import Logger
from test.fixture import AzureStorageFixture, Fixture
from sidraconnector.sdk.databricks.utils import Utils as DatabricksUtils
from sidraconnector.sdk.databricks.dsuingestion.tabularingestion import TabularIngestion
from pyspark.sql import SparkSession

class TestE2EBase(unittest.TestCase):
  _spark = SparkSession.builder.getOrCreate()
  _logger = Logger(_spark, 'Test_DSUIngestion_E2E')
  _logger.set_level('DEBUG')
  _fixture =  Fixture(_spark, _logger)
  _storage_fixture = AzureStorageFixture(_spark, _logger) 
  _dbutils = DatabricksUtils(_spark).get_db_utils()
  
  @classmethod
  def setUpClass(cls): 
    cls._storage_fixture = AzureStorageFixture(cls._spark, cls._logger)
    cls._logger.debug(f"[Tabular Ingestion] Test E2E: Setting up Test class")
    cls._fixture = Fixture(cls._spark, cls._logger)
   
  def tearDown(self):
    self._logger.debug(f"[Tabular Ingestion] Test E2E: Tearing down Test")
    self._fixture.cleanup()

  def get_suffix(self) -> str:
    return datetime.now().strftime('%Y%m%d%H%M%S%f')      

  def execute_tabular_ingestion(self, file_path :str, assetDate : str = None, assetId : int = None,  assetIsFullExtract : bool = False):
      fileUri = self._storage_fixture.get_destination_file_absolute_uri(file_path)
      tabular_ingestion = TabularIngestion(self._spark)
      tabular_ingestion.process(asset_id=assetId, asset_uri=fileUri, asset_is_full_extract=assetIsFullExtract)
