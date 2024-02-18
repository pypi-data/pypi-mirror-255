from sidraconnector.sdk import constants
from sidraconnector.sdk.api.sidra.core.utils import Utils as CoreApiUtils
from sidraconnector.sdk.metadata.models.providermodel import ProviderModel
from sidraconnector.sdk.log.logging import Logger
import SidraCoreApiPythonClient

class ProviderService():
  def __init__(self, spark):
    self.logger = Logger(spark, self.__class__.__name__)
    self.utils = CoreApiUtils(spark)
    sidra_core_api_client = self.utils.get_SidraCoreApiClient()
    self._metadata_provider_api_instance = SidraCoreApiPythonClient.MetadataProvidersProviderApi(sidra_core_api_client)
  
  def get_provider(self, id_provider):
    # Returns MetadataProvidersProviderDTO
    self.logger.debug(f"[Provider Service][get_provider] Retrieve provider {id_provider} information")
    provider = self._metadata_provider_api_instance.api_metadata_providers_id_basicinfo_get(id_provider, api_version = constants.API_VERSION)
    return provider
  
  def get_provider_first_or_default(self, provider_item_id):
    try:
      provider = self._metadata_provider_api_instance.api_metadata_providers_get(field="ItemId",text=provider_item_id.lower()).items
      return next((p for p in provider if p.item_id == provider_item_id.lower()), None)
    except:
      return None
  
  def get_provider_model(self, id_provider):
    self.logger.debug(f"[Provider Service][get_provider_model] Get provider model. Provider id: {id_provider}")
    provider = self.get_provider(id_provider)
    providerModel = ProviderModel(id_provider, provider.provider_name, provider.database_name, provider.owner, provider.description)
    return providerModel
 
  def create_provider(self, provider:dict):
    body = provider
    provider = self._metadata_provider_api_instance.api_metadata_providers_post(body=body, api_version = constants.API_VERSION)
    providerModel = ProviderModel(provider.id, provider.provider_name, provider.database_name, provider.owner, provider.description)
    return providerModel
      
  def delete_provider(self, id):
    self._metadata_provider_api_instance.api_metadata_providers_id_delete(id=id, api_version = constants.API_VERSION)

  def get_provider_full(self, id_provider):
    self.logger.debug(f"[Provider Service][get_provider_full] Retrieve provider {id_provider} information")
    provider = self._metadata_provider_api_instance.api_metadata_providers_id_get(id_provider, api_version = constants.API_VERSION)
    providerModel = ProviderModel(id_provider, provider.provider_name, provider.database_name, provider.owner, provider.description, provider.item_id)
    return providerModel