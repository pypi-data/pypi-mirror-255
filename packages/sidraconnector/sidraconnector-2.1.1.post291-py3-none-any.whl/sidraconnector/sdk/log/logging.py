from sidraconnector.sdk.utils import SingletonMeta
from sidraconnector.sdk.databricks.utils import Utils

from applicationinsights import TelemetryClient # To be replaced by opencensus
import logging
import json
from opentelemetry._logs import (
    set_logger_provider
)
from opentelemetry.sdk._logs import (
    LoggerProvider,
    LoggingHandler
)
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

class LogConfiguration(metaclass=SingletonMeta):
    def __init__(self, spark):
        self._databricks_utils = Utils(spark)
        self.utils = Utils(spark)
        self.db_utils = self.utils.get_db_utils()
        self._execution_context = json.loads(self.db_utils.notebook.entry_point.getDbutils().notebook().getContext().toJson())
        self._instrumentation_key = self._databricks_utils.get_databricks_secret(scope='log', key='ApplicationInsights--InstrumentationKey')
        logger_provider = LoggerProvider()
        set_logger_provider(logger_provider)
        exporter = AzureMonitorLogExporter(connection_string = f"InstrumentationKey={self._instrumentation_key}")
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
        handler = LoggingHandler()
		# Attach LoggingHandler to Root logger
        logger = logging.getLogger()
        logger.addHandler(handler)   

class Logger():
    def __init__(self, spark, name, log_level = logging.DEBUG):
        LogConfiguration(spark)
        self.databricks_utils = Utils(spark)
        self._name = name
        self.utils = Utils(spark)
        self.db_utils = self.utils.get_db_utils()
        self._execution_context = json.loads(self.db_utils.notebook.entry_point.getDbutils().notebook().getContext().toJson())
        self._extra_properties = self._initialize_extra_properties()
        instrumentation_key = self.databricks_utils.get_databricks_secret(scope='log', key='ApplicationInsights--InstrumentationKey')
        self._telemetry_logger = TelemetryClient(instrumentation_key)
        self._logger = logging.getLogger(name)
        self._logger.setLevel(log_level)
   	
    def __del__(self):
        self._telemetry_logger.flush()
    
    def set_level(self, log_level):
        self._logger.setLevel(log_level)

    def _initialize_extra_properties(self):
        job_name = self._execution_context['tags'].get("jobName")
        if job_name is None:
            job_name = ""
        run_id = self._execution_context['tags'].get("runId")
        if run_id is None:
            run_id = ""
        return {'appName':'sidraconnector.sdk','log_name': self._name, 'job_name': job_name, 'run_id':run_id, 'user': self._execution_context['tags']['user']}

    def add_extra_properties(self, value : dict):
        self._extra_properties.update(value)

    def _set_extra_properties(self, arguments : dict):
        if 'extra' in arguments.keys():
            arguments['extra'].update(self._extra_properties)
        else:
            if arguments is None:
                arguments = {}
            arguments['extra'] = self._extra_properties
        return arguments

    def debug(self, msg, *args, **kwargs):
        self._set_extra_properties(kwargs)
        self._logger.debug(msg, *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self._set_extra_properties(kwargs)
        self._logger.info(msg, *args, **kwargs)
    
    def warning(self,msg, *args, **kwargs):
        self._set_extra_properties(kwargs)
        self._logger.warning(msg, *args, **kwargs)
    
    def error(self,msg, *args, **kwargs):
        self._set_extra_properties(kwargs)
        self._logger.error(msg, *args, **kwargs)
    
    def critical(self,msg, *args, **kwargs):
        self._set_extra_properties(kwargs)
        self._logger.critical(msg, *args, **kwargs)
    
    def exception(self,msg, *args, **kwargs):
        self._set_extra_properties(kwargs)
        self._logger.exception(msg, *args, **kwargs)
    
    def event(self, name, properties=None, measurements=None):
        self._telemetry_logger.track_event(name, properties, measurements)
    
    def flush(self):
        self._telemetry_logger.flush()
    