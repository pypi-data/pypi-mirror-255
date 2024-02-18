from unittest.mock import ANY, MagicMock, patch
from uuid import uuid4

import numpy as np
from deci_platform_client import DeciPlatformClient
from deci_platform_client.apis.tags.platform_api import PlatformApi
from deci_platform_client.models import DatasetName

from tests.helpers import get_api_response_instance, get_random_enum_value
from tests.mocks import (
    APIResponseAddModelResponseFactory,
    APIStrResponseFactory,
    Model,
    ModelMetadataFactory,
)

from .base_test_case import BaseTestCase

_ADD_MODEL_START_RETURN = uuid4()
_ADD_MODEL_V2_RETURN = get_api_response_instance(APIResponseAddModelResponseFactory.create())
_COPY_MODEL_FILE_RETURN = get_api_response_instance(APIStrResponseFactory.create())


class TestRegisterModel(BaseTestCase):
    @patch.object(PlatformApi, "add_model_v2", return_value=_ADD_MODEL_V2_RETURN)
    def test_register_model(self, add_model_v2_mock: MagicMock) -> None:
        model_metadata = ModelMetadataFactory(
            framework="tf2", primaryBatchSize=1, datasetName=get_random_enum_value(DatasetName)
        )
        model = str(uuid4())
        extra_kwargs = {"wow": "look", "at": "all", "these": "kwargs"}
        with patch.object(
            DeciPlatformClient,
            "_add_model_start",
            return_value=(model_metadata, _ADD_MODEL_START_RETURN),
        ) as mock:
            ret = self.client.register_model(
                model=model,
                name=model_metadata["name"],
                framework=model_metadata["framework"],
                dl_task=model_metadata["dlTask"],
                input_dimensions=model_metadata["inputDimensions"],
                hardware_types=[model_metadata["primaryHardware"]],
                description=model_metadata.get("description"),
                dataset_name=model_metadata["datasetName"],
                **extra_kwargs,
            )
        mock.assert_called_once_with(
            model_metadata=ANY,
            model_path=model,
            inputs_metadata=None,
            **extra_kwargs,
        )
        model_metadata_param = mock.mock_calls[0][2]["model_metadata"]
        self.assertEqual(model_metadata_param["name"], model_metadata["name"])
        self.assertEqual(model_metadata_param["framework"], model_metadata["framework"])
        self.assertEqual(model_metadata_param["dlTask"], model_metadata["dlTask"])
        self.assertEqual(model_metadata_param["inputDimensions"], model_metadata["inputDimensions"])
        self.assertEqual(model_metadata_param["primaryHardware"], model_metadata["primaryHardware"])
        self.assertEqual(model_metadata_param.get("description"), model_metadata.get("description"))
        self.assertEqual(model_metadata_param["datasetName"], model_metadata["datasetName"])
        add_model_v2_mock.assert_called_once_with(body=ANY, query_params={"etag": _ADD_MODEL_START_RETURN})
        body_add_model_v2_param = add_model_v2_mock.mock_calls[0][2]["body"]
        self.assertCountEqual(body_add_model_v2_param["hardware_types"], [model_metadata["primaryHardware"]])
        for key, value in body_add_model_v2_param.model.items():
            if key == "primaryBatchSize":
                continue
            self.assertEqual(model_metadata_param[key], value)
        self.assertEqual(ret, _ADD_MODEL_V2_RETURN.body["data"]["modelId"])

    @patch.object(PlatformApi, "add_model_v2", return_value=_ADD_MODEL_V2_RETURN)
    @patch.object(PlatformApi, "copy_model_file_from_s3_uri", return_value=_COPY_MODEL_FILE_RETURN)
    def test_register_model_with_s3_link(
        self,
        copy_model_file_from_s3_uri_mock: MagicMock,
        add_model_v2_mock: MagicMock,
    ) -> None:
        model_metadata = ModelMetadataFactory(
            framework="tf2", primaryBatchSize=1, datasetName=get_random_enum_value(DatasetName)
        )
        model_s3_uri = "s3://bla/blu"
        with patch.object(
            DeciPlatformClient,
            "_add_model_start",
            return_value=(model_metadata, _ADD_MODEL_START_RETURN),
        ) as mock:
            ret = self.client.register_model(
                model=model_s3_uri,
                name=model_metadata["name"],
                framework=model_metadata["framework"],
                hardware_types=[model_metadata["primaryHardware"]],
            )
        mock.assert_not_called()
        copy_model_file_from_s3_uri_mock.assert_called_once_with(
            path_params={"model_name": model_metadata["name"]}, body={"s3_uri": model_s3_uri}
        )
        add_model_v2_mock.assert_called_once_with(body=ANY, query_params={"etag": _COPY_MODEL_FILE_RETURN.body["data"]})
        body_add_model_v2_param = add_model_v2_mock.mock_calls[0][2]["body"]
        self.assertCountEqual(body_add_model_v2_param["hardware_types"], [model_metadata["primaryHardware"]])
        self.assertEqual(ret, _ADD_MODEL_V2_RETURN.body["data"]["modelId"])

    @patch.object(PlatformApi, "add_model_v2", return_value=_ADD_MODEL_V2_RETURN)
    @patch.object(DeciPlatformClient, "convert_pytorch_to_onnx")
    @patch.object(DeciPlatformClient, "support", MagicMock())
    @patch.object(DeciPlatformClient, "_upload_file_to_s3")
    def test_register_pytorch_model(
        self,
        upload_file_mock: MagicMock,
        convert_pytorch_mock: MagicMock,
        add_model_v2_mock: MagicMock,
    ) -> None:
        model_metadata = ModelMetadataFactory(framework="pytorch", primary_batch_size=1)
        model = Model()
        inputs_metadata = {"input0": {"dtype": np.float32, "shape": (1, *model_metadata["inputDimensions"][0])}}
        extra_kwargs = {"wow": "look", "at": "all", "these": "kwargs"}
        ret = self.client.register_model(
            model=model,
            name=model_metadata["name"],
            framework=model_metadata["framework"],
            dl_task=model_metadata["dlTask"],
            inputs_metadata=inputs_metadata,
            hardware_types=[model_metadata["primaryHardware"]],
            description=model_metadata.get("description"),
            **extra_kwargs,
        )
        convert_pytorch_mock.assert_called_once_with(
            local_loaded_model=model,
            inputs_metadata=inputs_metadata,
            **extra_kwargs,
        )
        body_add_model_v2_param = add_model_v2_mock.mock_calls[0][2]["body"]
        model_metadata_param = body_add_model_v2_param.model
        self.assertEqual(model_metadata_param["name"], model_metadata["name"])
        self.assertNotEqual(model_metadata_param["framework"], model_metadata["framework"])
        self.assertEqual(model_metadata_param["framework"], "onnx")
        self.assertEqual(model_metadata_param["dlTask"], model_metadata["dlTask"])
        self.assertEqual(model_metadata_param["inputDimensions"], model_metadata["inputDimensions"])
        self.assertEqual(model_metadata_param["primaryHardware"], model_metadata["primaryHardware"])
        self.assertEqual(model_metadata_param.get("description"), model_metadata.get("description"))
        add_model_v2_mock.assert_called_once_with(body=ANY, query_params={"etag": upload_file_mock.return_value})
        self.assertCountEqual(body_add_model_v2_param["hardware_types"], [model_metadata["primaryHardware"]])
        self.assertEqual(ret, _ADD_MODEL_V2_RETURN.body["data"]["modelId"])
