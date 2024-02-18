import math
import pandas as pd
import urllib.parse
from sidraconnector.sdk.log.logging import Logger
from sidraconnector.sdk.databricks.utils import Utils
from sidraconnector.sdk.constants import *

class DataPreviewService():
  def __init__(self, spark, logger):
    self.databricks_utils = Utils(spark)
    self.spark = spark       
    self.dbutils = self.databricks_utils.get_db_utils()
    self.logger = logger        

  def write_df_into_databse(self, jdbc_url, df, table_name_with_schema, mode="overwrite"):
    df.write \
      .format("jdbc")\
      .mode(mode)\
      .option("url", jdbc_url)\
      .option("dbtable", table_name_with_schema)\
      .save()

  def execute_sp(self, jdbc_url, statement):
    driver_manager = self.spark._sc._gateway.jvm.java.sql.DriverManager
    con = driver_manager.getConnection(jdbc_url)
    exec_statement = con.prepareCall(statement)
    exec_statement.execute()
    exec_statement.close()
    con.close()

  def create_sqlserver_datapreview_table(self, asset_id, max_sample_records, provider_database, entity_table, entity_id):
   
    source_table = '{provider_database}.{entity_table}'.format(provider_database = provider_database, entity_table = entity_table)
    preview_table = '{provider_database}_{entity_table}'.format(provider_database = provider_database, entity_table = entity_table)
    
    self.logger.debug(f"""[DataPreviewService][create_sqlserver_datapreview_table] Creating data preview table: asset_id: {asset_id}, max_sample_records: {max_sample_records}, provider_database:{provider_database}, source_table: {source_table}, preview_table: {preview_table}""")
    
    jdbcUrl = self.dbutils.secrets.get(scope = "jdbc", key = "coreJdbcDbConnectionString").replace('yes', 'true')
    table_description = self.spark.sql('DESCRIBE {source_table}'.format(source_table=source_table))
    table_columns = self.spark.sql('SHOW COLUMNS IN {source_table}'.format(source_table=source_table)) 
    
    select_fields=list()
    for field in table_columns.rdd.collect():       
        column_description = table_description.filter(table_description.col_name==field.col_name).first()
        if column_description is None:
            self.logger.warning(f"""[DataPreviewService][create_sqlserver_datapreview_table] Mismatch in column information: {field.col_name}""")
            break;
        if column_description.data_type != 'binary':
            select_fields.append('CAST(' + field.col_name + ' AS STRING)')
            
    select_fields=pd.Series(select_fields).drop_duplicates().tolist()
    select_fields_str = ','.join(select_fields)
    chunk_size = math.floor(2100/len(select_fields)) # sql allows up to 2100 parameters in a query
    # Recreate table
    selectQuery='select {select_fields_str} from {source_table} limit 0'.format(select_fields_str=select_fields_str, source_table=source_table)
    df_table_empty = self.spark.sql(selectQuery)
    self.write_df_into_databse(jdbcUrl, df_table_empty, f"[DataPreview].[{preview_table}]")

    # Set dynamic data masking command
    statement = 'exec [DataPreview].[SetDynamicDataMasking] @IdEntity={entity_id}'.format(entity_id=entity_id)
    self.execute_sp(jdbcUrl, statement)
    
    # Add sample of records
    selectQuery='select {select_fields_str} from {source_table} where {ATTRIBUTE_NAME_ASSET_ID} = {asset_id} limit {max_sample_records}'.format(select_fields_str=select_fields_str, source_table=source_table, ATTRIBUTE_NAME_ASSET_ID = ATTRIBUTE_NAME_ASSET_ID, asset_id = asset_id, max_sample_records=max_sample_records)
    df_table_records = self.spark.sql(selectQuery)
    self.write_df_into_databse(jdbcUrl, df_table_records, f"[DataPreview].[{preview_table}]")
    
    # Insert in DataPreviewLoadHistory
    jsonResults = self.spark.sql(selectQuery).toPandas().to_json(orient='split').replace("\'","\\'")   
    selectQuery = 'select \'{entity_id}\' as IdEntity, \'{preview_table}\' as TableName, {ATTRIBUTE_NAME_LOAD_DATE} as LoadDate, \'{jsonResults}\' as LoadJson from {source_table} where {ATTRIBUTE_NAME_ASSET_ID} = {asset_id} limit 1'.format(jsonResults=jsonResults, ATTRIBUTE_NAME_LOAD_DATE = ATTRIBUTE_NAME_LOAD_DATE, ATTRIBUTE_NAME_ASSET_ID = ATTRIBUTE_NAME_ASSET_ID, asset_id=asset_id, entity_id=entity_id, source_table=source_table, preview_table=preview_table)
    df_datapreview_load_history = self.spark.sql(selectQuery)
    self.write_df_into_databse(jdbcUrl, df_datapreview_load_history, "[DataCatalog].[DataPreviewLoadHistory]", mode="append")
