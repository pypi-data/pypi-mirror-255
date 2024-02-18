from unittest.mock import MagicMock, patch
from uuid import uuid4

from deci_platform_client import DeciPlatformClient
from deci_platform_client.apis.tags.platform_api import PlatformApi
from deci_platform_client.client.exceptions import UnsupportedLoadedModelFramework
from deci_platform_client.models import FrameworkType, ModelSource

from tests.mocks import ModelMetadataFactory
from tests.unit_tests.base_test_case import BaseTestCase

_ASSERT_MODEL_ARGUMENTS = "assert_model_arguments"
_SUPPORT = "support"
_CONVERT_RETURN_VALUE = uuid4()


class TestPrepareModel(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.inputs_metadata = {"random": {"mapping": "here"}}

    @patch.object(PlatformApi, _ASSERT_MODEL_ARGUMENTS)
    @patch.object(DeciPlatformClient, _SUPPORT)
    def test_prepare_non_pytorch_model(self, support_mock: MagicMock, assert_model_arguments_mock: MagicMock) -> None:
        model_metadata = ModelMetadataFactory()
        model_metadata, _ = self.client._prepare_model(model_metadata=model_metadata, model=None, inputs_metadata=None)
        support_mock.assert_not_called()
        assert_model_arguments_mock.assert_called_once_with(body=model_metadata)
        self.assertEqual(model_metadata["source"], ModelSource.SDK)

    @patch.object(PlatformApi, _ASSERT_MODEL_ARGUMENTS)
    @patch.object(DeciPlatformClient, _SUPPORT)
    def test_prepare_non_pytorch_model_with_model(
        self, support_mock: MagicMock, assert_model_arguments_mock: MagicMock
    ) -> None:
        model_metadata = ModelMetadataFactory()
        with self.assertRaises(UnsupportedLoadedModelFramework):
            self.client._prepare_model(model_metadata=model_metadata, model=model_metadata, inputs_metadata=None)
        support_mock.assert_not_called()
        assert_model_arguments_mock.assert_not_called()

    @patch.object(DeciPlatformClient, "convert_pytorch_to_onnx", return_value=_CONVERT_RETURN_VALUE)
    @patch.object(PlatformApi, _ASSERT_MODEL_ARGUMENTS)
    @patch.object(DeciPlatformClient, _SUPPORT)
    def test_prepare_pytorch_model(
        self,
        support_mock: MagicMock,
        assert_model_arguments_mock: MagicMock,
        convert_pytorch_to_onnx_mock: MagicMock,
    ) -> None:
        model_metadata = ModelMetadataFactory(framework=FrameworkType.PYTORCH)
        model_metadata_ret, ret = self.client._prepare_model(
            model_metadata=model_metadata,
            model=model_metadata,
            inputs_metadata=self.inputs_metadata,
        )
        support_mock.assert_called_once_with(tag="pytorch-to-onnx")
        assert_model_arguments_mock.assert_called_once_with(body=model_metadata_ret)
        convert_pytorch_to_onnx_mock.assert_called_once_with(
            local_loaded_model=model_metadata,
            inputs_metadata=self.inputs_metadata,
        )
        self.assertEqual(ret, _CONVERT_RETURN_VALUE)

    @patch.object(DeciPlatformClient, "convert_pytorch_to_onnx", return_value=_CONVERT_RETURN_VALUE)
    @patch.object(PlatformApi, _ASSERT_MODEL_ARGUMENTS)
    @patch.object(DeciPlatformClient, _SUPPORT)
    def test_prepare_pytorch_model_extra_args(
        self,
        support_mock: MagicMock,
        assert_model_arguments_mock: MagicMock,
        convert_pytorch_to_onnx_mock: MagicMock,
    ) -> None:
        model_metadata = ModelMetadataFactory(framework=FrameworkType.PYTORCH)
        extra_kwargs = {"this": "goes", "there": "wow"}
        model_metadata_ret, ret = self.client._prepare_model(
            model_metadata=model_metadata,
            model=model_metadata,
            inputs_metadata=self.inputs_metadata,
            **extra_kwargs,
        )
        support_mock.assert_called_once_with(tag="pytorch-to-onnx")
        assert_model_arguments_mock.assert_called_once_with(body=model_metadata_ret)
        convert_pytorch_to_onnx_mock.assert_called_once_with(
            local_loaded_model=model_metadata,
            inputs_metadata=self.inputs_metadata,
            **extra_kwargs,
        )
        self.assertEqual(ret, _CONVERT_RETURN_VALUE)
