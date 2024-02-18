import sidraconnector.sdk.databricks.utils as databricksutils
from azure.storage.blob import BlobServiceClient

import urllib

class Utils():
    def __init__(self, spark):
        self.spark = spark
        self.dbutils = databricksutils.Utils(spark).get_db_utils()
     
    def https_to_wasbs(self, https_url):
        parts = https_url.split("/", 4)
        if ('@' in parts[2]):
            parts = https_url.split("/", 3)
            return "wasbs://{container_and_storage}/{path}".format(container_and_storage = urllib.parse.unquote(parts[2]), path = urllib.parse.unquote(parts[3]))
        else:
            return "wasbs://{container}@{storage}/{path}".format(container = urllib.parse.unquote(parts[3]), storage = urllib.parse.unquote(parts[2]), path = urllib.parse.unquote(parts[4]))
    