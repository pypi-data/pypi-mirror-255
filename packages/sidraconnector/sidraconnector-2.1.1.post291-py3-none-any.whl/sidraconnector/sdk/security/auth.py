from sidraconnector.sdk.databricks.utils import Utils
import json
import requests

class Auth():
    def __init__(self, spark):
        self.spark = spark
        self.databricks_utils = Utils(spark)

    def get_token(self):   
        tenant_id = self.databricks_utils.get_databricks_secret("api", "tenant")
        application_id = self.databricks_utils.get_databricks_secret('api', 'application_id')
        application_secret = self.databricks_utils.get_databricks_secret('api', 'application_secret')
        auth_url = 'https://login.microsoftonline.com/{tenantID}/oauth2/v2.0/token'.format(tenantID = tenant_id)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload='grant_type=client_credentials&client_id={id}&client_secret={secret}&scope=https://vault.azure.net/.default'.format(id=application_id, secret=application_secret)

        r = requests.post(url=auth_url, headers=headers, data=payload)
        data = r.json()
        return data['access_token']        