from unittest import TestCase

from deci_platform_client import DeciPlatformClient


class BaseTestCase(TestCase):
    def setUp(self) -> None:
        self.client = DeciPlatformClient()
