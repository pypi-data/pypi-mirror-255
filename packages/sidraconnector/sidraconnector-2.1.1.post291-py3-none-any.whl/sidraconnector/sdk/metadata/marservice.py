from sidraconnector.sdk.metadata.assetservice import AssetService
from sidraconnector.sdk.metadata.providerservice import ProviderService
from sidraconnector.sdk.metadata.entityservice import EntityService
from sidraconnector.sdk.metadata.dataintakeprocessservice import DataIntakeProcessService
from sidraconnector.sdk.log.logging import Logger
from sidraconnector.sdk.constants import *
from datetime import timedelta
from datetime import datetime
import SidraCoreApiPythonClient
from SidraCoreApiPythonClient.api.telemetry_telemetry_api import TelemetryTelemetryApi
from SidraCoreApiPythonClient.models.telemetry_models_telemetry_set_dto import TelemetryModelsTelemetrySetDTO
from SidraCoreApiPythonClient.rest import ApiException
from SidraCoreApiPythonClient.models.api_system_status_model_telemetry_sample_category_enum import APISystemStatusModelTelemetrySampleCategoryEnum
from SidraCoreApiPythonClient.api.metadata_entities_delta_loads_entity_delta_load_api import MetadataEntitiesDeltaLoadsEntityDeltaLoadApi as EntityDeltaLoadApi
from sidraconnector.sdk.api.sidra.core.utils import Utils as CoreApiUtils
import sidraconnector.sdk.databricks.utils as databricksutils
import json

class MarService():
    def __init__(self, spark):
        self.spark = spark
        self.logger = self.logger = Logger(spark, self.__class__.__name__)   
        self.assetService = AssetService(spark)
        sidra_core_api_client = CoreApiUtils(spark).get_SidraCoreApiClient()
        self.telemetryApi = TelemetryTelemetryApi(sidra_core_api_client)
        self.entityDeltaLoadApi = EntityDeltaLoadApi(sidra_core_api_client)
        self.dbutils = databricksutils.Utils(spark).get_db_utils()
        self.providerService = ProviderService(spark)
        self.entityService = EntityService(spark)
        self.dataintakeprocessService = DataIntakeProcessService(spark)
       
    def _calculate_mar(self, entity_id, complete_table_name, consolidation_mode):   
        mar = None    
        is_incremental = self._is_incremental(entity_id)

        if (consolidation_mode==CONSOLIDATION_MODE_MERGE or is_incremental):
            mar = self._merge_calculation(entity_id, complete_table_name)    
        elif(consolidation_mode==CONSOLIDATION_MODE_SNAPSHOT):
            mar = self._snapshot_calculation(entity_id, complete_table_name)
        else:
            self.logger.warning(f"Unknown consolidation_mode: {consolidation_mode}")
        
        self.logger.info("MAR calculated for entity {entity_id} with consolidation mode {consolidation_mode}. Value: {mar}.".format(entity_id=entity_id,consolidation_mode=consolidation_mode, mar=mar))
        
        return mar, is_incremental
    
    def _is_incremental(self, entity_id):
        edl = self.entityDeltaLoadApi.api_metadata_entity_delta_load_get(field="idEntity",text=entity_id).items
        return len(edl) > 0

    def _merge_calculation(self, entity_id, complete_table_name):      
        first_day_of_current_month = self.spark.sql("SELECT trunc(current_date(), 'MM') as first_day").first()[0]
        assets_current_month = self.assetService.get_recent_entity_assets(entity_id, first_day_of_current_month)

        min_AssetId = min(assets_current_month, key=lambda x: x.id).id
        max_AssetId = max(assets_current_month, key=lambda x: x.id).id
            
        mar = self.spark.sql("SELECT COUNT(*) as mar FROM {complete_table_name} WHERE {ATTRIBUTE_NAME_ASSET_ID} >= {min_AssetId} AND {ATTRIBUTE_NAME_ASSET_ID} <= {max_AssetId}".format(complete_table_name=complete_table_name, ATTRIBUTE_NAME_ASSET_ID=ATTRIBUTE_NAME_ASSET_ID, min_AssetId = min_AssetId, max_AssetId = max_AssetId)).first()["mar"]
        
        return mar

    #Snapshot calculation is made calculating the avg amount of active rows since the first day of month. The reason to use the avg is because snapshot mode can have multiple versions of the
    #same entry in table and using the avg is an easy way to estimate how many rows have received changes during the current month.
    def _snapshot_calculation(self, entity_id, complete_table_name):
        first_day_of_current_month = self.spark.sql("SELECT trunc(current_date(), 'MM') as first_day").first()[0] 
        assets = self.assetService.get_recent_entity_assets(entity_id, first_day_of_current_month)

        min_AssetId = min(assets, key=lambda x: x.id).id
        max_AssetId = max(assets, key=lambda x: x.id).id

        mar = self.spark.sql("SELECT AVG(inner_count) as mar FROM ( SELECT {ATTRIBUTE_NAME_ASSET_ID}, COUNT(1) as inner_count FROM {complete_table_name} WHERE {ATTRIBUTE_NAME_ASSET_ID} >= {min_AssetId} and {ATTRIBUTE_NAME_ASSET_ID} <= {max_AssetId} GROUP BY {ATTRIBUTE_NAME_ASSET_ID} ) as subquery".format(complete_table_name=complete_table_name, ATTRIBUTE_NAME_ASSET_ID=ATTRIBUTE_NAME_ASSET_ID, min_AssetId=min_AssetId,max_AssetId=max_AssetId)).first()["mar"]

        return mar

    def execute(self, entity_id, provider_id, dataintakeprocess_id, consolidation_mode, ingestion_start_date, complete_table_name, asset_row_count):
        
        try:
            mar, is_incremental = self._calculate_mar(entity_id, complete_table_name, consolidation_mode)
            totalRecordCount = self.spark.sql("SELECT COUNT(*) as recordCount FROM {complete_table_name}".format(complete_table_name=complete_table_name)).first()["recordCount"]
            installation_id = self.dbutils.secrets.get(scope="api", key="installation_id")
            if dataintakeprocess_id:
                dip = self.dataintakeprocessService.get_dataintakeprocess(dataintakeprocess_id)
                dip_item_id = dip.item_id
                dip_id_plugin = dip.id_plugin
            else:
                dip_item_id = None
                dip_id_plugin = None
            
            if( mar is None):
                comments = "Error. Unknown consolidation mode. MAR could not be calculated. Consolidation_mode received: {consolidation_mode}".format(consolidation_mode=consolidation_mode)
            else:
                comments = ''

            payload =  {
                    "InstallationId": installation_id,
                    "DIPId": dip_item_id, 
                    "ProviderId": self.providerService.get_provider_full(provider_id).item_id, 
                    "EntityId": self.entityService.get_entity(entity_id, '').item_id, 
                    "ConsolidationMode": consolidation_mode, 
                    "TotalRecordCount": totalRecordCount,
                    "RecordCount": asset_row_count,
                    "MAR": mar, 
                    "DSUIngestionStartDate": ingestion_start_date.strftime('%Y-%m-%d %H:%M:%S'), 
                    "DSUIngestionEndDate": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    "PluginId": dip_id_plugin,
                    "Comments": comments,
                    "Incremental": str(is_incremental)
            }
            sample = {
                "IdSampleCategory": APISystemStatusModelTelemetrySampleCategoryEnum.DIP, 
                "Payload": json.dumps(payload)
            }
            samples = []
            samples.append(sample)
            
            body = TelemetryModelsTelemetrySetDTO(samples)
            self.telemetryApi.api_telemetry_post(body=body,api_version=API_VERSION)

        except Exception as e:
            self.logger.exception(f"[MAR_Calculation] Exception calculating MAR for entity_id {entity_id} in consolidation_mode {consolidation_mode}: {e}")
            raise e
