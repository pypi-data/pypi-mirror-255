from random import randint
from unittest.mock import MagicMock, patch
from uuid import uuid4

from deci_platform_client.apis.tags.platform_api import PlatformApi

from .base_test_case import BaseTestCase

get_get_all_models_mock = patch.object(PlatformApi, "get_all_models")


class TestGetAllModels(BaseTestCase):
    @get_get_all_models_mock
    def test_get_all_models(self, get_all_models_mock: MagicMock) -> None:
        response = self.client.get_all_models()
        get_all_models_mock.assert_called_once_with(query_params={})
        self.assertEqual(response, get_all_models_mock.return_value.body["data"])

    @get_get_all_models_mock
    def test_get_all_models_with_ids(self, get_all_models_mock: MagicMock) -> None:
        ids = ["1", *[uuid4() for _ in range(randint(1, 10))]]
        response = self.client.get_all_models(ids=ids)
        get_all_models_mock.assert_called_once_with(query_params={"ids": [str(model_id) for model_id in ids]})
        self.assertEqual(response, get_all_models_mock.return_value.body["data"])
