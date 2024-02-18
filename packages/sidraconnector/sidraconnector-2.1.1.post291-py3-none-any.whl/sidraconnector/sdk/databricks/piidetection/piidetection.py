from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from SidraCoreApiPythonClient import PIIPIIApi
from SidraCoreApiPythonClient.rest import ApiException
from SidraCoreApiPythonClient import MetadataEntitiesEntityApi
from signalrcore.hub_connection_builder import HubConnectionBuilder
from signalrcore.transport.websockets.connection import ConnectionState
from requests.exceptions import ConnectionError
from time import sleep
import urllib.parse
from sidraconnector.sdk.log.logging import Logger
from sidraconnector.sdk.storage.utils import Utils as StorageUtils
from sidraconnector.sdk.api.sidra.core.utils import Utils as SidraAPIUtils
from sidraconnector.sdk.log.notification import NotificationsSignalR
from sidraconnector.sdk.constants import *
import logging

class PIIDetection():
    def __init__(self, spark):
      self.spark = spark
      self.notification_signalR = NotificationsSignalR(spark)
      self.logger = self.logger = Logger(spark, self.__class__.__name__)
      self.storage_utils = StorageUtils(spark)
      self._sidra_api_utils =  SidraAPIUtils(spark)
      self.sidra_core_api_client = self._sidra_api_utils.get_SidraCoreApiClient()
      self.entities_api_instance = MetadataEntitiesEntityApi(self.sidra_core_api_client)
      # Create an instance of the API class
      self.pii_api_instance = PIIPIIApi(self.sidra_core_api_client)
      
    def create_analyzer(self):
        configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "es", "model_name": "es_core_news_lg"},
                        {"lang_code": "en", "model_name": "en_core_web_lg"}],
        }
        provider = NlpEngineProvider(nlp_configuration=configuration)
        nlp_engine_with_spanish = provider.create_engine()
        analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine_with_spanish, 
            supported_languages=["en", "es"]
        )
        return analyzer
    
    def get_token(self, api_client):
       return api_client.configuration.get_oauth2_token(api_client)
     
    def get_language(self, entity_language):
        if entity_language == "english":
            language = "en"
        elif entity_language == "spanish":
            language = "es"
        return language

    def get_analyze_entities(self, analyzer, source_item_id, total_entities, entities_detected_pii, execution_date):
        skip = 0
        take = 50
        while skip == 0 or skip < total_entities:
            result_entities = self.pii_api_instance.api_pii_entities_for_pii_detection_by_dip_dip_item_id_get(source_item_id, _date=execution_date, skip=skip, take=take)
            list_entities = result_entities.entities
            if total_entities == 0:
              total_entities = result_entities.total
              source_name = result_entities.data_intake_process_name
            for entity in list_entities:
                entity_id = int(entity.entity_id)
                language = self.get_language(entity.language)
                #Get the entities from the id
                entity_attributes = self.entities_api_instance.api_metadata_entities_id_get(entity_id, include='Attributes')
                assets_with_pii = False
                for asset in entity.assets:
                    try:
                        asset_id = int(asset.asset_id)
                        asset_destination_path = asset.destination_path
                        urlInWasbs = self.storage_utils.https_to_wasbs(asset_destination_path)
                        df = self.spark.read.format('parquet').load(urlInWasbs)
                        #Analyze PII
                        detected_pii = self.detect_pii(df, language, analyzer, entity_attributes)
                        if detected_pii:
                            assets_with_pii = True
                            self.logger.debug("The PII has been extracted from the asset with id {asset_id}.".format(asset_id=asset_id))
                    except Exception as e:
                        self.logger.error("There was an error when extracting PII from the asset with id {asset_id}. Exception message: {message} args: {args}".format(asset_id=asset_id, message=e.message, args=e.args))
                if assets_with_pii:
                    entities_detected_pii += 1
            skip += take    
        return total_entities, entities_detected_pii, source_name

    def notify(self, source_item_id, source_name, total_entities=0, entities_detected_pii=0, exception=' ', success=False):
        notificationType = 2
        notificationSubType = 7
        source = 'DataIntakeProcess'
        if success:
            message = "The PII detection for {source} Id {source_item_id} and name {source_name} has finished succesfully for {total_entities} Entities. PII was detected in {entities_detected_pii}.".format(source=source, source_item_id=source_item_id, source_name=source_name, total_entities=total_entities, entities_detected_pii=entities_detected_pii)
            notificationPayLoad = { 'EventResultType': 'Success', 'Source': source, 'SourceItemId': source_item_id, 'SourceName': source_name, 'TotalNumberEntities': int(total_entities), 'EntitiesDetectedWithPII': int(entities_detected_pii) }
            properties = {'custom_dimensions': notificationPayLoad }
            self.notification_signalR.notify_PII_detection('Success', source, source_item_id, source_name, None, total_entities, entities_detected_pii)
            self.logger.info('PII Detection Execution', extra=properties)
        else:
            message = "There was an error when executing the PII detection notebook for {source} Id {source_item_id} and name {source_name}. See the Log for more details. {e}".format(source=source, source_item_id=source_item_id, source_name=source_name, e=exception)
            notificationPayLoad = { 'EventResultType': 'Error', 'Source': source, 'SourceItemId': source_item_id, 'SourceName': source_name, 'Exception': exception }
            self.notification_signalR.notify_PII_detection('Error', source, source_item_id, source_name, exception)
  
        self.logger.info("{message}: {payload}".format(message=message, payload=notificationPayLoad))
  
  
    def clean_dataframe(self, df):
        metadata_columns = ['ModifiedDate', ATTRIBUTE_NAME_LOAD_DATE, ATTRIBUTE_NAME_FILE_DATE, ATTRIBUTE_NAME_PASSED_VALIDATION, ATTRIBUTE_NAME_ASSET_ID]
        df = df.drop(*metadata_columns)
        bool_columns = list(map(lambda column_type: column_type[0], filter(lambda column_type: column_type[1] == "boolean", df.dtypes)))
        df = df.drop(*bool_columns)
        return df

    def analyze_text(self,analyzer, df, column, detected_pii_attribute, language, entity_attributes):
        pii_counter = {} 
        entities=["EMAIL_ADDRESS", "PERSON", "PHONE_NUMBER", "ES_NIF", "US_ITIN", "US_SSN", "US_PASSPORT", "UK_NHS"]
        df = df.withColumn(column, df[column].cast('string'))
        df = df.filter(df[column].isNotNull())
        processed_data = df.count()
        text_to_analyze = df.select(column).rdd.map(lambda r: r[0]).collect() 
        results = list(map(lambda t: analyzer.analyze(text = t, entities = entities, language = language), text_to_analyze)) 
        list(map(lambda result: self.modify_dic(pii_counter, result[0].entity_type), filter(lambda result: result, results)))
        if pii_counter:
            self.analyze_pii(processed_data, column, pii_counter, detected_pii_attribute, entity_attributes)
  
    def modify_dic(self, dic, key):
        if key in dic:
            dic[key] = dic.get(key) + 1
        else:
            dic.setdefault(key, 1)
    
    def analyze_pii(self, processed_data, attribute_name, dic, detected_pii_attribute, entity_attributes):
        max_value = max(dic.values())
        if max_value > processed_data/2:
            max_pii = list(dic.keys())[list(dic.values()).index(max_value)]
            attribute = list(filter(lambda attribute: attribute.name == attribute_name, entity_attributes.attributes))
            id_attribute = attribute[0].id
            detected_pii_attribute.setdefault(id_attribute, max_pii)    
    
    def detect_pii(self, df, language, analyzer, entity_attributes):
        df = self.clean_dataframe(df)
        detected_pii_attribute = {} 
        self.spark.sparkContext.parallelize(map(lambda column: self.analyze_text(analyzer, df, column, detected_pii_attribute, language, entity_attributes), df.columns))
        message = "PII extracted: Detected attributes: {detected_pii_attribute} ; Total rows: {rows} ; Total columns: {columns}".format(detected_pii_attribute=detected_pii_attribute, rows=df.count(), columns=len(df.columns))
        self.logger.debug(message)
        try:
            # Relates attributes with PII tags.
            if detected_pii_attribute:
                api_response = self.pii_api_instance.api_pii_add_pii_tags_post(body=detected_pii_attribute)
                return True
            else:
                return False
        except ApiException as e:
            print("Exception when calling PiiApi->api_pii_add_pii_tags_post: {e}".format(e=e))            
            message = "Exception when calling PiiApi->api_pii_add_pii_tags_post: {e}".format(e=e)
            self.logger.exception(message)

    def execute(self, data_intake_process_itemId, execution_date):
        self.logger._logger.setLevel(logging.DEBUG)
        total_entities = 0
        entities_detected_pii = 0
        source_name = ' '
        try:
            #Presidio object
            analyzer = self.create_analyzer()
            total_entities, entities_detected_pii, source_name = self.get_analyze_entities(analyzer, data_intake_process_itemId, total_entities, entities_detected_pii, execution_date)
            self.notify(data_intake_process_itemId, source_name, total_entities=total_entities, entities_detected_pii=entities_detected_pii, success=True)
            self.logger.debug("PII detection process was run successfully.")
        except Exception as e:
            self.notify(data_intake_process_itemId, source_name, exception=e.args[0])
            self.logger.exception("Exception while detecting PII: {e}".format(e=e))

        self.logger.flush()
        sleep(20)