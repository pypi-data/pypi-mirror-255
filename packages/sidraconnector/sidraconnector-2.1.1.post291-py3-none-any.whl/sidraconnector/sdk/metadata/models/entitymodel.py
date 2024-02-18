# -----------------
# Entity Model Dto
# -----------------
from sidraconnector.sdk import constants
import json

class EntityModel():
  def __init__(self, id_entity, id_data_intake_process, id_provider, name, table_name, regular_expression, start_valid_date, reader_properties, load_properties, additional_properties = {}, attributes = None):
    self.id = id_entity
    self.id_data_intake_process = id_data_intake_process
    self.id_provider = id_provider
    self.name = name
    self.table_name = table_name
    self.regular_expression = regular_expression
    self.start_valid_date = start_valid_date
    self.load_properties = load_properties
    self.reader_properties = reader_properties
    self.attributes = attributes
    self.additional_properties = additional_properties

  @classmethod
  def map_entity_model_to_dto(self, entityModel) -> dict:
    entity = {}
    entity["IdProvider"] = entityModel.id_provider
    entity["Name"]=entityModel.name
    entity["Description"]= None
    entity["TableName"] = entityModel.table_name
    entity["RegularExpression"] = entityModel.regular_expression
    entity["StartValidDate"] = entityModel.start_valid_date
    if(entityModel.reader_properties.header_lines is None):
      entity["HeaderLines"] = 0
    else:
      entity["HeaderLines"] = entityModel.reader_properties.header_lines
    entity["IdTableFormat"] = entityModel.load_properties.id_table_format
    entity["Format"] = entityModel.reader_properties.file_format
    entity["NullText"] = entityModel.load_properties.null_text
    entity["ReCreateTableOnDeployment"] =  entityModel.load_properties.re_create_table_on_deployment
    entity["FilesPerDrop"] = 1
    entity["SourcePath"] = None
    entity["GenerateDeltaTable"] = entityModel.load_properties.generate_delta_table
    entity["IdDataIntakeProcess"] = entityModel.id_data_intake_process
    additional_properties = {}
    if hasattr(entityModel, "additional_properties") and entityModel.additional_properties:
        additional_properties = entityModel.additional_properties

    if entityModel.load_properties.consolidation_mode != None:
      additional_properties[constants.KEY_ADDITIONAL_PROPERTIES_CONSOLIDATION_MODE] = entityModel.load_properties.consolidation_mode
    if entityModel.load_properties.data_preview != None:
      additional_properties[constants.KEY_ADDITIONAL_PROPERTIES_DATA_PREVIEW] = entityModel.load_properties.data_preview
    if entityModel.reader_properties.reader_options != None:
      additional_properties[constants.KEY_ADDITIONAL_PROPERTIES_READER_OPTIONS] = entityModel.reader_properties.reader_options
    if entityModel.load_properties.pii_detection != None:
      additional_properties[constants.KEY_ADDITIONAL_PROPERTIES_PII_DETECTION] = entityModel.load_properties.pii_detection
    if entityModel.load_properties.pii_detection_language != None:
      additional_properties[constants.KEY_ADDITIONAL_PROPERTIES_PII_DETECTION_LANGUAGE] = f"{entityModel.load_properties.pii_detection_language}"
    if entityModel.load_properties.has_encryption != None:
      additional_properties[constants.KEY_ADDITIONAL_PROPERTIES_ASSETS_ENCRYPTED] = entityModel.load_properties.has_encryption
        
    entity["AdditionalProperties"] = json.dumps(additional_properties)
    entity["ViewDefinition"] = None
    return entity
  
       
class EntityReaderPropertiesModel():
  def __init__(self, reader_options, header_lines, file_format):
    self.reader_options = reader_options
    self.header_lines = header_lines
    self.file_format = file_format
    
class EntityLoadPropertiesModel():
  def __init__(self, consolidation_mode, generate_delta_table, id_table_format, data_preview, has_encryption, null_text, re_create_table_on_deployment, pii_detection, pii_detection_language, anomaly_detection=constants.DEFAULT_ANOMALY_DETECTION):
    self.consolidation_mode = consolidation_mode
    self.generate_delta_table = generate_delta_table
    self.id_table_format = id_table_format
    self.data_preview = data_preview
    self.has_encryption = has_encryption
    self.null_text = null_text
    self.pii_detection = pii_detection
    self.pii_detection_language = pii_detection_language
    self.re_create_table_on_deployment = re_create_table_on_deployment
    self.anomaly_detection = anomaly_detection
