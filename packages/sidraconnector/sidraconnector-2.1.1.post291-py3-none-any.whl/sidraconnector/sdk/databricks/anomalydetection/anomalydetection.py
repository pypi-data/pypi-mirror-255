from SidraCoreApiPythonClient.rest import ApiException
from SidraCoreApiPythonClient import MetadataAssetsAssetsApi
from requests.exceptions import ConnectionError
from time import sleep
from sidraconnector.sdk.log.logging import Logger
from sidraconnector.sdk.storage.utils import Utils as StorageUtils
from sidraconnector.sdk.api.sidra.core.utils import Utils as SidraAPIUtils
from sidraconnector.sdk import constants
from sidraconnector.sdk.log.notification import Notifications
import pandas as pd
import pyod

class AnomalyDetection():
    def __init__(self, spark):      
      self.spark = spark
      self.logger = Logger(spark, self.__class__.__name__)
      self._sidra_api_utils =  SidraAPIUtils(spark)
      self.sidra_core_api_client = self._sidra_api_utils.get_SidraCoreApiClient()
      self.assets_api_instance = MetadataAssetsAssetsApi(self.sidra_core_api_client)
      self.notifications = Notifications(spark)
    

    def notify(self, asset_id, attribute, anomaly_measure, model, score):
        message = f"Anomaly detected in Data Intake"    
        print({ 'assetId': asset_id,  'attribute': attribute, 'anomalyMeasure': anomaly_measure, 'model': model, 'score': score })
        self.logger.event(message, { 'assetId': asset_id,  'attribute': attribute, 'anomalyMeasure': anomaly_measure, 'model': model, 'score': score  })
        # TODO: WHAT HAPPENS WITH MULTIVARIATE? SHOULD WE INCLUDE ALL ATTRIBUTES AND ALL MEASURES?
        self.notifications.notify_anomaly(asset_id=asset_id, attribute=attribute, anomaly_measure=anomaly_measure, model=model, score=score)

    def translate_field_name(self, field_name):
        match field_name:
            case "byte_size":
                return "ByteSize"
            case "entities":
                return "Entities"
            case "validation_errors":
                return "ValidationErrors"        
                    
        return field_name

    def execute(self, entity_id, asset_id : int, max_asset_history_length = constants.DEFAULT_CONSOLIDATION_MODE):
        self.logger.debug("Starting Anomaly detection process for Asset {asset_id}.".format(asset_id = asset_id))
        
        # Get the last N assets
        assets = self.assets_api_instance.api_metadata_assets_get(take=max_asset_history_length, sort_field='LastUpdated', sort_desc=True, field='IdEntity', text=str(entity_id), exact_match=True)

        if (assets.total_items < constants.ANOMALY_DETECTION_MIN_ASSETS):
            print("Anomaly Detection skipped: Too few Assets.")
            self.logger.debug("Anomaly Detection skipped: Too few Assets.")
            return

        assets_list = []
        for item in assets.items:
            assets_list.append(item.to_dict())

        # Assets come in descending order, changet it to ascending
        assets_df = pd.DataFrame(assets_list[::-1])       

        # Include only finished Assets
        # TODO: IT WOULD BE BETTER TO FILTER WHEN OBTAINING THE ASSETS, BUT WE WOULD NEED ANOTHER METHOD FOR THAT, SINCE WE ALREADY NEED THE FILTER FOR EntityId
        assets_df = assets_df[assets_df.id_status == constants.ANOMALY_DETECTION_ASSET_STATUS]

        asset_id_int = int(asset_id) #cast to int is needed because the asset_id type is string and the dataframe id is int. Otherwise the filter does not work
       
        if (assets_df[assets_df.id == asset_id_int].empty): 
            raise Exception("Anomaly Detection: Invalid Asset Id")

        # Keep only the needed fields
        # TODO: Add validation_errors and ingestion_time when available
        assets_df = assets_df[["id", "last_updated", "entities", "byte_size"]]

        # Check for anomalies
        # TODO: We could use other method, or several methods and voting.
        from pyod.models.knn import KNN

        fields = ["entities", "byte_size"]
        
        # TODO: For Multivariate, do this only once with the entire fields array
        for field in fields:
            # Extract the features from the dataset
            X = assets_df[[field]]

            # Choose an anomaly detection algorithm from pyod
            # For example, we can use the KNN method
            detector = pyod.models.knn.KNN()

            # Fit the detector to the data
            detector.fit(X)

            # Get the anomaly scores of each observation
            scores = detector.decision_scores_

            # Get the labels of the outliers
            labels = detector.labels_

            # Add the scores and labels to the dataframe
            assets_df["score_{field}".format(field = field)] = scores
            assets_df["label_{field}".format(field = field)] = labels

            # CHECK IF THERE IS ANOMALY IN THE CURRENT ASSET.
            idx = assets_df[assets_df.id == asset_id_int].index
            label = assets_df.at[idx[0], "label_{field}".format(field = field)]

            # Notify if needed
            if (label == 1):
                print("Anomaly detected in {field}, notifying".format(field=field))
                self.logger.debug("Anomaly detected. asset_id: {asset_id}, field: {field}, value: {value}, model: {model}, score: {score}".format(asset_id=asset_id, field = field, value= float(assets_df.at[idx[0], field]), model="KNN", score=assets_df.at[idx[0], "score_{field}".format(field = field)]))
                # numpy Int64 is not serializable, but we convert to python's float
                self.notify(asset_id, self.translate_field_name(field), float(assets_df.at[idx[0], field]), "KNN", assets_df.at[idx[0], "score_{field}".format(field = field)])
        
        self.logger.debug("Anomaly detection process was run successfully for Asset {asset_id}.".format(asset_id = asset_id))
        return assets_df