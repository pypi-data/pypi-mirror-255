from collections import namedtuple
from sidraconnector.sdk.api.sidra.core.utils import Utils as SidraAPIUtils
from sidraconnector.sdk.databricks.utils import Utils as DatabricksUtils
from sidraconnector.sdk.log.logging import Logger
from SidraCoreApiPythonClient.api.metadata_entities_entity_api import MetadataEntitiesEntityApi
from SidraCoreApiPythonClient.api.metadata_providers_provider_api import MetadataProvidersProviderApi
from SidraCoreApiPythonClient.api.metadata_data_intake_processes_data_intake_process_api import MetadataDataIntakeProcessesDataIntakeProcessApi
from SidraCoreApiPythonClient.models.data_ingestion_entity_type_enum import DataIngestionEntityTypeEnum
from SidraCoreApiPythonClient.models.persistence_common_entities_data_ingestion_table_format_enum import PersistenceCommonEntitiesDataIngestionTableFormatEnum
from sidraconnector.sdk.metadata.entityservice import EntityService

class UpdateTables:
  def __init__(self, spark):
      self.spark = spark
      self.sidra_api_utils =  SidraAPIUtils(spark)
      self.databricks_utils = DatabricksUtils(spark)
      self.entity_service = EntityService(spark)
      self.logger =  self.logger = Logger(spark, self.__class__.__name__)

  def _get_table_format(self, table_format_id):
    DEFAULT_VALUE = PersistenceCommonEntitiesDataIngestionTableFormatEnum.DELTA
    if table_format_id is None:
        return DEFAULT_VALUE
    elif table_format_id == 1:
        return PersistenceCommonEntitiesDataIngestionTableFormatEnum.ORC
    elif table_format_id == 2:
        return PersistenceCommonEntitiesDataIngestionTableFormatEnum.PARQUET
    elif table_format_id == 3:
        return PersistenceCommonEntitiesDataIngestionTableFormatEnum.DELTA
    raise AttributeError(f"table format {table_format_id} is not supported")  


  def _get_entity_type(self, entity_type_id):
      if entity_type_id == 0:
        return DataIngestionEntityTypeEnum.OTHER
      elif entity_type_id == 1:
        return DataIngestionEntityTypeEnum.TABLE
      elif entity_type_id == 2:
        return DataIngestionEntityTypeEnum.VIEW


  def _validate_model(self, model, *keys):
      errors = [f"Missing key: {key}" for key in filter(lambda x: x not in model, keys)]
      if errors:
          raise ValueError(f"Model is invalid. Errors: {', '.join(errors)}")

  def _get_entities_to_update(self, id_DIP, client) -> list:
     dip_api = MetadataDataIntakeProcessesDataIntakeProcessApi(client)
     dip = dip_api.api_metadata_data_intake_processes_id_get(id_DIP)
     dip._id_provider
     entities = self.entity_service.get_all()
     entities_ids = []

     entities_to_update = filter(lambda entity: entity._last_deployed is not None and entity._last_updated > entity._last_deployed and entity._id_provider == dip._id_provider, entities)
     if entities_to_update:
        entities_ids = [e._id for e in entities_to_update]
     
     return entities_ids
           
  def _get_entities(self, id_entities, client):
      metadata_entity_api = MetadataEntitiesEntityApi(client)
      KEY_ID_ENTITY = 'id'
      KEY_ID_PROVIDER = 'id_provider'
      KEY_TABLE_NAME = 'table_name'
      KEY_ID_TABLE_FORMAT = 'id_table_format'
      KEY_RECREATE_TABLE_ON_DEPLOYMENT = 're_create_table_on_deployment'
      KEY_GENERATE_DELTA_TABLE = 'generate_delta_table'
      KEY_ATTRIBUTES = 'attributes'
      KEY_ENTITY_TYPE = 'entity_type'
      KEY_VIEW_DEFINITION = 'view_definition'
      entities=metadata_entity_api.api_metadata_entities_withattributes_get(body=id_entities)   
      EntityModel = namedtuple('EntityModel', 'id_entity id_provider table_name table_format recreate_table generate_delta_table attributes entity_type view_definition')
      entities_model = []
      for entity in entities:
          self._validate_model(entity.to_dict(), KEY_ID_ENTITY, KEY_ID_PROVIDER, KEY_TABLE_NAME, KEY_ID_TABLE_FORMAT, KEY_RECREATE_TABLE_ON_DEPLOYMENT, KEY_GENERATE_DELTA_TABLE, KEY_ATTRIBUTES)
          id_entity = entity.id
          id_provider = entity.id_provider
          table_name = entity.table_name
          table_format = self._get_table_format(entity.id_table_format)
          recreate_table = entity.re_create_table_on_deployment
          generate_delta_table = entity.generate_delta_table
          entity_type = self._get_entity_type(entity.entity_type)
          view_definition = entity.view_definition
          attributes = self._parse_attributes(entity.attributes)
          entities_model.append(EntityModel(id_entity = id_entity, id_provider = id_provider, table_name = table_name, table_format =table_format, recreate_table = recreate_table, generate_delta_table = generate_delta_table, attributes =attributes, entity_type = entity_type, view_definition = view_definition))
      return entities_model

  def _get_provider(self, id_provider, client):
      providers_cache = dict()
      metadata_provider_api = MetadataProvidersProviderApi(client)
      KEY_DATABASE_NAME = 'database_name'
      if id_provider not in providers_cache:
        providers_cache[id_provider] = metadata_provider_api.api_metadata_providers_id_get(id_provider)
        
      provider=providers_cache[id_provider]
      
      self._validate_model(provider.to_dict(), KEY_DATABASE_NAME)
      ProviderModel = namedtuple('ProviderModel', 'id_provider database_name')
      database_name = provider.database_name
      return ProviderModel(id_provider = id_provider, database_name = database_name)

  def _parse_attributes(self, attributes_from_api):
    attribute_tuples = []
    AttributeModel = namedtuple('AttributeModel', 'name hive_type is_partition is_calculated order')
    for attribute in attributes_from_api:
      name = attribute.name
      hive_type = 'STRING' if attribute.is_encrypted else attribute.hive_type
      is_partition = attribute.is_partition_column
      is_calculated = attribute.is_calculated
      order = attribute.order
      attribute_tuples.append(AttributeModel(name = name, hive_type = hive_type, is_partition = is_partition, is_calculated = is_calculated, order = order))
    return sorted(attribute_tuples, key = lambda x: x.order)

  def execute(self, id_DIP):
    self.spark.conf.set("fs.azure.createRemoteFileSystemDuringInitialization", "true")
    try:
        client = self.sidra_api_utils.get_SidraCoreApiClient()

        principal_storage_name = self.databricks_utils.get_databricks_secret(scope='resources', key='principal_storage_account_name')
        id_entities = self._get_entities_to_update(id_DIP, client)
        if not id_entities:
            self.logger.info("No entities found for schema evolution")
            return

        entities = self._get_entities(id_entities, client)
        
        provider_info = {}
        for entity in entities:
            if entity.id_provider in provider_info:
                provider = provider_info[provider.id_provider]
            else:
                provider = self._get_provider(entity.id_provider, client)
                provider_info[provider.id_provider] = provider
                
        # SchemaEvolution
        for entity in entities:
            self.spark.sql(f"ALTER TABLE {provider.database_name}.{entity.table_name} SET TBLPROPERTIES (delta.enableChangeDataFeed = {entity.generate_delta_table})")
            existing_attributes = self.spark.sql(f'SHOW COLUMNS from {provider.database_name}.{entity.table_name}')
            existing_attributes_list = existing_attributes.select("col_name").rdd.map(lambda r: r[0]).collect()
            newAttributes = list(map(lambda x: x,filter(lambda x: x.name not in existing_attributes_list, entity.attributes)))
            if newAttributes:
                for newAttribute in newAttributes:
                    previous_attribute = list(filter(lambda x: x.order == newAttribute.order-1, entity.attributes))
                    self.spark.sql(f"ALTER TABLE {provider.database_name}.{entity.table_name} ADD COLUMN {newAttribute.name} {newAttribute.hive_type} AFTER {previous_attribute[0].name}")
                    print(f"ADDED new column {newAttribute.name} to {provider.database_name}.{entity.table_name}")
                    self.logger.info(f"ADDED new column {newAttribute.name} to {provider.database_name}.{entity.table_name}")
                self.logger.event('Table schema updated', {'tableName' : f"{provider.database_name}.{entity.table_name}", 'newAttributes': newAttributes })        
    finally:
        self.logger.flush()
        self.spark.conf.set("fs.azure.createRemoteFileSystemDuringInitialization", "false")