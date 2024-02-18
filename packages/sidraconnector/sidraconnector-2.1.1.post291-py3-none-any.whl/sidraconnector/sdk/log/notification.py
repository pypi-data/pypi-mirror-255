import SidraCoreApiPythonClient
from SidraCoreApiPythonClient.api.notifications_notifications_api import NotificationsNotificationsApi as NotificationsApi
from signalrcore.hub_connection_builder import HubConnectionBuilder
from signalrcore.transport.websockets.connection import ConnectionState
from requests.exceptions import ConnectionError
from sidraconnector.sdk.api.sidra.core.utils import Utils as SidraAPIUtils
from sidraconnector.sdk.log.logging import Logger
from sidraconnector.sdk import constants
from time import sleep
from enum import Enum
import json

NotificationType = Enum('NotificationType', ['GENERAL', 'INTAKE', 'APP'])
NotificationSubType = Enum('NotificationSubType', ['SECURITY', 'PIPELINE', 'CLUSTER', 'ANOMALY','SCHEMA', 'INFERENCE', 'PIIDETECTION', 'PLUGINUPGRADE'])

class Notifications():
    def __init__(self, spark) -> None:
      self._sidra_core_api_client = SidraAPIUtils(spark).get_SidraCoreApiClient()
      self._notificationsApi = NotificationsApi(self._sidra_core_api_client)
      self._logger = Logger(spark, self.__class__.__name__)

    def notify_pipeline_failed(self, pipeline_id :str, pipeline_name :str, entity_id :int, entity_type :str, error :str ):
        content = {
            'PipelineId' : pipeline_id,
            'PipelineName' : pipeline_name,
            'EntityId' : entity_id,
            'EntityType' : entity_type,
            'Error' : error
        }
        notifications_type = NotificationType.INTAKE
        notifications_subtype = NotificationSubType.PIPELINE
        self.notify(notifications_type, notifications_subtype, json.dumps(content))

    def notify_schema_changed(self, entity_id :int, entity_type :str, entity_name :str, provider_name :str, current_attributes :str, table_attributes :str):
        content = {
            'EntityId' : entity_id,
            'EntityType' : entity_type,
            'EntityName' : entity_name,
            'ProviderName' : provider_name,
            'CurrentAttributes' : current_attributes,
            'TableAttributes' : table_attributes
        }
        notifications_type = NotificationType.INTAKE
        notifications_subtype = NotificationSubType.SCHEMA
        self.notify(notifications_type, notifications_subtype, json.dumps(content))
    
    def notify_anomaly(self, asset_id :int, attribute :str, anomaly_measure : float, model: str, score: float):
        content = {
            'AssetId' : asset_id,
            'Attribute' : attribute,
            'AnomalyMeasure' : anomaly_measure,
            'Model' : model,
            'Score' : score
        }
        notifications_type = NotificationType.INTAKE
        notifications_subtype = NotificationSubType.ANOMALY
        self.notify(notifications_type, notifications_subtype, json.dumps(content))
    
    def notify_PII_detection(self, event_result_type :str, source :str, source_item_id :str, source_name :str, exception :str, total_number_entities = None, entities_detected_with_PII = None):
        content = {
            'EventResultType' : event_result_type,
            'Source' : source,
            'SourceItemId' : source_item_id,
            'SourceName' : source_name,
            'TotalNumberEntities' : total_number_entities,
            'EntitiesDetectedWithPII' : entities_detected_with_PII,
            'Exception' : exception
        }
        notifications_type = NotificationType.INTAKE
        notifications_subtype = NotificationSubType.PIIDETECTION
        self.notify(notifications_type, notifications_subtype, json.dumps(content))
    
    def notify(self, notifications_type: NotificationType, notifications_subtype : NotificationSubType, notifications_content):
        body = SidraCoreApiPythonClient.NotificationsNotificationDto
        body.notification_type = notifications_type.value
        body.notification_sub_type = notifications_subtype.value
        body.content = notifications_content
        self._notificationsApi.api_notifications_post(body = body, api_version=constants.API_VERSION)

    

class NotificationsSignalR():
    def __init__(self, spark) -> None:
      self._sidra_core_api_client = SidraAPIUtils(spark).get_SidraCoreApiClient()
      self._logger = Logger(spark, self.__class__.__name__)

    def notify_pipeline_failed(self, pipeline_id :str, pipeline_name :str, entity_id :int, entity_type :str, error :str ):
        content = {
            'PipelineId' : pipeline_id,
            'PipelineName' : pipeline_name,
            'EntityId' : entity_id,
            'EntityType' : entity_type,
            'Error' : error
        }
        notifications_type = NotificationType.INTAKE
        notifications_subtype = NotificationSubType.PIPELINE
        self.notify(notifications_type, notifications_subtype, json.dumps(content))

    def notify_schema_changed(self, entity_id :int, entity_type :str, entity_name :str, provider_name :str, current_attributes :str, table_attributes :str):
        content = {
            'EntityId' : entity_id,
            'EntityType' : entity_type,
            'EntityName' : entity_name,
            'ProviderName' : provider_name,
            'CurrentAttributes' : current_attributes,
            'TableAttributes' : table_attributes
        }
        notifications_type = NotificationType.INTAKE
        notifications_subtype = NotificationSubType.SCHEMA
        self.notify(notifications_type, notifications_subtype, json.dumps(content))
    
    def notify_anomaly(self, asset_id :int, attribute :str, anomaly_measure : float, model: str, score: float):
        content = {
            'AssetId' : asset_id,
            'Attribute' : attribute,
            'AnomalyMeasure' : anomaly_measure,
            'Model' : model,
            'Score' : score
        }
        notifications_type = NotificationType.INTAKE
        notifications_subtype = NotificationSubType.ANOMALY
        self.notify(notifications_type, notifications_subtype, json.dumps(content))
    
    def notify_PII_detection(self, event_result_type :str, source :str, source_item_id :str, source_name :str, exception :str, total_number_entities = None, entities_detected_with_PII = None):
        content = {
            'EventResultType' : event_result_type,
            'Source' : source,
            'SourceItemId' : source_item_id,
            'SourceName' : source_name,
            'TotalNumberEntities' : total_number_entities,
            'EntitiesDetectedWithPII' : entities_detected_with_PII,
            'Exception' : exception
        }
        notifications_type = NotificationType.INTAKE
        notifications_subtype = NotificationSubType.PIIDETECTION
        self.notify(notifications_type, notifications_subtype, json.dumps(content))
    
    def notify(self, notifications_type: NotificationType, notifications_subtype : NotificationSubType, notifications_content):
        hub_connection = self._get_hub_connection("notifications", self._sidra_core_api_client)
        hub_connection.send("NotifyAsync", [notifications_type.value, notifications_subtype.value, notifications_content])
        hub_connection.stop()

    def _get_hub_connection(self, hubName, api_client):
        hub_connection = (
            HubConnectionBuilder()
            .with_url(
                f"{api_client.configuration.host}/hubs/{hubName}",
                options={
                    "verify_ssl": False,
                    "access_token_factory": lambda: api_client.configuration.get_oauth2_token(api_client),
                },
            )
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 5,
                }
            )
            .build()
        )

        hub_connection.on_open(
            lambda: print("connection opened and handshake received ready to send messages")
        )
        hub_connection.on_close(lambda: print("connection closed"))

        hub_connection.start()
        num_wait_iterations = 3
        while hub_connection.transport.state != ConnectionState.connected:
            print("Connecting")
            sleep(5)
            num_wait_iterations -= 1
            if num_wait_iterations <= 0:
                raise ConnectionError(
                    "Server is not responding when starting a new connection."
                )

        return hub_connection