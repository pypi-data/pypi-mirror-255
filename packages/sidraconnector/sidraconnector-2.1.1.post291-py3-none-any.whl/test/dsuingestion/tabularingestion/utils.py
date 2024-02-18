
class Utils:
 
  @classmethod
  def get_table(cls, spark, database_name, table_name):
    tables_df = spark.catalog.listTables(dbName=database_name)
    tables_filtered = [table for table in tables_df if table.name.lower() == table_name.lower()]
    return tables_filtered