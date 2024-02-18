from random import randint
from unittest.mock import ANY, MagicMock, patch
from uuid import uuid4

from deci_platform_client.apis.tags.platform_api import PlatformApi
from deci_platform_client.models import BatchSize, DeepLearningTask, HardwareType

from tests.helpers import get_random_enum_value
from tests.mocks import AccuracyMetricFactory

from .base_test_case import BaseTestCase

get_edit_model_mock = patch.object(PlatformApi, "edit_model")


class TestEditModel(BaseTestCase):
    def test_edit_model_without_arguments(self) -> None:
        with self.assertRaises(ValueError):
            self.client.edit_model(model_id=uuid4())

    @get_edit_model_mock
    def test_edit_model_string(self, edit_model_mock: MagicMock) -> None:
        model_id = str(uuid4())
        name = str(uuid4())
        description = str(uuid4())
        dl_task = get_random_enum_value(DeepLearningTask)
        primary_batch_size = get_random_enum_value(BatchSize)
        primary_hardware = get_random_enum_value(HardwareType)
        accuracy_metrics = [AccuracyMetricFactory.create() for _ in range(randint(1, 5))]
        input_dimensions = [[randint(1, 100) for _ in range(randint(1, 5))] for _ in range(randint(1, 5))]
        self.client.edit_model(
            model_id,
            name=name,
            description=description,
            dl_task=dl_task,
            primary_batch_size=primary_batch_size,
            primary_hardware=primary_hardware,
            accuracy_metrics=accuracy_metrics,
            input_dimensions=input_dimensions,
        )
        edit_model_mock.assert_called_once_with(path_params={"model_id": model_id}, body=ANY)
        edit_model_form_param = edit_model_mock.call_args[1]["body"]
        self.assertEqual(edit_model_form_param["name"], name)
        self.assertEqual(edit_model_form_param["description"], description)
        self.assertEqual(edit_model_form_param["dlTask"], dl_task)
        self.assertEqual(edit_model_form_param["primaryBatchSize"], primary_batch_size)
        self.assertEqual(edit_model_form_param["primaryHardware"], primary_hardware)
        self.assertCountEqual([[int(v) for v in t] for t in edit_model_form_param["inputDimensions"]], input_dimensions)
        self.assertCountEqual(edit_model_form_param["accuracyMetrics"], accuracy_metrics)

    @get_edit_model_mock
    def test_edit_model_uuid(self, edit_model_mock: MagicMock) -> None:
        model_id = uuid4()
        name = str(uuid4())
        self.client.edit_model(model_id, name=name)
        edit_model_mock.assert_called_once_with(path_params={"model_id": model_id}, body={"name": name})
