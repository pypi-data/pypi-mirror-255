import SidraCoreApiPythonClient
import sidraconnector.sdk.databricks.utils as databricksutils

class Utils():
     def __init__(self, spark):
        self.spark = spark
        self.dbutils = databricksutils.Utils(spark).get_db_utils()
     
     def get_SidraCoreApiClient(self):
        # Configure OAuth2 access token for authorization: oauth2
        configuration = SidraCoreApiPythonClient.Configuration(
            host = self.dbutils.secrets.get(scope='api', key='api_url'),  
            auth_url = self.dbutils.secrets.get(scope='api', key='auth_url'),
            scope = self.dbutils.secrets.get(scope='api', key='scope'),
            client_id = self.dbutils.secrets.get(scope='api', key='client_id'),
            client_secret = self.dbutils.secrets.get(scope='api', key='client_secret')
        )
        return SidraCoreApiPythonClient.ApiClient(configuration)  