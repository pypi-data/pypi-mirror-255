from sidraconnector.sdk import constants
from sidraconnector.sdk.api.sidra.core.utils import Utils as CoreApiUtils
from sidraconnector.sdk.log.logging import Logger
import SidraCoreApiPythonClient

class DataIntakeProcessService():
    def __init__(self,spark):
        self.logger = Logger(spark, self.__class__.__name__)
        self.utils = CoreApiUtils(spark)
        sidra_core_api_client = self.utils.get_SidraCoreApiClient()
        self._metadata_dataintakeprocess_api_instance = SidraCoreApiPythonClient.MetadataDataIntakeProcessesDataIntakeProcessApi(sidra_core_api_client)

    def get_dataintakeprocess(self, id_dataintakeprocess):
        self.logger.debug(f"[DataIntakeProcess Service][get_dataintakeprocess] Retrieve dataintakeprocess {id_dataintakeprocess} information")
        dataintakeprocess = self._metadata_dataintakeprocess_api_instance.api_metadata_data_intake_processes_id_get(id_dataintakeprocess, api_version = constants.API_VERSION)
        return dataintakeprocess