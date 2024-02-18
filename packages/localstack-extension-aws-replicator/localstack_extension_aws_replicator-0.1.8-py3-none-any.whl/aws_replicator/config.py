from localstack.config import is_env_not_false
from localstack.constants import INTERNAL_RESOURCE_PATH

# handler path within the internal /_localstack endpoint
HANDLER_PATH_REPLICATE = f"{INTERNAL_RESOURCE_PATH}/aws/replicate"
HANDLER_PATH_PROXIES = f"{INTERNAL_RESOURCE_PATH}/aws/proxies"

# whether to clean up proxy containers
CLEANUP_PROXY_CONTAINERS = is_env_not_false("REPLICATOR_CLEANUP_PROXY_CONTAINERS")
