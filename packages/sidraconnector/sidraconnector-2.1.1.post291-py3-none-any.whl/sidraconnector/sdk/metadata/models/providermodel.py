# -------------------
# Provider Model Dto
# -------------------

class ProviderModel():
  def __init__(self, id_provider, provider_name, database_name, owner, description, item_id = None):
    self.id = id_provider
    self.provider_name = provider_name
    self.database_name = database_name 
    self.owner = owner
    self.description = description
    self.item_id = item_id
  
  @classmethod
  def map_provider_model_to_dto(self, providerModel) -> dict:
    provider = {}
    provider["IdProvider"] = providerModel.id
    provider["ProviderName"] = providerModel.provider_name
    provider["DatabaseName"] = providerModel.database_name
    provider["Owner"] = providerModel.owner
    provider["Description"] = providerModel.description
    return provider
  