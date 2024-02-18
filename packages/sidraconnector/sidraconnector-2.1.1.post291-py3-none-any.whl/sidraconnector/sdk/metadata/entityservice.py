from sidraconnector.sdk.metadata.models.builders import AttributeBuilder, AttributeLoadPropertiesBuilder, EntityBuilder
from sidraconnector.sdk.api.sidra.core.utils import Utils as CoreApiUtils
from sidraconnector.sdk.log.logging import Logger
from sidraconnector.sdk.metadata.models.entitymodel import EntityModel
from sidraconnector.sdk.metadata.models.entitymodel import EntityReaderPropertiesModel
from sidraconnector.sdk.metadata.models.entitymodel import EntityLoadPropertiesModel
from sidraconnector.sdk.metadata.models.attributemodel import AttributeModel
from sidraconnector.sdk.metadata.models.attributemodel import AttributeLoadPropertiesModel
from sidraconnector.sdk.metadata.models.attributemodel import AttributeFormatModel
from SidraCoreApiPythonClient.api.metadata_entities_delta_loads_entity_delta_load_api import MetadataEntitiesDeltaLoadsEntityDeltaLoadApi as EntityDeltaLoadApi
from SidraCoreApiPythonClient.api.metadata_attributes_attributes_api import MetadataAttributesAttributesApi as AttributesApi
from sidraconnector.sdk import constants
import SidraCoreApiPythonClient
import json
import uuid
from datetime import datetime, timedelta
from pyspark.sql.functions import *
from pyspark.sql.types import *

class EntityService():
  def __init__(self, spark):
    self.logger = Logger(spark, self.__class__.__name__)
    sidra_core_api_client = CoreApiUtils(spark).get_SidraCoreApiClient()
    self.metadata_entity_api_instance = SidraCoreApiPythonClient.MetadataEntitiesEntityApi(sidra_core_api_client)
    self.attributes_api = AttributesApi(sidra_core_api_client)
    self.entity_delta_load_api = EntityDeltaLoadApi(sidra_core_api_client)

  def get_all(self):
    self.logger.debug(f"[Entity Service][get_all] Retrieve all entities")
    return self.metadata_entity_api_instance.api_metadata_entities_all_get()    
 
  def get_entity(self, id_entity, include):
    self.logger.debug(f"[Entity Service][get_entity] Retrieve entity {id_entity} information")    
    return self.metadata_entity_api_instance.api_metadata_entities_id_get(id_entity, include=include, api_version=constants.API_VERSION)
    
  
  def _get_entity_by_name_and_provider(self, provider_id, entity_name):
    try:
      provider_entities = self.metadata_entity_api_instance.api_metadata_entities_get(field="Name",text=entity_name).items
      return next((e for e in provider_entities if e.name == entity_name and e.id_provider == provider_id), None)
    except:
      return None

  
  def get_entity_model_with_attribute_and_attribute_format(self, id_entity):
    entity = self.get_entity(id_entity, "Attributes.AttributeFormats")
    return self._get_entity_model_from_api_entity(entity)

  def _get_entity_model_from_api_entity(self, entity):
    self.logger.debug(f"[Entity Service][get_entity_model_with_attribute_and_attribute_format] Compose attributes for entity {entity.id}")
    attributes = self._parse_attributes(entity.attributes)  
    self.logger.debug(f"[Entity Service][get_entity_model_with_attribute_and_attribute_format] Compose load properties for entity {entity.id}")
    load_properties = self._parse_load_properties(entity, attributes)
    self.logger.debug(f"[Entity Service][get_entity_model_with_attribute_and_attribute_format] Compose reader properties for entity {entity.id}")
    reader_properties = self._parse_reader_properties(entity)
    return EntityModel(entity.id, entity.id_data_intake_process, entity.id_provider, entity.name, entity.table_name, entity.regular_expression, None, reader_properties, load_properties, None, attributes)


  def _parse_reader_properties(self, entity):
    file_format = constants.DEFAULT_FILE_FORMAT if entity.format is None else entity.format
    self.logger.debug(f"[Entity Service][_parse_reader_properties] Additional Properties {entity.additional_properties}")
    additional_properties = None if entity.additional_properties is None or entity.additional_properties.strip() == '' else json.loads(entity.additional_properties)
    reader_options = json.loads(constants.DEFAULT_READER_OPTIONS)
    if (not (additional_properties is None) and (constants.KEY_ADDITIONAL_PROPERTIES_READER_OPTIONS in additional_properties)):
        reader_options = additional_properties[constants.KEY_ADDITIONAL_PROPERTIES_READER_OPTIONS]
    return EntityReaderPropertiesModel(reader_options, entity.header_lines, file_format)
    
  def _parse_load_properties(self, entity, attributes):
    additional_properties = None if entity.additional_properties is None or entity.additional_properties.strip() == '' else json.loads(entity.additional_properties)
    self.logger.debug(f"[Entity Service][_parse_load_properties] Additional Properties {entity.additional_properties}")
    consolidation_mode = constants.DEFAULT_CONSOLIDATION_MODE if additional_properties is None or not constants.KEY_ADDITIONAL_PROPERTIES_CONSOLIDATION_MODE in additional_properties else additional_properties[constants.KEY_ADDITIONAL_PROPERTIES_CONSOLIDATION_MODE]
    
    # Data Preview
    data_preview = constants.DEFAULT_DATA_PREVIEW
    if additional_properties is not None and constants.KEY_ADDITIONAL_PROPERTIES_DATA_PREVIEW in additional_properties:
      if additional_properties[constants.KEY_ADDITIONAL_PROPERTIES_DATA_PREVIEW] in ['True', 'true', 'False', 'false']:
        data_preview = json.loads(additional_properties[constants.KEY_ADDITIONAL_PROPERTIES_DATA_PREVIEW].lower())
      else:
        data_preview = additional_properties[constants.KEY_ADDITIONAL_PROPERTIES_DATA_PREVIEW]

    # Anomaly Detection
    anomaly_detection = constants.DEFAULT_ANOMALY_DETECTION
    if additional_properties is not None and constants.KEY_ADDITIONAL_PROPERTIES_ANOMALY_DETECTION in additional_properties:
      if additional_properties[constants.KEY_ADDITIONAL_PROPERTIES_ANOMALY_DETECTION].lower() in ['True', 'true', 'False', 'false']:
        anomaly_detection = json.loads(additional_properties[constants.KEY_ADDITIONAL_PROPERTIES_ANOMALY_DETECTION].lower())
      else:
        anomaly_detection = additional_properties[constants.KEY_ADDITIONAL_PROPERTIES_ANOMALY_DETECTION]
    
    # PII Detection
    pii_detection = constants.DEFAULT_PII_DETECTION
    if additional_properties is not None and constants.KEY_ADDITIONAL_PROPERTIES_PII_DETECTION in additional_properties:
      if additional_properties[constants.KEY_ADDITIONAL_PROPERTIES_PII_DETECTION] in ['True', 'true', 'False', 'false']:
        pii_detection = json.loads(additional_properties[constants.KEY_ADDITIONAL_PROPERTIES_PII_DETECTION].lower())
      else:
        pii_detection = additional_properties[constants.KEY_ADDITIONAL_PROPERTIES_PII_DETECTION]
      
    pii_detection_language = constants.DEFAULT_PII_DETECTION_LANGUAGE if additional_properties is None or not constants.KEY_ADDITIONAL_PROPERTIES_PII_DETECTION_LANGUAGE in additional_properties else additional_properties[constants.KEY_ADDITIONAL_PROPERTIES_PII_DETECTION_LANGUAGE]
    has_encryption = any(attribute.is_encrypted for attribute in attributes) 
    generate_delta_table = constants.DEFAULT_GENERATE_DELTA_TABLE if entity.generate_delta_table is None else entity.generate_delta_table
    id_table_format = constants.DEFAULT_ID_TABLE_FORMAT if entity.id_table_format is None else entity.id_table_format
    null_text = None if entity.null_text is not None and entity.null_text.strip() == '' else entity.null_text
    return EntityLoadPropertiesModel(consolidation_mode, generate_delta_table, id_table_format, data_preview, has_encryption, null_text, entity.re_create_table_on_deployment, pii_detection, pii_detection_language, anomaly_detection)  
  
  def _parse_attributes(self, attributes_from_api):
    attributes = []
    for attribute in attributes_from_api:
      load_properties = self._parse_attributes_load_properties(attribute)
      attribute_formats = self._parse_attribute_formats(attribute.attribute_formats)
      attribute_model = AttributeModel(attribute.id, attribute.id_entity, attribute.name, attribute.order, attribute.is_primary_key, attribute.is_calculated, attribute.is_partition_column, attribute.is_metadata, attribute.hive_type, attribute.sql_type, attribute.is_encrypted, load_properties, attribute_formats)
      attributes.append(attribute_model)
    return sorted(attributes, key = lambda x: x.order)
  
  def _parse_attributes_load_properties(self, attribute):
    special_format = None if attribute.special_format is not None and attribute.special_format.strip() == '' else attribute.special_format
    replaced_text = None if attribute.replaced_text is not None and attribute.replaced_text.strip() == '' else attribute.replaced_text
    replacement_text = None if attribute.replacement_text is not None and attribute.replacement_text.strip() == '' else attribute.replacement_text
    validation_text = None if attribute.validation_text is not None and attribute.validation_text.strip() == '' else attribute.validation_text
    return AttributeLoadPropertiesModel(special_format, attribute.need_trim, replaced_text, replacement_text, attribute.treat_empty_as_null, attribute.is_nullable, validation_text, attribute.max_len)
  
  def _parse_attribute_formats(self, attribute_formats_from_api):
    attribute_formats = []
    for attribute_format in attribute_formats_from_api:
      attribute_format_model = AttributeFormatModel(attribute_format.id, attribute_format.id_attribute, attribute_format.source_value, attribute_format.reg_exp, attribute_format.hql_expression, attribute_format.lookup_expression)
      attribute_formats.append(attribute_format_model)
    return attribute_formats
  
  def create_or_get_entity(self, entity:EntityModel) -> EntityModel:
    existing_entity = self._get_entity_by_name_and_provider(entity.id_provider, entity.name)
    if (existing_entity is not None):
        return self.get_entity_model_with_attribute_and_attribute_format(existing_entity.id)
 
    entity_dto = EntityModel.map_entity_model_to_dto(entity)     
    return self.metadata_entity_api_instance.api_metadata_entities_post(body=entity_dto)
     
  
   #TODO: After field type analysis, this may be updated
  def get_sql_type(self, hive_type):
    hive_type = hive_type.upper()
    if (hive_type == "BOOLEAN"):
        return ("BIT") 
    if (hive_type == "DOUBLE"):
        return ("FLOAT") 
    if (hive_type == "STRING"):
        return ("NVARCHAR(MAX)") 
    if (hive_type == "TIMESTAMP"):
        return ("DATETIME2(7)")    
        
    return (hive_type)
       
  def create_attributes_from_data_frame(self, entity : EntityModel, df):
    if(entity.format == 'json'):
        df = df.select(*[to_json(col(col_name)).alias(col_name) if isinstance(df.schema[col_name].dataType, ArrayType) else col(col_name) for col_name in df.columns])
    ordered_types = [(col_name, str(df.schema[col_name].dataType).upper().replace("TYPE", "").replace("INTEGER", "INT").replace("()", "")) for col_name in df.columns]
    entity_attributes = self.attributes_api.api_metadata_attributes_get(field="IdEntity",text=entity.id).items
    attributes = []
    if(len(entity_attributes) == 0):
        order = 0
        attribute_load_properties_builder = AttributeLoadPropertiesBuilder()
        attribute_load_properties_builder.with_is_nullable(True)
        for columnInfo in ordered_types:
            hive_type = columnInfo[1]
            sql_type = self.get_sql_type(hive_type)
            order += 1
            attribute_model = AttributeBuilder() \
            .with_name(columnInfo[0]) \
            .with_order(order) \
            .with_databricks_type(hive_type) \
            .with_sql_type(sql_type) \
            .with_is_primary_key(False) \
            .with_load_properties(attribute_load_properties_builder.build()) \
            .build()
            attributes.append(attribute_model)

        metadata_attributes = self._get_metadata_attributes(order)
        attributes.extend(metadata_attributes)
        
        for attribute in attributes:
          attribute_dto = AttributeModel.map_attribute_model_to_dto(entity.id, attribute)
          self.attributes_api.api_metadata_attributes_post(body=attribute_dto) 
        return attributes
    
  def create_attributes_for_entity(self, id_entity, attributes):
    # Replaces all Attributes associated with the Entity with the provided ones
    body = attributes
    self.logger.debug(f"[Entity Service][create_attributes_for_entity] Creating attributes for entity: {attributes}")
    self.metadata_entity_api_instance.api_metadata_entities_id_entity_attributes_put(id_entity, body=body, api_version=constants.API_VERSION)

  def _get_metadata_attributes(self, initialOrder : int) -> list :
    attributes = []
    order = initialOrder

    load_date_attribute = AttributeBuilder().with_name(constants.ATTRIBUTE_NAME_LOAD_DATE).with_order(order).with_databricks_type("TIMESTAMP").with_sql_type("datetime2(7)").with_is_calculated(True).with_is_metadata(True).with_load_properties(AttributeLoadPropertiesBuilder().with_special_format("CURRENT_TIMESTAMP()").build()).build()
    attributes.append(load_date_attribute)

    order += 1
    passed_validation_attribute = AttributeBuilder().with_name(constants.ATTRIBUTE_NAME_PASSED_VALIDATION).with_order(order).with_databricks_type("BOOLEAN").with_sql_type("bit").with_is_calculated(True).with_is_metadata(True).with_load_properties(AttributeLoadPropertiesBuilder().with_is_nullable(True).build()).build()
    attributes.append(passed_validation_attribute)

    order += 1
    sidra_is_deleted_attribute = AttributeBuilder().with_name(constants.ATTRIBUTE_NAME_IS_DELETED).with_order(order).with_databricks_type("BOOLEAN").with_sql_type("bit").with_is_calculated(True).with_is_metadata(True).with_load_properties(AttributeLoadPropertiesBuilder().with_special_format(constants.ATTRIBUTE_NAME_IS_DELETED).build()).build()
    attributes.append(sidra_is_deleted_attribute)

    order += 1
    file_date_attribute = AttributeBuilder().with_name(constants.ATTRIBUTE_NAME_FILE_DATE).with_order(order).with_databricks_type("DATE").with_sql_type("date").with_is_calculated(True).with_is_metadata(True).with_is_partition_column(True).with_load_properties(AttributeLoadPropertiesBuilder().with_special_format(constants.ATTRIBUTE_NAME_FILE_DATE).build()).build()
    attributes.append(file_date_attribute)

    order += 1
    id_source_item_attribute = AttributeBuilder().with_name(constants.ATTRIBUTE_NAME_ASSET_ID).with_order(order).with_databricks_type("INT").with_sql_type("int").with_is_calculated(True).with_is_metadata(True).with_is_partition_column(True).with_load_properties(AttributeLoadPropertiesBuilder().with_special_format(constants.ATTRIBUTE_NAME_ASSET_ID).build()).build()
    attributes.append(id_source_item_attribute)
    return attributes


  def is_date_loaded(self, date, entity, date_format:str):
    try:
      if(entity.id is None):
          return False
      
      edl = self.entity_delta_load_api.api_metadata_entity_delta_load_get(field="idEntity",text=entity.id)
      edl_items = edl.to_dict()['items']
      edl_items_json = json.loads(json.dumps(edl_items))
      edl_id_entity = list(filter(lambda x: x["id_entity"] == entity.id and datetime.strptime(x["last_delta_value"], date_format) >= datetime.strptime(date, date_format), edl_items_json))
      
      if (len(edl_id_entity) == 0):
        return False
      else:
        return True
    except:
      return False
    
  def check_is_metadata_created(self, entity):
    try:
        if(entity.id is None):
          return False
        else:
          entity_attributes = self.attributes_api.api_metadata_attributes_get(field="IdEntity",text=entity.id).items
          if(len(entity_attributes) == 0):
            return False
          else:
            return True
    except:
        return False
    
  def save_date_entity_delta_load(self, id_entity, date: datetime, date_format: str):
    try:
        edl_dto = [{
            "IdEntity" : id_entity,
            "DeltaIsDate": True,
            "LastDeltaValue" : date.strftime(date_format),
            "NeedReload" : False,
            "EnableReload" : False
        }]
        
        edl = self.get_edl_for_entity(id_entity)
        id_edl = edl["id"]

        if(id_edl is not None and id_edl != -1): # if the entity exists in EntityDeltaLoad, the Id is added to the DTO for updating the record
            edl_dto[0]["Id"] = id_edl
            last_delta_value_edl = datetime.strptime(edl["last_delta_value"], date_format)

            if(last_delta_value_edl > date): # if the existing date is more recent than the provided, LastDeltaValue is not updated
                edl_dto[0]["LastDeltaValue"] = last_delta_value_edl.strftime(date_format)

        self.entity_delta_load_api.api_metadata_entity_delta_load_post(body=edl_dto)

    except Exception as e:
        raise Exception(f"{e}") from e
    
  def get_edl_for_entity(self, id_entity):
      edl = self.entity_delta_load_api.api_metadata_entity_delta_load_get(field="IdEntity",text=id_entity)
      edl_items = edl.to_dict()['items']
      edl_for_entity = {"id": None, "last_delta_value": None, "id_delta_attribute": None, "id_auxiliary_delta_attribute": None, "delta_is_date": None}
      for d in edl_items:
          if d.get("id_entity") == id_entity:
              id_edl = d.get("id")
              last_delta_value_edl = d.get("last_delta_value")
              id_delta_attribute_edl = d.get("id_delta_attribute")
              id_auxiliary_delta_attribute_edl = d.get("id_auxiliary_delta_attribute")
              delta_is_date_edl = d.get("delta_is_date")
              edl_for_entity = {"id": id_edl, "last_delta_value": last_delta_value_edl, "id_delta_attribute": id_delta_attribute_edl, "id_auxiliary_delta_attribute": id_auxiliary_delta_attribute_edl, "delta_is_date": delta_is_date_edl}

      return edl_for_entity
  
  def delete_entity(self, id):
    self.metadata_entity_api_instance.api_metadata_entities_id_delete(id=id, api_version=constants.API_VERSION)

  def is_incremental(self, entity_delta_load):
    id_edl = entity_delta_load["id"]
    return (id_edl is not None)
  
  def get_delta_attribute_name(self, id_entity, attributes):
    entity_delta_load = self.get_edl_for_entity(id_entity)
    attribute_name = None
    if (entity_delta_load["id_delta_attribute"] is not None):
      attribute_names = [attribute.name for attribute in attributes if attribute.id == int(entity_delta_load["id_delta_attribute"])]
      if (len(attribute_names) > 0):
        attribute_name = attribute_names[0]
    return (attribute_name)  
  
  def save_entity_delta_load(self, id_entity, edl):
    try:
        edl_dto = [{
            "IdEntity" : id_entity,
            "DeltaIsDate": edl["delta_is_date"],
            "LastDeltaValue" : edl["last_delta_value"],
            "NeedReload" : False,
            "EnableReload" : False,
            "IdDeltaAttribute": edl["id_delta_attribute"],
            "IdAuxiliaryDeltaAttribute": edl["id_auxiliary_delta_attribute"]
        }]
        
        id_edl = edl["id"]

        if(id_edl is not None and id_edl != -1): # if the entity exists in EntityDeltaLoad, the Id is added to the DTO for updating the record
            edl_dto[0]["Id"] = id_edl

        self.entity_delta_load_api.api_metadata_entity_delta_load_post(body=edl_dto)

    except Exception as e:
        raise Exception(f"{e}") from e  
  
  def update_entity_delta_load_in_incremental_loads(self, entity, incremental_load_new_max_value):
    if (incremental_load_new_max_value is not None):
      edl = self.get_edl_for_entity(entity.id)
      if (self.is_incremental(edl)):
        if (isinstance(incremental_load_new_max_value, datetime)):
          edl["last_delta_value"] = incremental_load_new_max_value.isoformat(sep=' ')
        else:
          edl["last_delta_value"] = incremental_load_new_max_value
        self.save_entity_delta_load(entity.id, edl)

