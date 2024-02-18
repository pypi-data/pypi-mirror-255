from sidraconnector.sdk.databricks.utils import Utils
from sidraconnector.sdk.security.auth import Auth
import requests
import json

class SettingsService():
    def __init__(self, spark):
        self.spark = spark
        self.databricks_utils = Utils(spark)
        self.auth = Auth(spark)
        self.token = self.auth.get_token()

    def get_dsu_secret(self, secret_name):
        dsu_akv = self.databricks_utils.get_databricks_secret('resources', 'dsu_key_vault_name')
        url = 'https://{key_vault}.vault.azure.net/secrets/{secret_name}?api-version=2016-10-01'.format(key_vault=dsu_akv, secret_name=secret_name)
        
        try: 
            headers = {'Authorization': f'Bearer {self.token}'}
            r = requests.get(url=url, headers=headers)
        except: # TODO: See if we can catch a specific exception
            self.token = self.auth.get_token()
            headers = {'Authorization': f'Bearer {self.token}'}
            r = requests.get(url=url, headers=headers)
        
        data = r.json()
        if ('value' in data):
            return data['value']
        else:
            raise(Exception(data))
    