from pyspark.sql.functions import col, lit, when
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
import SidraCoreApiPythonClient
from SidraCoreApiPythonClient.rest import ApiException
from sidraconnector.sdk.utils import Utils
from sidraconnector.sdk.databricks.utils import Utils as DatabricksUtils
from sidraconnector.sdk.api.sidra.core.utils import Utils as CoreApiUtils
from sidraconnector.sdk.metadata.assetservice import AssetService
from sidraconnector.sdk.metadata.entityservice import EntityService
from sidraconnector.sdk.metadata.providerservice import ProviderService
from sidraconnector.sdk.constants import *
from sidraconnector.sdk.databricks.dsuingestion.models.fielddefinition import FieldDefinition
from sidraconnector.sdk.storage.utils import Utils as StorageUtils
from sidraconnector.sdk.storage.storageservice import StorageService


class TabularIngestionService():
  def __init__(self, spark, logger, asset_uri, asset_id, asset_is_full_extract):
    self.spark = spark
    self.databricks_utils = DatabricksUtils(spark)
    self.storage_service = StorageService(spark)
    self.storage_utils = StorageUtils(spark)       
    self.dbutils = self.databricks_utils.get_db_utils()
    self.logger = logger  
    self.identifier_temp_table = Utils.get_guid()
    self.asset_uri = asset_uri
    self.asset_id = asset_id
    self.asset_date = None
    self.asset_is_full_extract = asset_is_full_extract
    self.asset_is_registered = asset_id is not None
    sidra_core_api_client = CoreApiUtils(spark).get_SidraCoreApiClient()
    self.ingestion_api_instance = SidraCoreApiPythonClient.IngestionIngestionApi(sidra_core_api_client) 
    self.asset_service = AssetService(spark)
    self.entity_service = EntityService(spark)
    self.provider_service = ProviderService(spark)
    self.provider = None
    self.entity = None
  
  # --------------------
  # Query Optimizationsinsert_into_validation_errors_table
  # --------------------
  
  def configure_query_optimization(self):
    #if (self.entity.reader_properties.row_delimiter is not None or self.entity.reader_properties.row_delimiter != ''):
    #  delimiter_query = f'SET textinputformat.record.delimiter={self.entity.reader_properties.row_delimiter}'
    #  spark.sql(delimiter_query)
    self.spark.sql('SET hive.exec.dynamic.partition = true')
    self.spark.sql('SET hive.exec.dynamic.partition.mode = nonstrict')
    self.spark.sql('SET hive.optimize.sort.dynamic.partition = false')
    
  # -----------------------------------
  # Get Metadata Information
  # -----------------------------------
  
  def set_metadata_information(self):
    if self.asset_id is not None:
      try:
        asset = self.asset_service.get_asset(self.asset_id)
        self.asset_date = asset.asset_date
        self.logger.debug(f'Getting entity with id {asset.id_entity}')
        self.entity = self.entity_service.get_entity_model_with_attribute_and_attribute_format(asset.id_entity)
        self.provider = self.provider_service.get_provider_model(self.entity.id_provider)
      except ApiException as e:
        self.logger.exception(f"[Tabular Ingestion][set_metadata_information] Exception when calling API to get associated metadata for asset id {self.asset_id}: {e}")
        raise e        
      except Exception as e:
        self.logger.exception(f"[Tabular Ingestion][set_metadata_information] Exception when get the associated metadata for asset id {self.asset_id}: {e}")
        raise e
    else:
      message = "[Tabular Ingestion][set_metadata_information] Unable to retrieve the metadata for the asset because there is not asset id defined"
      self.logger.error(message)
      raise Exception(message)
 
  def get_entity(self):
    return self.entity
  
  def get_asset_id(self):
    return self.asset_id
  
  def get_consolidation_mode(self):
    if self.entity is not None:
      self.logger.debug(f"[Tabular Ingestion][get_consolidation_mode] The consolidation mode is: {self.entity.load_properties.consolidation_mode}")
      return self.entity.load_properties.consolidation_mode
    else:
      message = "[Tabular Ingestion][get_consolidation_mode] Unable to retrieve the consolidation mode because the entity is not defined"
      self.logger.error(message)
      raise Exception(message)
      
  def has_to_generate_change_data_feed(self):
    if self.entity is not None:
      return self.entity.load_properties.generate_delta_table
    else:
      message = "[Tabular Ingestion][has_to_generate_change_data_feed] Unable to retrieve if it has to generate Change Data Feed because the entity is not defined"
      self.logger.error(message)
      raise Exception(message)
      
  def has_to_generate_data_catalog(self):
    if self.entity is not None:
      return self.entity.load_properties.data_preview
    else:
      message = "[Tabular Ingestion][has_to_generate_data_catalog] Unable to retrieve if it has to generate Data Catalog because the entity is not defined"
      self.logger.error(message)
      raise Exception(message)      
      
  # -----------------------------------
  # Database, Table and Columns Naming
  # -----------------------------------
  def get_provider_database(self):
    return f'{self.provider.database_name}'
    
  # TODO: REVIEW: Apply same logic than _get_staging_table_name ?
  def _get_full_table_name(self, suffix = ''):
    return f'`{self.provider.database_name}`.`{self.entity.table_name}{suffix}`'
  
  #def _get_staging_table_name(self, _get_insert_merge_data_into_final_tablesuffix_tableName = ''): Review why this was like this
  def _get_staging_table_name(self, suffix_tableName = ''):
    suffix_tableName = '' if suffix_tableName is None else suffix_tableName
    tableName = f"{self.entity.table_name}{self.identifier_temp_table}{suffix_tableName}";
    tableNameChecker = f"{self.entity.table_name}{suffix_tableName}";
    if (len(tableNameChecker) + GUID_LEN_WITHOUT_HYPHENS > TABLE_NAME_MAX_LEN):
      max = TABLE_NAME_MAX_LEN - (GUID_LEN_WITHOUT_HYPHENS + len(suffix_tableName))
      entityTableName = self.entity.table_name[0:max]
      tableName = f"{entityTableName}{self.identifier_temp_table}{suffix_tableName}";
    return tableName;
    
  def get_non_calculated_field_names(self):
    column_names = [attribute.name for attribute in filter(lambda x: not x.is_calculated, self.entity.attributes)]
    column_names.append(ATTRIBUTE_NAME_IS_DELETED)
    return column_names
    
  def _get_processed_field_name(self, attribute):
    return f"`{attribute.name}`" if attribute.is_calculated or attribute.is_partition_column else f"`{attribute.name}{ATTRIBUTE_PROCESSED_SUFFIX}`"
      
  def _get_raw_field_name(self, attribute):
    return f"`{attribute.name}{ATTRIBUTE_RAW_SUFFIX}`"
  
  # ---------------------
  # Create Staging Table
  # ---------------------
  
  def add_is_deleted_column(self, fileDF):
      # Change Tracking column
      if ('SYS_CHANGE_OPERATION' in fileDF.columns):
          df = fileDF.withColumn(ATTRIBUTE_NAME_IS_DELETED, when(col('SYS_CHANGE_OPERATION') == 'D', True).otherwise(False)).drop('SYS_CHANGE_OPERATION')
      else:
          df = fileDF.withColumn(ATTRIBUTE_NAME_IS_DELETED, lit(False))
      return df
  
  def create_staging_table(self, fileDF):
    table_filename = self._get_staging_table_name()
    self.logger.debug(f"[Tabular Ingestion][create_staging_table] Create or replace stagin table {table_filename}")
    fileDF.createOrReplaceTempView(table_filename)
    return table_filename
      
  def _get_processed_field_for_select_statement(self, attribute, expression):  
    field_name = self._get_processed_field_name(attribute)
    field_type = None
    field_expression = None
    # TODO: Remove this expression? Is is a legacy option
    #if expression == 'BLOCK__OFFSET__INSIDE__FILE': field_expression = '0':
    if expression == ATTRIBUTE_NAME_ASSET_ID: 
      field_expression = f"{self.asset_id}"
    elif expression == ATTRIBUTE_NAME_FILE_DATE:
      field_expression = f"'{self.asset_date}'"
    else:
      field_expression = f"{expression}"
      field_type = attribute.databricks_type
    
    return FieldDefinition(field_name, field_expression, field_type)
  
  def _get_raw_field_for_select_statement(self, attribute):
    # TODO: Pending to generate lookup result
    #if (isLookupResult)
    # return (_lookupAttributeService.GetLookupSelectField(col));
    if not attribute.is_calculated:
      field_name = self._get_raw_field_name(attribute)
      # is the replace needed? _nameService.GetRawColumnName(col).Replace("`","")
      return FieldDefinition(field_name, f"s.`{attribute.name}`", None)
  
  def _get_field_expression(self, attribute):
    alias = 's' # TODO: REVIEW: isLookupResult ? _lookupAttributeService.GetTableReference(col)  
    field_text = f"{alias}.`{attribute.name}`"
    # attribute.remove_quotes is not used as databricks removes the quotes when reading the file
    if attribute.load_properties.need_trim is True:
      field_text = f"TRIM({field_text})"
    if attribute.load_properties.replaced_text is not None:
      field_text = f"REGEXP_REPLACE({field_text},'{attribute.load_properties.replaced_text}','{attribute.load_properties.replacement_text}')"
    if (attribute.databricks_type == 'INT'):
      field_text = f"CASE WHEN CAST({field_text} AS INT) <=> CAST({field_text} AS DECIMAL(38,18)) THEN {field_text} ELSE 'NaN' END"
    return field_text
  
  def _get_statements_for_null_verifications(self, field_text, null_text, treat_empty_as_null):
    statements = [] # TODO: Is it possible return more than one? I guess not
    if null_text is not None and treat_empty_as_null is True:
      statements.append(f"WHEN {field_text} = '{null_text}' OR {field_text} == '' THEN NULL")
    else:
      if null_text is not None:
        statements.append(f"WHEN {field_text} = '{null_text}' THEN NULL")
      if treat_empty_as_null is True:
        statements.append(f"WHEN {field_text} = '' THEN NULL")
    return statements;
  
  # TODO: Tests
  def _get_statements_for_formatted_field(self, field_text, attribute):
    # Nullable booleans need to be treated as strings
    treat_as_string = attribute.load_properties.is_nullable is True and attribute.databricks_type == 'BOOLEAN'
    quote_char = "'" if treat_as_string is True else ""
    statements = []
    if attribute.attribute_formats is not None:
      for attr_format in attribute.attribute_formats:
        if attr_format.source_value is not None:
          statements.append(f"WHEN {field_text} = '{attr_format.source_value}' THEN {quote_char}{attr_format.databricks_expression}{quote_char}")
        elif attr_format.reg_exp is not None:
          statements.append(f"WHEN REGEXP_REPLACE({field_text},{attr_format.reg_exp},0) IS NOT NULL THEN {quote_char}{attr_format.databricks_expression}{quote_char}")  
      return statements
  
  def _get_fields_for_staging_table(self):
    fields = []     
    # SidraPassedValidation column are excluded because are autogenerated on the query.
    attributes = [attribute for attribute in self.entity.attributes if attribute.name != ATTRIBUTE_NAME_PASSED_VALIDATION]
        
    for attribute in attributes:
      if attribute.is_calculated is True and attribute.is_metadata is not True and attribute.load_properties.special_format is None:
        message = f"[Tabular Ingestion] The attribute '{attribute.name}' is not a metadata attribute and it is defined as calculated without a definition of how it is calculated."
        self.logger.exception(message)
        raise Exception(message)
      
      if attribute.load_properties.special_format is not None:
        field_expression = attribute.load_properties.special_format
      else:
        statements = []
        field_text = self._get_field_expression(attribute)
        null_verifications = self._get_statements_for_null_verifications(field_text, self.entity.load_properties.null_text, attribute.load_properties.treat_empty_as_null)
        formatted_statements = self._get_statements_for_formatted_field(field_text, attribute)
        has_only_null_verifications = True if null_verifications and not formatted_statements else False
        if null_verifications:
          statements.extend(null_verifications)
        if formatted_statements:
          statements.extend(formatted_statements)
        if statements:
          if has_only_null_verifications or attribute.is_nullable:
            statements.append(f" ELSE {field_text}")
          else:
            statements.append(" ELSE NULL")
          join_statements = " ".join(statements)
          field_expression = f"CASE {join_statements} END"
        else:
          field_expression = field_text
      processed_field = self._get_processed_field_for_select_statement(attribute, field_expression)
      raw_field = self._get_raw_field_for_select_statement(attribute)
      fields.append(processed_field)
      self.logger.debug(f"[Tabular Ingestion] Create processed field: Name: {processed_field.name} Type: {processed_field.type} Expression: {processed_field.expression}")
      if raw_field is not None:
        fields.append(raw_field) 
        self.logger.debug(f"[Tabular Ingestion] Create raw field: Name: {raw_field.name} Type: {raw_field.type} Expression: {raw_field.expression}")
    return fields
      
  # create_staging_table_insert
  def _get_table_staging_query(self):
    fields = self._get_fields_for_staging_table()
    select_fields = [f"CAST ({field.name} AS {field.type}) AS {field.name}" if ATTRIBUTE_PROCESSED_SUFFIX in field.name else f"{field.name}" for field in fields]
    select_fields_statement = f", ".join(select_fields)
    source_fields = [f"{field.expression} AS {field.name}" for field in fields]
    source_fields_statement = f", ".join(source_fields)

    # TODO: Pending to implement AttributeFormats
    join_statements = ''

    query = f"""SELECT 
    {select_fields_statement}
    , NULL AS {ATTRIBUTE_NAME_PASSED_VALIDATION} 
    FROM (
      SELECT {source_fields_statement}
      FROM {self._get_staging_table_name()} s
      {join_statements}
    )""" 
    
    self.logger.debug(f"[Tabular Ingestion] Staging table for entity {self.entity.id}: {query}")    
    
    # TODO: Pending to add: var joinStatements = _lookupAttributeService.GetJoinStatements(); if (!string.IsNullOrWhiteSpace(joinStatements)) {sb.Append(joinStatements);}  
    return query
  
  def create_table_staging_query(self):
    query = self._get_table_staging_query()
    resultDF = self.spark.sql(query)
    tmp_table_name = self._get_staging_table_name(TABLE_TEMP_JOIN_SUFFIX)
    resultDF.createOrReplaceTempView(tmp_table_name)
    
  # -------------------
  # Drop Staging Table
  # -------------------
  
  def drop_staging_tables(self):
    queries = self._get_queries_to_drop_staging_tables()
    self.logger.debug(f"[Tabular Ingestion][drop_staging_tables] Dropping staging tables {queries}")    
    self.databricks_utils.execute_sql_queries(queries)
    
  def _get_queries_to_drop_staging_tables(self):
    sql_queries = []
    sql_queries.append(f'DROP TABLE IF EXISTS {self._get_staging_table_name(TABLE_TEMP_JOIN_SUFFIX)}')
    sql_queries.append(f'DROP TABLE IF EXISTS {self._get_staging_table_name()}')    
    return sql_queries
      
  # -----------------------------------
  # Snapshot Mode - Create Final Table 
  # -----------------------------------
  
  def _get_insert_snapshot_data_into_final_table_statement(self):
    table_name = self._get_full_table_name()
    staging_table_name = self._get_staging_table_name(TABLE_TEMP_JOIN_SUFFIX)
    partition_fields = [f'`{attribute.name}`' for attribute in self.entity.attributes if attribute.is_partition_column is True] 
    non_partition_fields = [attribute for attribute in self.entity.attributes if attribute.is_partition_column is False]
    fields_to_insert = []
    column_names = []
    
    for column in non_partition_fields:
      column_names.append(f"`{column.name}`")
      column_name = self._get_processed_field_name(column)
      # Nullable custom format booleans get values from the validated string here
      # Replicated how the original generated transfer query implements this but:
      # TODO: Why this is been done here? The format should be applied in the staging side, not here
      # TODO: Why are we checking for format but not using it?
      if column.load_properties.is_nullable and column.databricks_type == 'BOOLEAN' and column.attribute_formats is not None and len(column.attribute_formats) > 0:
        fields_to_insert.append(f"CASE WHEN {column_name} = 'FALSE' THEN FALSE WHEN {column_name} = 'TRUE' THEN TRUE ELSE NULL END AS {column_name}")
      else:
        if column.is_encrypted:
          fields_to_insert.append(f"encrypt({column_name}) as {column_name}")
        else:
          fields_to_insert.append(f"{column_name}")
    
    if self.entity.load_properties.id_table_format == ID_DELTA_TABLE_FORMAT:
      partition = '' if partition_fields is None or len(partition_fields) == 0 else f"PARTITION ({(','.join(partition_fields))})"
      column_names.extend(partition_fields)
      insert_statement = f"INSERT INTO TABLE {table_name} {partition} ({(','.join(column_names))}) "
      fields_to_insert.extend(partition_fields)
    else:
      # important: we will only set values for File date and Idsource items but we will add all files to the partition block (e.g: (SidraFileDate='2020-05-15', SidraIdAsset=11111, otherPartitionField)).
      # Don't forget to add the non mapped partition fields in the select
      standard_partition_fields = [f"`{ATTRIBUTE_NAME_FILE_DATE}`", f"`{ATTRIBUTE_NAME_ASSET_ID}`"]
      non_standard_partition_fields = [attribute for attribute in partition_fields if attribute not in standard_partition_fields]
      non_standard_partition_fields_statement = ",".join(non_standard_partition_fields)
      base_partition_block = f"`{ATTRIBUTE_NAME_FILE_DATE}`='{self.asset_date}',`{ATTRIBUTE_NAME_ASSET_ID}`='{self.asset_id}'"
      partition_block = f"{base_partition_block}" if non_standard_partition_fields_statement == '' else f"{base_partition_block},{non_standard_partition_fields_statement}"
      column_names.extend(non_standard_partition_fields)
      insert_statement = f"INSERT OVERWRITE TABLE {table_name} PARTITION ({partition_block}) ({(','.join(column_names))}) "
      fields_to_insert.extend(non_standard_partition_fields) 
    
    query = f"""{insert_statement}
SELECT {(",".join(fields_to_insert))}
FROM {staging_table_name}"""

    self.logger.debug(f"[Tabular Ingestion][_get_insert_snapshot_data_into_final_table_statement] Query to insert data into {table_name}: {query}")
    return query
    
  def insert_snapshot_data_into_final_table(self):
    query = self._get_insert_snapshot_data_into_final_table_statement()
    self.spark.sql(query)
  
  # ------------------------------------
  # Snapshot Mode - Truncate Partitions
  # ------------------------------------
  
  def _get_truncate_old_partition_from_same_file_statements(self):
    statements = []
    table_name = self._get_full_table_name()
    asset_id_field = next((attribute for attribute in self.entity.attributes if attribute.is_partition_column is True and attribute.name == ATTRIBUTE_NAME_ASSET_ID), None)
    # Only reason to not partition the table by SidraAssetId is that table is overwriten always, in that case, we can simply truncate 
    if (asset_id_field is None):
      self.logger.debug(f"[Tabular Ingestion] The table is not partitioned by AssetId. The table {table_name} will be truncated because they are overwritten in each load")
      statements.append(f"TRUNCATE TABLE {table_name}")
    else:
      if (self.entity.load_properties.id_table_format == ID_DELTA_TABLE_FORMAT):
        self.logger.debug(f"[Tabular Ingestion] Delete if exist partitions asset id: {self.asset_id} for table {table_name}")
        # Cannot alter/drop Delta tables' partitions once created.
        # But a DELETE FROM can be executed, filtering by a partition column, which is fast. https://docs.databricks.com/delta/delta-update.html#delete-from
        statements.append(f"DELETE FROM {table_name} WHERE `{ATTRIBUTE_NAME_ASSET_ID}`={self.asset_id}")
      else:
        self.logger.warning(f"[Tabular Ingestion][_get_truncate_old_partition_from_same_file_statements] Partition delete is not needed for table {table_name} because the INSERT will overwrite the existing partition")
    return statements
    
  def truncate_old_partition_from_same_file(self):
    queries = self._get_truncate_old_partition_from_same_file_statements()
    self.databricks_utils.execute_sql_queries(queries)

  # -----------------------------------
  # Merge Mode - Create Final Table
  # -----------------------------------
  def _get_insert_merge_data_into_final_table(self):
    table_name = self._get_full_table_name()
    staging_table_name = self._get_staging_table_name(TABLE_TEMP_JOIN_SUFFIX)
    entity_attributes = [attribute for attribute in self.entity.attributes]
    entity_attributes_names = [attribute.name for attribute in self.entity.attributes]
    primary_key_attributes = [attribute for attribute in self.entity.attributes if attribute.is_primary_key is True]
    attributes_to_update = [attribute for attribute in self.entity.attributes if attribute.is_primary_key is False]
    
    if not primary_key_attributes:
      errorMessage = "There is no primary key defined. It is necessary to set some attributes as primary key to create a Merge transfer query."
      self.logger.error(errorMessage)
      raise Exception(errorMessage)
    
    #SELECT section ---
      # TODO - Pending to implement _cryptographyService.EncryptColumn(i)
    entity_attributes_processed = []
    for entity_attribute in entity_attributes:
      entity_attribute_processed = self._get_processed_field_name(entity_attribute)
      entity_attributes_processed.append(entity_attribute_processed)
    
    select_statement = ", ".join(entity_attributes_processed)
    
    #ON section -----
    primary_key_fields = []
    for primary_key_field in primary_key_attributes:
      processed_pk_field_name = self._get_processed_field_name(primary_key_field)
      primary_key_fields.append(f"s.{processed_pk_field_name} = t.{primary_key_field.name}")
      
    #WHEN MATCHED THEN UPDATE SET section ---
    attributes_to_update_filtered = [attribute for attribute in attributes_to_update if attribute.name != ATTRIBUTE_NAME_IS_DELETED and attribute.name != ATTRIBUTE_NAME_ASSET_ID]
    
    columns_update_is_deleted = []
    for column in attributes_to_update_filtered:
      columns_update_is_deleted.append(f"t.`{column.name}` = CASE s.{ATTRIBUTE_NAME_IS_DELETED} WHEN True THEN t.`{column.name}` else s.{self._get_processed_field_name(column)} END")
      
    attributes_update_is_deleted_splited = ", ".join(columns_update_is_deleted)
    when_matched_then_update_is_deleted = f"""  
WHEN MATCHED THEN UPDATE SET
  {attributes_update_is_deleted_splited}, t.`{ATTRIBUTE_NAME_IS_DELETED}` = s.`{ATTRIBUTE_NAME_IS_DELETED}`,t.`{ATTRIBUTE_NAME_ASSET_ID}` = s.`{ATTRIBUTE_NAME_ASSET_ID}`"""
    
    columns_update_is_not_deleted = []
    for column in attributes_to_update_filtered:
      columns_update_is_not_deleted.append(f"\n t.`{column.name}` = s.{self._get_processed_field_name(column)} ")
    
    when_matched_then_update_is_not_deleted = f"""WHEN MATCHED THEN UPDATE SET
  {columns_update_is_not_deleted}"""
    
    is_deleted = any(at for at in entity_attributes if at.name == ATTRIBUTE_NAME_IS_DELETED)
    
    if(is_deleted):
      when_match_then_update_statement = when_matched_then_update_is_deleted
    else:
      when_match_then_update_statement = when_matched_then_update_is_not_deleted
    
    #WHEN NOT MATCHED section ---   
    when_not_matched_entity_attributes_processed = []
    for attribute in entity_attributes_processed:
      when_not_matched_entity_attributes_processed.append(f"s.{attribute}")
    
    when_not_matched_entity_attributes = ", ".join(entity_attributes_names)
    when_not_matched_entity_attributes_values = ", ".join(when_not_matched_entity_attributes_processed)
    when_not_matched_statement = f"""WHEN NOT MATCHED THEN INSERT
  ({when_not_matched_entity_attributes})
VALUES
  ({when_not_matched_entity_attributes_values})"""
    
    query = f"""
MERGE INTO {table_name} AS t
USING (
  SELECT {select_statement}
  FROM {staging_table_name}
  ) s ON {"AND ".join(primary_key_fields)}
{when_match_then_update_statement}
{when_not_matched_statement}"""

    
    self.logger.debug(f"[Tabular Ingestion][_get_insert_merge_data_into_final_table] - [Merge Mode] Query to insert data into {table_name}: {query}")
    return query
      
  def insert_merge_data_into_final_table(self):
    query = self._get_insert_merge_data_into_final_table()
    self.spark.sql(query)

  # -------
  # DELETE 
  # -------
  
  def delete_from_table(self):
    table_name = self._get_full_table_name()
    if (self.entity.load_properties.id_table_format == ID_DELTA_TABLE_FORMAT):    
      if (self.asset_is_full_extract is True):
        self.logger.debug(f"[Tabular Ingestion][delete_from_table] Truncate table {table_name}")
        self.spark.sql(f'TRUNCATE TABLE {table_name}')
      else:
        self.logger.debug(f"[Tabular Ingestion][delete_from_table] Remove partition asset id {self.asset_id} for table {table_name}")
        self.spark.sql(f'DELETE FROM {table_name} WHERE `{ATTRIBUTE_NAME_ASSET_ID}`={self.asset_id}')
    else:
      # Delete all tables files if needed
      if (self.asset_is_full_extract is True):
        self.delete_table_folder(table_name)
  
  def delete_table_folder(self, tableName):
      table_location = (self.spark.sql("desc formatted " + tableName).filter("col_name=='Location'").collect()[0].data_type)
      self.logger.debug(f"[Tabular Ingestion][delete_table_folder] Delete table folder located in {table_location}")
      self.dbutils.fs.rm(table_location, True)
      
  # ---------------
  # Register Asset
  # ---------------
  
  def register_asset(self):
    # Registers an asset from a Landing Zone. Returns: APIDataIngestionModelAssetFromLanding
    try:
      registered_asset = self.asset_service.register_asset(self.asset_uri)
      self.asset_id = registered_asset.asset_id
      self.asset_date = registered_asset.asset_date     
    except ApiException as e:
      self.logger.exception(f"[Tabular Ingestion][register_asset] Exception when Register Asset {self.asset_uri}: %s\n" % e)
      raise e
    return registered_asset
  
  def register_info(self, registered_asset): 
    # registered_asset is the result of register_asset() function and it is an APIDataIngestionModelAssetFromLanding
    # Returns APICommonCorePipelineParameter
    try:
      result = self.asset_service.register_info(registered_asset)
    except ApiException as e:
      self.logger.exception(f"[Tabular Ingestion][register_asset] Exception when register information for the asset {registered_asset.asset_id}: %s\n" % e) 
      raise e
    return result
  
  # -------------------------
  # Update Asset Information 
  # -------------------------
  
  def finish_loading(self, entities_count):  
    try:
      self.asset_service.update_asset_loaded(self.asset_id, entities_count)
    except ApiException as e:
      self.logger.exception(f"[Tabular Ingestion][finish_loading] Exception when updating the asset {self.asset_id} with the number of entities loaded and the number of errors %s\n" % e)
      raise e
      
  # --------------
  # Manage blobs.
  # --------------
  def copy_raw_file(self, source_uri, destination_wasb):
    destination_container = destination_wasb.split('@')[0].replace('wasbs://', '')
    destination_path = destination_wasb.split('/', 3)[3]    
    try:
      self.storage_service.copy_file(source_uri, destination_container, destination_path)
    except ResourceExistsError as e:
      self.logger.exception(f"[Tabular Ingestion][copy_raw_file] Error copying from blob {source_uri} to {destination_container}/{destination_path}: {e.reason}")
      raise e  
    except ResourceNotFoundError as e:
      self.logger.exception(f"[Tabular Ingestion][copy_raw_file] Error copying from blob {source_uri} to {destination_container}/{destination_path}: {e.reason}")
      raise e     
      
  def get_wasbs_file(self, file_uri):
    return self.storage_utils.https_to_wasbs(file_uri)
      
  def delete_source_file(self, source_uri):
    try:
      self.storage_service.delete_file(source_uri)
    except Exception as e:
      self.logger.exception(f"[Tabular Ingestion][delete_source_file] There was an error deleting the file {source_uri}: {e.reason}")
      raise e        
      
