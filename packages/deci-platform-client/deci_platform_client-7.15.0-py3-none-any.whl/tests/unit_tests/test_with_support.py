import logging
from typing import Optional
from unittest.mock import MagicMock, patch

from deci_platform_client import DeciPlatformClient
from deci_platform_client.models import SentryLevel

from .base_test_case import BaseTestCase


@patch.object(DeciPlatformClient, "send_support_logs")
class TestWithSupport(BaseTestCase):
    @staticmethod
    def _get_logged_output(print_str: Optional[str] = None, log_str: Optional[str] = None):
        stdout = f"{print_str}\n" if print_str is not None else ""
        logs = f"{log_str}\n" if log_str is not None else ""
        return f"stdout:\n{stdout}\nlogging:\n{logs}"

    def test_with_support_exception(self, send_support_logs_mock: MagicMock) -> None:
        log = "This should be sent"
        try:
            with self.client.support():
                print(log)
                raise ValueError("Oh noes")
        except ValueError:
            pass
        send_support_logs_mock.assert_called_once_with(level=None, log=self._get_logged_output(print_str=log), tag=None)

    def _test_with_support(
        self,
        *,
        send_support_logs_mock: MagicMock,
        print_str: Optional[str] = None,
        log_str: Optional[str] = None,
        level: Optional[SentryLevel] = None,
        tag: Optional[str] = None,
    ) -> None:
        with self.client.support():
            if print_str is not None:
                print(print_str)
            if log_str is not None:
                logging.warning(log_str)
        send_support_logs_mock.assert_called_once_with(
            level=level,
            log=self._get_logged_output(print_str=print_str, log_str=log_str),
            tag=tag,
        )

    def test_with_support_empty(self, send_support_logs_mock: MagicMock) -> None:
        self._test_with_support(send_support_logs_mock=send_support_logs_mock)

    def test_with_support_print(self, send_support_logs_mock: MagicMock) -> None:
        self._test_with_support(send_support_logs_mock=send_support_logs_mock, print_str="help")

    def test_with_support_log(self, send_support_logs_mock: MagicMock) -> None:
        self._test_with_support(send_support_logs_mock=send_support_logs_mock, log_str="I need somebody")

    def test_with_support_print_and_log(self, send_support_logs_mock: MagicMock) -> None:
        self._test_with_support(
            send_support_logs_mock=send_support_logs_mock,
            print_str="not just anybody",
            log_str="help me",
        )
