import json
from datetime import datetime, timedelta, timezone
from sidraconnector.sdk.metadata.models.providermodel import ProviderModel
from sidraconnector.sdk.metadata.models.entitymodel import EntityModel
from sidraconnector.sdk.metadata.models.entitymodel import EntityReaderPropertiesModel
from sidraconnector.sdk.metadata.models.entitymodel import EntityLoadPropertiesModel
from sidraconnector.sdk.metadata.models.attributemodel import AttributeModel
from sidraconnector.sdk.metadata.models.attributemodel import AttributeLoadPropertiesModel
from sidraconnector.sdk.metadata.models.attributemodel import AttributeFormatModel
from sidraconnector.sdk import constants

# COMMAND ----------

# -----------------
# Provider Builder
# -----------------

class ProviderBuilder():
  def __init__(self):
    self.id_provider = 0
    self.provider_name = None
    self.database_name = None 
    self.owner = None
    self.description = None

  def with_id(self, id):
    self.id_provider = id
    return self

  def with_database_name(self, database_name):
    self.database_name = database_name
    return self
  
  def with_name(self, name):
    self.provider_name = name
    return self
  
  def with_owner(self, owner):
    self.owner = owner
    return self
  
  def with_description(self, description):
    self.description = description
    return self
  
  def build(self):
    return ProviderModel(self.id_provider, self.provider_name, self.database_name, self.owner, self.description)
  

# COMMAND ----------

# ---------------
# Entity Builder
# ---------------

class EntityBuilder():
  def __init__(self):
    self.id_provider = 0
    self.id_entity = 0
    self.id_data_intake_process = None
    self.name = None
    self.table_name = None
    self.start_valid_date = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    self.regular_expression = None
    self.load_properties = LoadPropertiesBuilder().build()
    self.reader_properties = ReaderPropertiesBuilder().build()
    self.attributes = []
    self.additional_properties = {}

  def with_id(self, id):
    self.id_entity = id
    return self

  def with_id_provider(self, id):
    self.id_provider = id
    return self
  
  def with_id_data_intake_process(self, id):
    self.id_data_intake_process = id
    return self
  
  def with_name(self, name):
    self.name = name
    self.table_name= name.replace(' ', '_')
    return self  
  
  def with_table_name(self, table_name):
    self.table_name = table_name
    return self
  
  def with_default_regular_expression(self, provider_name, entity_name, format):
    regular_expression_datetime = "((?<year>\\d{4})(?<month>\\d{2})(?<day>\\d{2}))(?:-(?<hour>\\d{2})(?<minute>\\d{2})(?<second>\\d{2}))"
    self.regular_expression = "^{provider_name}_{entity_name}_{time_stamp_regular_expression}?.{format}".format(provider_name=provider_name.lower(), entity_name=entity_name, time_stamp_regular_expression=regular_expression_datetime, format=format)
    return self

  def with_regular_expression(self, regular_expression):
    self.regular_expression = regular_expression
    return self
  
  def with_load_properties(self, load_properties):
    self.load_properties = load_properties
    return self  
  
  def with_reader_properties(self, reader_properties):
    self.reader_properties = reader_properties
    return self  

  def with_additional_property(self, additional_property_name, additional_property_value):
    self.additional_properties[additional_property_name] = additional_property_value
    return self
  
  def with_additional_properties(self, additional_properties):
      self.additional_properties = additional_properties
      return self
  
  def with_attributes(self, attributes):
    self.attributes = attributes
    if (self.load_properties is not None):
      self.load_properties.has_encryption = any(attribute.is_encrypted for attribute in attributes)
    return self
  
  def build(self):
    return EntityModel(self.id_entity, self.id_data_intake_process, self.id_provider, self.name, self.table_name, self.regular_expression, self.start_valid_date, self.reader_properties, self.load_properties, self.additional_properties, self.attributes)   

class ReaderPropertiesBuilder():
  def __init__(self):
    self.file_format =  constants.DEFAULT_FILE_FORMAT
    self.reader_options = {}
    self.header_lines = 0
 
  def with_file_format(self, file_format):
    self.file_format = file_format
    return self
  
  def with_file_format_with_default_reader_options(self, file_format):
    self.file_format = file_format
    reader_options_json = {"header":True}
    if file_format == "xls":
      reader_options_json = {"header":0} #According to the documentation, the number of the header row is 0-indexed
    self.with_reader_options(reader_options_json)
    return self
  
  def with_reader_options(self, reader_options_json : dict):
    self.reader_options = reader_options_json
    return self  
     
  def with_header_lines(self, header_lines):
    self.header_lines = header_lines
    return self  
  
  def build(self):
    return EntityReaderPropertiesModel(self.reader_options, self.header_lines, self.file_format)
  
class LoadPropertiesBuilder():
  def __init__(self):
    self.consolidation_mode = constants.CONSOLIDATION_MODE_SNAPSHOT
    self.re_create_table_on_deployment = True
    self.generate_delta_table = False
    self.id_table_format = 3
    self.data_preview = constants.DEFAULT_DATA_PREVIEW
    self.has_encryption = False
    self.null_text = None
    self.pii_detection = False
    self.pii_detection_language = 'en'
    self.anomaly_detection = True

  def with_consolidation_mode(self, consolidation_mode):
    self.consolidation_mode = consolidation_mode
    return self

  def with_generate_delta_table(self, generate_delta_table):
    self.generate_delta_table = generate_delta_table
    return self
  
  def with_id_table_format(self, id_table_format):
    self.id_table_format = id_table_format
    return self
  
  def with_data_preview(self, data_preview):
    self.data_preview = data_preview
    return self  
    
  def with_has_encryption(self, has_encryption):
    self.has_encryption = has_encryption
    return self
  
  def with_null_text(self, null_text):
    self.null_text = null_text
    return self
  
  def with_re_create_table_on_deployment(self, re_create_table_on_deployment):
    self.re_create_table_on_deployment = re_create_table_on_deployment
    return self
  
  def with_pii_detection(self, pii_detection):
    self.pii_detection = pii_detection
    return self  
  
  def with_pii_detection_language(self, pii_detection_language):
    self.pii_detection_language = pii_detection_language
    return self    
  
  def with_anomaly_detection(self, anomaly_detection):
    self.anomaly_detection = anomaly_detection
    return self   
  
  def build(self):
    return EntityLoadPropertiesModel(self.consolidation_mode, self.generate_delta_table, self.id_table_format, self.data_preview, self.has_encryption, self.null_text, self.re_create_table_on_deployment, self.pii_detection, self.pii_detection_language, self.anomaly_detection)

# COMMAND ----------

# ------------------
# Attribute Builder
# ------------------

class AttributeBuilder():
  def __init__(self):
    self.id_attribute = 0
    self.id_entity = 0
    self.name = 'Attr'
    self.order = 1
    self.is_primary_key = False
    self.is_encrypted = False
    self.is_calculated = False
    self.is_partition_column = False  
    self.is_metadata = False
    self.databricks_type = 'STRING'
    self.load_properties = AttributeLoadPropertiesBuilder().build()
    self.attribute_formats = None
    self.sql_type = None

  def with_id(self, id_attribute):
    self.id_attribute = id_attribute
    return self
  
  def with_id_entity(self, id_entity):
    self.id_entity = id_entity
    return self
  
  def with_name(self, name):
    self.name = name
    return self

  def with_order(self, order):
    self.order = order
    return self

  def with_is_primary_key(self, is_primary_key):
    self.is_primary_key = is_primary_key
    return self
  
  def with_is_encrypted(self, is_encrypted):
    self.is_encrypted = is_encrypted
    return self
  
  def with_is_calculated(self, is_calculated):
    self.is_calculated = is_calculated
    return self  

  def with_is_partition_column(self, is_partition_column):
    self.is_partition_column = is_partition_column
    return self 
  
  def with_is_metadata(self, is_metadata):
    self.is_metadata = is_metadata
    return self 
  
  def with_databricks_type(self, databricks_type):
    self.databricks_type = databricks_type.upper()
    return self  
  
  def with_sql_type(self, sql_type):
    self.sql_type = sql_type.upper()
    return self  
  
  def with_load_properties(self, load_properties):
    self.load_properties = load_properties
    return self  
  
  def with_attribute_formats(self, attribute_formats):
    self.attribute_formats = attribute_formats
    return self
  
  def build(self):
    return AttributeModel(self.id_attribute, self.id_entity, self.name, self.order, self.is_primary_key, self.is_calculated, self.is_partition_column, self.is_metadata, self.databricks_type, self.sql_type, self.is_encrypted, self.load_properties, self.attribute_formats)
  
class AttributeLoadPropertiesBuilder():
  def __init__(self):
    self.special_format = None
    self.need_trim = False
    self.replaced_text = None
    self.replacement_text = None
    self.treat_empty_as_null = False
    self.is_nullable = False
    self.validation_text = None
    self.max_len = None

  def with_special_format(self, special_format):
    self.special_format = special_format
    return self

  def with_need_trim(self, need_trim):
    self.need_trim = need_trim
    return self
  
  def with_replaced_text(self, replaced_text):
    self.replaced_text = replaced_text
    return self
  
  def with_replacement_text(self, replacement_text):
    self.replacement_text = replacement_text
    return self
  
  def with_treat_empty_as_null(self, treat_empty_as_null):
    self.treat_empty_as_null = treat_empty_as_null
    return self
  
  def with_is_nullable(self, is_nullable):
    self.is_nullable = is_nullable
    return self 
  
  def with_validation_text(self, validation_text):
    self.validation_text = validation_text
    return self   
  
  def with_max_len(self, max_len):
    self.max_len = max_len
    return self  
  
  def build(self):   
    return AttributeLoadPropertiesModel(self.special_format, self.need_trim, self.replaced_text, self.replacement_text, self.treat_empty_as_null, self.is_nullable, self.validation_text, self.max_len)
  
class AttributeFormatBuilder():
  def __init__(self):
    self.id_attribute_format = 0
    self.id_attribute = 0
    self.source_value = '0'
    self.regular_expression = None
    self.databricks_expression = 'False'
    self.lookup_expression = None

  def with_id_attribute_format(self, id_attribute_format):
    self.id_attribute_format = id_attribute_format
    return self
    
  def with_id_attribute(self, id_attribute):
    self.id_attribute = id_attribute
    return self
  
  def with_source_value(self, source_value):
    self.source_value = source_value
    return self
  
  def with_databricks_expression(self, databricks_expression):
    self.databricks_expression = databricks_expression
    return self
  
  def with_regex_expression(self, regex_expression):
    self.regex_expression = regex_expression
    return self
  
  def with_lookup_expression(self, lookup_expression):
    self.lookup_expression = lookup_expression
    return self  
  
  def build(self):
    return AttributeFormatModel(self.id_attribute_format, self.id_attribute, self.source_value, self.regular_expression, self.databricks_expression, self.lookup_expression)  
