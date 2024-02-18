import io
import logging
from collections.abc import Callable
from unittest import TestCase

from deci_platform_client import DeciPlatformClient


class TestRedirectOutput(TestCase):
    def _test_redirect_output(self) -> tuple[io.StringIO, io.StringIO]:
        print_message = "This is a test"
        logging_message = "This is different"
        with DeciPlatformClient.redirect_output() as (stdout, stderr):
            print(print_message)
            logging.warning(logging_message)
        stdout_value = stdout.getvalue()
        stderr_value = stderr.getvalue()
        self.assertEqual(stdout_value, f"{print_message}\n")
        self.assertEqual(stderr_value, f"{logging_message}\n")
        return stdout, stderr

    def test_redirect_output(self) -> None:
        self._test_redirect_output()

    def _test_logging_handler_removed(self, log_fn: Callable[[], None]) -> None:
        (stdout, stderr) = self._test_redirect_output()
        first_values = [stdout.getvalue(), stderr.getvalue()]
        log_fn()
        second_values = [stdout.getvalue(), stderr.getvalue()]
        self.assertListEqual(first_values, second_values)

    def test_logging_handler_removed_with_print(self) -> None:
        def log_fn() -> None:
            print("This is a test")

        self._test_logging_handler_removed(log_fn=log_fn)

    def test_logging_handler_removed_with_logging_info(self) -> None:
        def log_fn() -> None:
            logging.info("This is a different test")

        self._test_logging_handler_removed(log_fn=log_fn)

    def test_logging_handler_removed_with_logging_error(self) -> None:
        def log_fn() -> None:
            logging.error("This is yet another test")

        self._test_logging_handler_removed(log_fn=log_fn)
