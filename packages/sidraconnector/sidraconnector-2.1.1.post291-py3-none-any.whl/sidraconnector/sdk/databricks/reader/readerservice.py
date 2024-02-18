import pandas as pd
from sidraconnector.sdk.databricks.utils import Utils
from sidraconnector.sdk.metadata.models.entitymodel import EntityModel
from pyspark.sql.types import *
from pyspark.sql.functions import *

class ReaderService():
  def __init__(self, spark, logger):
    self.logger = logger
    self.spark = spark
    self.databricks_utils = Utils(spark)        
    self.dbutils = self.databricks_utils.get_db_utils()    
  
  # -----------------
  # Reader Functions
  # -----------------
  def read_file(self, filename, entity : EntityModel):
    # TODO: Test for custome events but it is not working as expected, review and change the message
    properties = {'asset_properties': {'assetname': filename, 'asset_format': entity.reader_properties.file_format, 'entity_id': entity.id, 'entity_name': entity.name}}
    self.logger.add_extra_properties(properties)
    self.logger.debug(f"[ReaderService] Read File")
    
    file_format = entity.reader_properties.file_format
    if (file_format == 'csv'):
      return self._spark_csv_reader(filename, entity)
    elif (file_format == 'xls'):
      return self._pandas_excel_reader(filename, entity)
    elif (file_format == 'xlsx' or file_format == 'xlsm'):
      default_options = { "header": False }
      return self._spark_generic_reader(filename, entity, 'com.crealytics.spark.excel', default_options)
    elif (file_format == 'json'):
      df = self._spark_generic_reader(filename, entity, spark_reader = "parquet")
      df = df.select(*[to_json(col(col_name)).alias(col_name) if isinstance(df.schema[col_name].dataType, ArrayType) else col(col_name) for col_name in df.columns])
      return df
    return self._spark_generic_reader(filename, entity)
  
  def _spark_generic_reader(self, filename, entity : EntityModel, spark_reader= None, default_options = None):
    self.logger.debug(f"[ReaderService][_spark_generic_reader] Read File {filename}, entity: {entity}, spark_reader: {spark_reader}, default_options: {default_options}")
    reader_format = spark_reader if spark_reader is not None else entity.reader_properties.file_format
    if default_options is None:
      options = entity.reader_properties.reader_options
    else:
      default_options.update(entity.reader_properties.reader_options)
      options = default_options
      
    fileDF = self.spark.read.format(reader_format).options(**options).load(filename)
    return fileDF
  
  # Posible options: https://spark.apache.org/docs/3.1.2/api/python/reference/api/pyspark.sql.DataFrameReader.csv.html
  def _get_csv_reader_options(self, entity : EntityModel):
    options_dict = { "inferSchema": False }
    
    # If there is no header row or it is only one row, we can use default header option
    if (entity.reader_properties.header_lines == 0):
      options_dict["header"] = False
    else:
      if (entity.reader_properties.header_lines == 1):
        options_dict["header"] = True
        
    # Serde, SerdeProperties, RowDelimiter, FieldDelimiter y Encoding columns are deprecated.
    
    # Overwrite keys with the ones defined in reader_options
    options_dict.update(entity.reader_properties.reader_options)
    # if there are more than one row, define the option as no header and it will be treated after the file is read
    if (entity.reader_properties.header_lines is not None and entity.reader_properties.header_lines > 1):
      options_dict["header"] = False
    self.logger.debug(f"[ReaderService][_get_csv_reader_options] csv reader optiones: {options_dict}")
    
    return options_dict
    
  def _spark_csv_reader(self, filename, entity : EntityModel):
    options = self._get_csv_reader_options(entity)
    self.logger.debug(f"[ReaderService][_spark_csv_reader] Read csv file {filename}, entity: {entity}")
    
    fileDF = self.spark.read.format(entity.reader_properties.file_format).options(**options).load(filename)
    
    # If there are more than one header row, we have to convert the dataframe to pandas, drop the rows and then recreate the spark dataframe
    if (entity.reader_properties.header_lines is not None and entity.reader_properties.header_lines > 1 and "header" in entity.reader_properties.reader_options and entity.reader_properties.reader_options["header"] is True):
      pandasDF = fileDF.toPandas()
      fileDF = self.spark.createDataFrame(pandasDF.iloc[entity.reader_properties.header_lines:])
      pandasDF = None
      del pandasDF
    return fileDF
     
  # TODO: Try to use the storage file directly without mounting in databricks file system
  # Available options: https://spark.apache.org/docs/latest/sql-data-sources-csv.html / https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_excel.html
  def _pandas_excel_reader(self, sourcePath, entity : EntityModel):
    self.logger.debug(f"[ReaderService][_pandas_excel_reader] Reading pandas excel sourcePath {sourcePath}, entity: {entity}")
    sourcePathList = sourcePath.split("@")
    container = sourcePathList[0].replace("wasbs://", "")
    filePath = sourcePathList[1].split("/")
    folderPath = "/".join(filePath[1:-1])
    fileName = filePath[-1]
      
    sourceFolder = sourcePath.replace("/" + fileName, "")
    mntFolder = "/mnt/" + container + "/" + folderPath
    fulldbfsPath = "/dbfs" + mntFolder + "/" + fileName
    
    scopeVar = "resources"
    keyNameVar = "additional_storage_account_name"
    keyVar = "additional_storage_account_key"
    storageName = self.dbutils.secrets.get(scope = scopeVar, key = keyNameVar)
    config = "fs.azure.account.key." + storageName + ".blob.core.windows.net"
    secret = self.dbutils.secrets.get(scope = scopeVar, key = keyVar)
    options = entity.reader_properties.reader_options
    fileDF = None
       
    try:   
      self.dbutils.fs.mount(
        source = sourceFolder,
        mount_point = mntFolder,
        extra_configs = { config: secret})
    except Exception as e:
      self.logger.exception(f"[ReaderService][_pandas_excel_reader] Exception reading excel pandas {e}")
      pass
    sourceDF = pd.read_excel(io=fulldbfsPath, **options)
    self.dbutils.fs.unmount(mntFolder)
    stringDF = sourceDF.astype(str)
    fileDF = self.spark.createDataFrame(stringDF) 
       
    return fileDF
