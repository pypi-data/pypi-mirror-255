from unittest.mock import MagicMock, patch

from deci_platform_client.apis.tags.platform_api import PlatformApi

from .base_test_case import BaseTestCase


class TestSendSupportLogs(BaseTestCase):
    @patch.object(PlatformApi, "log")
    def test_send_support_logs_empty_log(self, log_mock: MagicMock) -> None:
        self.client.send_support_logs(log="")
        log_mock.assert_not_called()

    @patch.object(PlatformApi, "log")
    def test_send_support_logs(self, log_mock: MagicMock) -> None:
        log = "this is quite the log"
        self.client.send_support_logs(log=log)
        log_mock.assert_called_once()
        # 0 for first call, 2 for **kwargs, "log_request_body" for parameter
        log_request_body = log_mock.mock_calls[0][2]["body"]
        self.assertEqual(log_request_body.log, log)
