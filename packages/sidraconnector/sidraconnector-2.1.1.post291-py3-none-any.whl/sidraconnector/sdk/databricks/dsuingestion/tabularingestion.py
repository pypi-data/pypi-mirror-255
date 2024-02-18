import sys
from sidraconnector.sdk import constants
from sidraconnector.sdk.log.logging import Logger
from sidraconnector.sdk.storage.utils import Utils
from sidraconnector.sdk.databricks.dsuingestion.tabularingestionservice import TabularIngestionService
from sidraconnector.sdk.databricks.datapreview.datapreviewservice import DataPreviewService
from sidraconnector.sdk.databricks.reader.readerservice import ReaderService
from sidraconnector.sdk.metadata.entityservice import EntityService
from sidraconnector.sdk.metadata.marservice import MarService
from datetime import datetime

class TabularIngestion():
    def __init__(self, spark):
        self.spark = spark
        self.utils =  Utils(spark)
        self.logger = Logger(spark, self.__class__.__name__)
        self.reader_service = ReaderService(spark, self.logger)
        self.data_preview_service = DataPreviewService(spark, self.logger)
        self.entity_service = EntityService(spark)

    def process(self, asset_id : int, asset_uri : str, asset_is_full_extract : bool):
        ingestion_start_date = datetime.utcnow()
        self.logger.debug(f"[TabularIngestion] Asset_Id: {asset_id}, Asset_Uri:{asset_uri}, Asset_Is_Full_Extract: {asset_is_full_extract}")
        self.tabular_service = TabularIngestionService(self.spark, self.logger, asset_uri, asset_id, asset_is_full_extract)
        self.mar_service = MarService(self.spark)

        if self.tabular_service.asset_is_registered is False:
            registered_asset = self.tabular_service.register_asset()
            self.logger.debug(f"[TabularIngestion]: Registered asset: {registered_asset}")
            file_name = self.tabular_service.get_wasbs_file(registered_asset.destination_uri)
            self.logger.debug(f"[TabularIngestion]: Copying file: {registered_asset.source_uri} to {file_name}")
            self.tabular_service.copy_raw_file(registered_asset.source_uri, file_name)
            registered_asset_info = self.tabular_service.register_info(registered_asset)
            self.tabular_service.delete_source_file(registered_asset.source_uri)
        else: 
            file_name = self.utils.https_to_wasbs(self.tabular_service.asset_uri)

        self.tabular_service.set_metadata_information()

        file_dataframe = self.reader_service.read_file(file_name, self.tabular_service.entity)
        file_dataframe = self.tabular_service.add_is_deleted_column(file_dataframe)

        if self.tabular_service.get_consolidation_mode() == constants.CONSOLIDATION_MODE_SNAPSHOT:
            self.tabular_service.truncate_old_partition_from_same_file()

        column_names = self.tabular_service.get_non_calculated_field_names()
        self.tabular_service.delete_from_table()
        

        if file_dataframe.count() > 0:
            entity = self.tabular_service.get_entity() 

            # Get max value for Incremental Load
            incremental_load_new_max_value = None
            incremental_column = [c for c in file_dataframe.columns if c.lower()==constants.TEMPORAL_FIELD_NAME_DELTA_VALUE.lower()]
            if (len(incremental_column)>0):
                incremental_load_new_max_value = file_dataframe.agg({incremental_column[0]: "max"}).collect()[0][0]
                file_dataframe = file_dataframe.drop(incremental_column[0])
            else:
                # Note that, this will work with the main delta column only, not the secondary one, which is used for dates and expected to be included as column constants.TEMPORAL_FIELD_NAME_DELTA_VALUE
                delta_column = self.entity_service.get_delta_attribute_name(entity.id, entity.attributes)
                if (delta_column is not None):
                    incremental_load_new_max_value = file_dataframe.agg({delta_column: "max"}).collect()[0][0]


            file_dataframe = file_dataframe.toDF(*column_names)
            self.tabular_service.create_staging_table(file_dataframe)
            self.tabular_service.configure_query_optimization()
            self.tabular_service.create_table_staging_query()
            
            #if tabular_service.has_to_generate_change_data_feed() is True:
                # TODO: Not Implemented yet: It will be changed for Change Data Feed from Databricks
                #tabular_service.insert_data_into_delta_table() 
            #

            
            consolidation_mode = self.tabular_service.get_consolidation_mode()
            self.logger.debug(f"[TabularIngestion]: Starting ingestion with consolidation mode: {consolidation_mode}")
            if consolidation_mode == constants.CONSOLIDATION_MODE_SNAPSHOT:
                self.tabular_service.insert_snapshot_data_into_final_table()
            elif consolidation_mode == constants.CONSOLIDATION_MODE_MERGE:
                self.tabular_service.insert_merge_data_into_final_table() 
            else: # OVERWRITE MODE, not implemented yet
                error_message = f"[TabularIngestion] Consolidation mode {consolidation_mode} is not implemented"
                self.logger.error(error_message)
                self.mar_service.execute(entity.id, entity.id_provider, entity.id_data_intake_process, constants.CONSOLIDATION_MODE_UNKNOWN, ingestion_start_date, self.tabular_service._get_full_table_name(), file_dataframe.count())
                raise Exception(error_message)
            
            # Update EntityDeltaLoad in incremental loads
            self.entity_service.update_entity_delta_load_in_incremental_loads(entity, incremental_load_new_max_value)

            self.tabular_service.drop_staging_tables()
            
            #Mar
            self.mar_service.execute(entity.id, entity.id_provider, entity.id_data_intake_process, consolidation_mode, ingestion_start_date, self.tabular_service._get_full_table_name(), file_dataframe.count())

            # Generate DATA CATALOG
            if self.tabular_service.has_to_generate_data_catalog() is True:
                try: 
                    provider_database = self.tabular_service.get_provider_database()                 
                    entity_id = entity.id
                    entity_table = entity.table_name
                    asset_id = self.tabular_service.get_asset_id()
                    self.data_preview_service.create_sqlserver_datapreview_table(asset_id, constants.DATACATALOG_SAMPLE_NUMBER_RECORDS, provider_database, entity_table, entity_id)
                except:
                    self.logger.exception('Error on create_sqlserver_datapreview_table: %s' %sys.exc_info()[1])          

        self.tabular_service.finish_loading(file_dataframe.count())  

        # Data Quality validations
        try:
            import sidradataquality.sdk.databricks.utils as ValidationDatabricksUtils
            databricks_utils = ValidationDatabricksUtils.Utils(self.spark)

            if databricks_utils.service_is_enabled():
                self.logger.debug(f"Executing Data Quality validations.")
                from sidradataquality.sdk.data.validationservice import ValidationService as ValidationCheckService
                validation_check_service = ValidationCheckService(self.spark)
                executed = validation_check_service.execute_validations_for_entity_asset(entity.id, asset_id)
                if not executed:
                    self.logger.debug(f"Validations not available for current entity '{entity.table_name}' ({entity.id}).")
            else:
                self.logger.debug(f"Data Quality not deployed in current DSU.")

        except Exception as e:
            self.logger.exception("Exception on Asset {asset_id} Data Quality: {e}".format(asset_id= asset_id, e=e))


        # Anomaly Detection
        try:
            if (entity.load_properties.anomaly_detection):
                self.logger.debug(f"Executing Anomaly Detection.")
                # import delayed in case it fails (old cluster without pyod, is catched by the try/except)
                from sidraconnector.sdk.databricks.anomalydetection.anomalydetection import AnomalyDetection
                anomaly_detector = AnomalyDetection(self.spark)
                anomaly_detection_results = anomaly_detector.execute(entity.id, asset_id, constants.ANOMALY_DETECTION_DEFAULT_MAX_ASSET_HISTORY_LENGTH)
                return anomaly_detection_results
            else: 
                self.logger.debug(f"Anomaly Detection skipped as configured.")
        except Exception as e:
            self.logger.exception("Exception on Asset {asset_id} Anomaly Detection: {e}".format(asset_id= asset_id, e=e))
