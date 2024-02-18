# -----------------
# Attribute Model Dto
# -----------------

class AttributeModel():
  def __init__(self, id_attribute, id_entity, name, order, is_primary_key, is_calculated, is_partition_column, is_metadata, databricks_type, sql_type, is_encrypted, load_properties, attribute_formats):
    self.id = id_attribute
    self.id_entity = id_entity
    self.name = name
    self.order = order
    self.is_primary_key = is_primary_key
    self.is_calculated = is_calculated
    self.is_partition_column = is_partition_column
    self.is_metadata = is_metadata
    self.databricks_type = databricks_type.upper() if databricks_type else None
    self.sql_type = sql_type.upper() if sql_type else None
    self.is_encrypted = is_encrypted
    self.load_properties = load_properties
    self.attribute_formats = attribute_formats

  @classmethod
  def map_attribute_model_to_dto(self, id_entity : int, attributeModel) -> dict:
    attribute = {}
    attribute["IdEntity"] = id_entity
    attribute["Name"]=attributeModel.name
    attribute["HiveType"]=attributeModel.databricks_type
    attribute["MaxLen"] = attributeModel.load_properties.max_len
    attribute["IsNullable"] = attributeModel.load_properties.is_nullable
    attribute["NeedTrim"] = attributeModel.load_properties.need_trim
    attribute["RemoveQuotes"] = False
    attribute["ReplacedText"] = attributeModel.load_properties.replaced_text
    attribute["ReplacementText"] = attributeModel.load_properties.replacement_text
    attribute["SpecialFormat"]= attributeModel.load_properties.special_format
    attribute["TreatEmptyAsNull"] = attributeModel.load_properties.treat_empty_as_null
    attribute["IsPrimaryKey"] = attributeModel.is_primary_key
    attribute["Order"] =  attributeModel.order
    attribute["IsCalculated"] = attributeModel.is_calculated
    attribute["IsPartitionColumn"] = attributeModel.is_partition_column
    attribute["IsMetadata"] = attributeModel.is_metadata
    attribute["SQLType"] = attributeModel.sql_type
    attribute["ValidationText"] = attributeModel.load_properties.validation_text
    attribute["Description"] = None
    attribute["IsEncrypted"] = attributeModel.is_encrypted
    attribute["DataMask"] = None
    attribute["SourceType"] = None
    return attribute
  
  @classmethod
  def map_attributes_model_to_dto(self, id_entity, attributes):
    attributes_dto = [self.map_attribute_model_to_dto(id_entity, attribute) for attribute in attributes]
    return attributes_dto
    
class AttributeLoadPropertiesModel():
  def __init__(self, special_format, need_trim, replaced_text, replacement_text, treat_empty_as_null, is_nullable, validation_text, max_len):
    self.special_format = special_format
    self.need_trim = need_trim
    self.replaced_text = replaced_text
    self.replacement_text = replacement_text
    self.treat_empty_as_null = treat_empty_as_null
    self.is_nullable = is_nullable
    self.validation_text = validation_text
    self.max_len = max_len
    
class AttributeFormatModel():
  def __init__(self, id_attribute_format, id_attribute, source_value, regular_expression, databricks_expression, lookup_expression):
    self.id_attribute_format = id_attribute_format
    self.id_attribute = id_attribute
    self.source_value = source_value
    self.regular_expression = regular_expression
    self.databricks_expression = databricks_expression
    self.lookup_expression = lookup_expression
