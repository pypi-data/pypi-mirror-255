import os
from typing import TYPE_CHECKING
from unittest import TestCase

import numpy as np
import onnx
import super_gradients
from deci_platform_client import DeciPlatformClient
from parameterized import parameterized
from transformers import (
    AutoModel,
    AutoModelForCausalLM,
    AutoModelForSequenceClassification,
    BertForSequenceClassification,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any

NLP_MODELS_INPUTS_METADATA = {
    "input_ids": {
        "dtype": np.int64,
        "shape": (1, 128),
    },
    "attention_mask": {
        "dtype": np.int64,
        "shape": (1, 128),
    },
}

NLP_MODELS_DYNAMIC_AXES = {
    "input_ids": {0: "batch_size", 1: "sequence"},
    "attention_mask": {0: "batch_size", 1: "sequence"},
}


class TestConvertPytorchToOnnx(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super_gradients.init_trainer()

    def tearDown(self) -> None:
        if hasattr(self, "converted_model_path"):
            os.remove(self.converted_model_path)

    @parameterized.expand(
        [
            (
                "resnet18",
                (
                    {
                        "input0": {
                            "dtype": np.float32,
                            "shape": (1, 3, 224, 224),
                        },
                    }
                ),
            ),
            (
                "yolox_t",
                (
                    {
                        "input0": {
                            "dtype": np.float32,
                            "shape": (1, 3, 320, 320),
                        },
                    }
                ),
            ),
            (
                "regseg48",
                (
                    {
                        "input0": {
                            "dtype": np.float32,
                            "shape": (1, 3, 224, 224),
                        },
                    }
                ),
            ),
        ]
    )
    def test_convert_super_gradients_pytorch_to_onnx(self, architecture: str, inputs_metadata) -> None:
        model = super_gradients.training.models.get(model_name=architecture, num_classes=1000)
        self.converted_model_path = DeciPlatformClient.convert_pytorch_to_onnx(
            local_loaded_model=model,
            inputs_metadata=inputs_metadata,
            export_path=f"{architecture.replace('/', '-').strip().lower()}.onnx",
        )
        self._assert_onnx_checkpoint(self.converted_model_path)

    @parameterized.expand(
        [
            # TODO: Commented for CI speedup
            (
                "microsoft/MiniLM-L12-H384-uncased",
                NLP_MODELS_INPUTS_METADATA,
                NLP_MODELS_DYNAMIC_AXES,
                BertForSequenceClassification,
            ),
            (
                "distilroberta-base",
                NLP_MODELS_INPUTS_METADATA,
                NLP_MODELS_DYNAMIC_AXES,
                AutoModelForSequenceClassification,
            ),
            (
                "distilbert-base-uncased",
                NLP_MODELS_INPUTS_METADATA,
                NLP_MODELS_DYNAMIC_AXES,
                AutoModelForSequenceClassification,
            ),
            (
                "distilbert-base-uncased-finetuned-sst-2-english",
                NLP_MODELS_INPUTS_METADATA,
                NLP_MODELS_DYNAMIC_AXES,
                AutoModelForSequenceClassification,
            ),
            (
                "bert-base-uncased",
                NLP_MODELS_INPUTS_METADATA,
                NLP_MODELS_DYNAMIC_AXES,
                AutoModelForCausalLM,
            ),
            (
                "facebook/bart-base",
                NLP_MODELS_INPUTS_METADATA,
                NLP_MODELS_DYNAMIC_AXES,
                AutoModelForCausalLM,
            ),
        ]
    )
    def test_convert_transformers_pytorch_to_onnx(
        self,
        huggingface_model_name: str,
        inputs_metadata: "Mapping[str, Mapping[str, Any]]",
        dynamic_axes: "Mapping[str, Any]",
        auto_model_class: "AutoModel",
    ) -> None:
        # return_dict=False is required to avoid Dict layers in ONNX that are not supported yet.
        model = auto_model_class.from_pretrained(huggingface_model_name, return_dict=False)
        self.converted_model_path = DeciPlatformClient.convert_pytorch_to_onnx(
            local_loaded_model=model,
            inputs_metadata=inputs_metadata,
            dynamic_axes=dynamic_axes,
            export_path=f"{huggingface_model_name.replace('/', '-').strip().lower()}.onnx",
        )
        self._assert_onnx_checkpoint(self.converted_model_path)

    def test_convert_multi_inputs_cv_model_to_onnx(self):
        import torch

        class MultiInputCVModel(torch.nn.Module):
            def __init__(self):
                super(MultiInputCVModel, self).__init__()

                # Layers
                self.pool = torch.nn.MaxPool2d(2, 2)
                self.conv1 = torch.nn.Conv2d(3, 16, (3, 3))
                self.conv2 = torch.nn.Conv2d(16, 8, (3, 3))
                self.fc1 = torch.nn.Linear(54, 432)  # 432x54
                self.fc2 = torch.nn.Linear(432, 128)
                self.fc3 = torch.nn.Linear(128, 64)
                self.fc4 = torch.nn.Linear(64, 1)

            def forward(self, input0, input1) -> tuple[torch.Tensor, torch.Tensor]:
                x = input0 * input1
                conv1_hidden_state = self.pool(self.conv1(input0))
                conv1_hidden_state *= conv1_hidden_state
                x = self.pool(self.conv1(x))
                x = self.pool(self.conv2(x))
                x = torch.relu(self.fc1(x))
                x = torch.relu(self.fc2(x))
                x = torch.relu(self.fc3(x))
                x = torch.relu(self.fc4(x))
                return x, conv1_hidden_state

        bs = 4
        x0 = torch.randn((bs, 3, 224, 224))
        x1 = torch.randn((bs, 1, 224, 224))
        model = MultiInputCVModel()
        x, conv1_hidden_state = model(x0, x1)
        self.assertEqual(tuple(x.shape), (bs, 8, 54, 1))

        inputs_metadata = {
            "input0": {"dtype": np.float32, "shape": (1, 3, 224, 224)},
            "input1": {"dtype": np.float32, "shape": (1, 1, 224, 224)},
        }

        # Convert with static batch
        self.converted_model_path = DeciPlatformClient.convert_pytorch_to_onnx(
            local_loaded_model=model,
            inputs_metadata=inputs_metadata,
            export_path="/tmp/multi_input_pytorch_cv_test_model.onnx",
        )
        self._assert_onnx_checkpoint(self.converted_model_path)

        # Convert with dynamic batch
        self.converted_model_path = DeciPlatformClient.convert_pytorch_to_onnx(
            local_loaded_model=model,
            inputs_metadata=inputs_metadata,
            dynamic_axes={
                "input0": {0: "batch_size"},
                "input1": {0: "batch_size"},
                "37": {0: "batch_size"},
                "17": {0: "batch_size"},
            },
            export_path="/tmp/multi_input_pytorch_cv_test_model.onnx",
        )
        self._assert_onnx_checkpoint(self.converted_model_path)

    def _assert_onnx_checkpoint(self, onnx_path):
        self.assertIsNotNone(onnx_path)
        onnx.load(onnx_path)
        onnx.checker.check_model(onnx_path, full_check=True)
