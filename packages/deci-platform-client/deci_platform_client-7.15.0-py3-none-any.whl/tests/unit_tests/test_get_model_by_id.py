from unittest.mock import MagicMock, patch
from uuid import uuid4

from deci_platform_client.apis.tags.platform_api import PlatformApi

from .base_test_case import BaseTestCase

get_get_model_by_id_mock = patch.object(PlatformApi, "get_model_by_id")


class TestGetModelByID(BaseTestCase):
    @get_get_model_by_id_mock
    def test_get_model_by_id_string(self, get_model_by_id_mock: MagicMock) -> None:
        model_id = str(uuid4())
        response = self.client.get_model_by_id(model_id)
        get_model_by_id_mock.assert_called_once_with(path_params={"model_id": model_id})
        self.assertEqual(response, get_model_by_id_mock.return_value.body["data"])

    @get_get_model_by_id_mock
    def test_get_model_by_id_uuid(self, get_model_by_id_mock: MagicMock) -> None:
        model_id = uuid4()
        response = self.client.get_model_by_id(model_id)
        get_model_by_id_mock.assert_called_once_with(path_params={"model_id": model_id})
        self.assertEqual(response, get_model_by_id_mock.return_value.body["data"])
