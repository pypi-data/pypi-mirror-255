import uuid

class Utils():
    def __init__(self, spark):
        self.spark = spark
        self.dbutils = self.get_db_utils()
    
    def execute_sql_queries(self, queries):
        for query in queries:
            self.spark.sql(query)

    def get_databricks_secret(self, scope, key):
        try:
            return self.dbutils.secrets.get(scope=scope, key=key)
        except:
            return ''

    def get_db_utils(self):
        dbutils = None      
        if self.spark.conf.get("spark.databricks.service.client.enabled") == "true":            
            from pyspark.dbutils import DBUtils
            dbutils = DBUtils(self.spark)        
        else:            
            import IPython
            dbutils = IPython.get_ipython().user_ns["dbutils"]        
        return dbutils
    
    def get_notebook_parameter(self, key):
        try:
            return self.dbutils.widgets.get(key)
        except:
            return None 