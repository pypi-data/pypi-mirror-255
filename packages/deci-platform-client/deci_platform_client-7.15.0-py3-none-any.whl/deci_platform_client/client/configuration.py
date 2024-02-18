import os
from typing import TYPE_CHECKING

from deci_platform_client.configuration import Configuration as BaseConfiguration

if TYPE_CHECKING:
    from typing import Any, Optional


class Configuration(BaseConfiguration):
    def __init__(
        self,
        proxy_headers: "Optional[dict[str, Any]]" = None,
    ):
        api_host = os.environ.get("DECI_API_HOST", "api.deci.ai")
        api_port = int(os.environ.get("DECI_API_PORT", "443"))
        https = os.environ.get("DECI_API_HTTPS") != "False"
        base_url = f"http{'s' if https else ''}://{api_host}:{api_port}"
        super().__init__(host=base_url)
        self.proxy = os.environ.get("DECI_CLIENT_PROXY_URL")
        self.proxy_headers = proxy_headers
