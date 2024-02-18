import os
import random
from unittest.mock import MagicMock, patch
from uuid import uuid4

import numpy as np
from deci_platform_client import DeciPlatformClient

from tests.mocks import ModelMetadataFactory

from .base_test_case import BaseTestCase

_REMOVE = "remove"
_UPLOAD_FILE_TO_S3 = "_upload_file_to_s3"
_PREPARE_MODEL = "_prepare_model"

_PREPARE_RETURN_VALUE = f"{uuid4()}"


class TestAddModelStart(BaseTestCase):
    def test_add_model_without_model_or_model_path(self) -> None:
        with self.assertRaises(TypeError):
            self.client._add_model_start(model_metadata=None)

    def test_add_model_with_model_or_model_path(self) -> None:
        with self.assertRaises(TypeError):
            self.client._add_model_start(model_metadata=None, model="a", model_path="b")

    @patch.object(os, _REMOVE)
    @patch.object(DeciPlatformClient, _UPLOAD_FILE_TO_S3)
    def test_add_model_non_pytorch(
        self,
        upload_file_to_s3_mock: MagicMock,
        os_remove_mock: MagicMock,
    ) -> None:
        model_metadata = ModelMetadataFactory()
        model_path = f"{uuid4()}"
        extra_args = {"these": "are", "some": "more", "keyword": "args"}
        with patch.object(
            DeciPlatformClient,
            _PREPARE_MODEL,
            return_value=(model_metadata, None),
        ) as prepare_model_mock:
            self.client._add_model_start(model_metadata=model_metadata, model_path=model_path, **extra_args)
        prepare_model_mock.assert_called_once_with(
            model=None,
            model_metadata=model_metadata,
            inputs_metadata=None,
            **extra_args,
        )
        upload_file_to_s3_mock.assert_called_once_with(model_path, model_metadata.name)
        os_remove_mock.assert_not_called()

    @patch.object(os, _REMOVE)
    @patch.object(DeciPlatformClient, _UPLOAD_FILE_TO_S3)
    def test_add_model_with_converted_model_path(
        self,
        upload_file_to_s3_mock: MagicMock,
        os_remove_mock: MagicMock,
    ) -> None:
        model_metadata = ModelMetadataFactory()
        model = f"{uuid4()}"
        inputs_metadata = {"input0": {"dtype": np.float32, "shape": (1, *(random.randint(1, 100) for _ in range(3)))}}
        with patch.object(
            DeciPlatformClient,
            _PREPARE_MODEL,
            return_value=(model_metadata, _PREPARE_RETURN_VALUE),
        ) as prepare_model_mock:
            metadata, _ = self.client._add_model_start(
                model_metadata=model_metadata,
                model=model,
                inputs_metadata=inputs_metadata,
            )
        prepare_model_mock.assert_called_once_with(
            model=model,
            model_metadata=model_metadata,
            inputs_metadata=inputs_metadata,
        )
        upload_file_to_s3_mock.assert_called_once_with(_PREPARE_RETURN_VALUE, model_metadata.name)
        os_remove_mock.assert_called_once_with(_PREPARE_RETURN_VALUE)
