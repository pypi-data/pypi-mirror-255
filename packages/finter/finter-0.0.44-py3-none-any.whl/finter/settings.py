import finter
import logging


configuration = finter.Configuration()

api_client = finter.ApiClient(configuration)

logger = logging.getLogger("finter_sdk")
logger.setLevel(logging.INFO)

log_handler = logging.StreamHandler()
log_handler.setLevel(logging.INFO)  # 필요한 로깅 레벨 설정
logger.addHandler(log_handler)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log_handler.setFormatter(formatter)
