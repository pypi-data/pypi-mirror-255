import finter
import logging


configuration = finter.Configuration()

api_client = finter.ApiClient(configuration)

logger = logging.getLogger("finter_sdk")
logger.setLevel(logging.INFO)
