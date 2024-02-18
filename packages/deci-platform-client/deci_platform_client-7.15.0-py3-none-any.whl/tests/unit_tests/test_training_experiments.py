from unittest.mock import MagicMock, patch
from uuid import uuid4

from deci_platform_client import DeciPlatformClient
from deci_platform_client.apis.tags.platform_api import PlatformApi
from deci_platform_client.models import (
    APIResponseDictStrAny,
    APIResponseTrainingExperiment,
    TrainingExperiment,
)

from tests.helpers import get_api_response_instance

from .base_test_case import BaseTestCase

EXPERIMENT_NAME = "a name"


def get_experiment_mock() -> TrainingExperiment:
    company_id = uuid4()
    return TrainingExperiment(name=EXPERIMENT_NAME, companyId=company_id, id=uuid4(), workspaceId=company_id)


@patch.object(
    PlatformApi,
    "start_experiment",
    return_value=get_api_response_instance(
        APIResponseTrainingExperiment(success=True, data=get_experiment_mock(), message="")
    ),
)
class TestTrainingExperiment(BaseTestCase):
    def test_register_experiment_unsuccessfully(self, start_experiment_mock: MagicMock) -> None:
        start_experiment_mock.return_value = get_api_response_instance(
            APIResponseTrainingExperiment(success=False, message="")
        )
        self.client.register_experiment(name=EXPERIMENT_NAME)
        self.assertEqual(None, self.client.experiment)

    def test_register_experiment_successfully(self, _: MagicMock) -> None:
        self.client.register_experiment(name=EXPERIMENT_NAME)
        self.assertEqual(EXPERIMENT_NAME, self.client.experiment.name)

    def test_save_experiment_file_non_existing(self, start_experiment_mock: MagicMock) -> None:
        start_experiment_mock.return_value = get_api_response_instance(
            APIResponseTrainingExperiment(success=False, message="")
        )
        self.client.register_experiment(name=EXPERIMENT_NAME)
        response = self.client.save_experiment_file(file_path="./non-existing.py")
        self.assertIsNotNone(response)

    @patch.object(PlatformApi, "get_experiment_upload_url", side_effect=Exception)
    def test_save_experiment_with_get_upload_url_exception(
        self,
        get_experiment_upload_url_mock: MagicMock,
        start_experiment_mock: MagicMock,
    ) -> None:
        self._test_save_experiment_file(get_experiment_upload_url_mock, start_experiment_mock)

    def _test_save_experiment_file(
        self,
        get_experiment_upload_url_mock: MagicMock,
        start_experiment_mock: MagicMock,
    ) -> None:
        self.client.register_experiment(name=EXPERIMENT_NAME)
        response = self.client.save_experiment_file(file_path=__file__)
        self.assertIsNotNone(response)
        response.join()
        get_experiment_upload_url_mock.assert_called_once_with(
            path_params={"experiment_id": start_experiment_mock.return_value.body["data"]["id"]},
            query_params={"filename": "test_training_experiments.py"},
        )

    @patch.object(
        PlatformApi,
        "get_experiment_upload_url",
        return_value=get_api_response_instance(
            APIResponseDictStrAny(success=True, data={"url": "", "fields": {}}, message=""),
        ),
    )
    @patch.object(DeciPlatformClient, "upload_file_to_s3", side_effect=Exception)
    def test_save_experiment_with_upload_file_to_s3_exception(
        self,
        upload_file_to_s3_mock: MagicMock,
        get_experiment_upload_url_mock: MagicMock,
        start_experiment_mock: MagicMock,
    ) -> None:
        self._test_save_experiment_file(get_experiment_upload_url_mock, start_experiment_mock)
        upload_file_to_s3_mock.assert_called_once()
