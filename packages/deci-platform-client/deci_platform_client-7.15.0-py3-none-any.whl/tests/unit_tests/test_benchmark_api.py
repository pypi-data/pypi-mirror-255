from unittest.mock import ANY, MagicMock, patch
from uuid import uuid4

from deci_platform_client import DeciPlatformClient
from deci_platform_client.apis.tags.platform_api import PlatformApi
from deci_platform_client.client.exceptions import (
    BenchmarkRequestError,
    BenchmarkResultNotFoundException,
)
from deci_platform_client.models import (
    BodySendModelBenchmarkRequest,
    FrameworkType,
    HardwareType,
    ModelBenchmarkState,
    ModelOptimizationState,
    QuantizationLevel,
)

from tests.helpers import get_api_response_instance, get_random_enum_value
from tests.mocks import (
    APIResponseBaselineModelResponseMetadataFactory,
    APIResponseGruModelResponseFactory,
    BaselineModelResponseMetadataFactory,
    ModelBenchmarkResultMetadataFactory,
)

from .base_test_case import BaseTestCase


@patch.object(DeciPlatformClient, "register_model", return_value=uuid4())
@patch.object(
    PlatformApi,
    "gru_model",
    return_value=get_api_response_instance(APIResponseGruModelResponseFactory.create()),
)
@patch.object(PlatformApi, "send_model_benchmark_request")
class TestRequestBenchmark(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.hardware_type = get_random_enum_value(HardwareType)

    def test_request_benchmark(
        self,
        benchmark_model_mock: MagicMock,
        gru_model_mock: MagicMock,
        register_model_mock: MagicMock,
    ) -> None:
        job_id = self.client.request_benchmark(model_path="/random/path/to/model", hardware_type=self.hardware_type)
        self.assertEqual(gru_model_mock.return_value.body["data"]["optimizedModelIds"][0], job_id)
        register_model_mock.assert_called_once_with(
            model="/random/path/to/model",
            name=ANY,
            primary_batch_size=1,
            architecture="model",
            description="Benchmark request on model: /random/path/to/model",
            framework=FrameworkType.ONNX,
            quantization_level=QuantizationLevel.FP32,
            hardware_types=[self.hardware_type],
        )
        gru_model_mock.assert_called_once_with(
            path_params={"model_id": register_model_mock.return_value},
            body=ANY,
        )
        gru_request_form = gru_model_mock.call_args[1]["body"]
        self.assertSequenceEqual(gru_request_form["targetHardwares"], [self.hardware_type])
        self.assertSequenceEqual(gru_request_form["quantizationLevels"], [QuantizationLevel.FP16])
        self.assertSequenceEqual(gru_request_form["targetBatchSizes"], [1])
        benchmark_model_mock.assert_not_called()

    def test_request_benchmark_fail_to_add_model(
        self,
        benchmark_model_mock: MagicMock,
        gru_model_mock: MagicMock,
        register_model_mock: MagicMock,
    ) -> None:
        register_model_mock.side_effect = Exception()
        with self.assertRaises(BenchmarkRequestError):
            self.client.request_benchmark(model_path="/random/path/to/model", hardware_type=self.hardware_type)
        register_model_mock.assert_called_once_with(
            model="/random/path/to/model",
            name=ANY,
            primary_batch_size=1,
            architecture="model",
            description="Benchmark request on model: /random/path/to/model",
            framework=FrameworkType.ONNX,
            quantization_level=QuantizationLevel.FP32,
            hardware_types=[self.hardware_type],
        )
        gru_model_mock.assert_not_called()
        benchmark_model_mock.assert_not_called()

    def test_request_benchmark_fail_to_optimize_model(
        self,
        benchmark_model_mock: MagicMock,
        gru_model_mock: MagicMock,
        register_model_mock: MagicMock,
    ) -> None:
        gru_model_mock.side_effect = Exception()
        with self.assertRaises(BenchmarkRequestError):
            self.client.request_benchmark(model_path="/random/path/to/model", hardware_type=self.hardware_type)
        register_model_mock.assert_called_once_with(
            model="/random/path/to/model",
            name=ANY,
            primary_batch_size=1,
            architecture="model",
            description="Benchmark request on model: /random/path/to/model",
            framework=FrameworkType.ONNX,
            quantization_level=QuantizationLevel.FP32,
            hardware_types=[self.hardware_type],
        )
        gru_model_mock.assert_called_once_with(
            path_params={"model_id": register_model_mock.return_value},
            body=ANY,
        )
        benchmark_model_mock.assert_not_called()

    def test_request_benchmark_without_conversion(
        self,
        benchmark_model_mock: MagicMock,
        gru_model_mock: MagicMock,
        register_model_mock: MagicMock,
    ) -> None:
        job_id = self.client.request_benchmark(
            model_path="/random/path/to/model",
            hardware_type=self.hardware_type,
            should_convert=False,
            source_framework=FrameworkType.OPENVINO,
        )
        self.assertEqual(register_model_mock.return_value, job_id)
        register_model_mock.assert_called_once_with(
            model="/random/path/to/model",
            name=ANY,
            primary_batch_size=1,
            architecture="model",
            description="Benchmark request on model: /random/path/to/model",
            framework=FrameworkType.OPENVINO,
            quantization_level=QuantizationLevel.FP16,
            hardware_types=[self.hardware_type],
        )
        gru_model_mock.assert_not_called()
        benchmark_model_mock.assert_called_once_with(
            path_params={"model_id": job_id},
            body=BodySendModelBenchmarkRequest(
                batch_sizes=[1],
                hardwares=[self.hardware_type],
            ),
        )


@patch.object(
    PlatformApi,
    "get_model_by_id",
    return_value=get_api_response_instance(APIResponseBaselineModelResponseMetadataFactory.create()),
)
class TestGetBenchmarkResult(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.job_id = str(uuid4())

    def test_get_benchmark_result(self, get_model_by_id_mock: MagicMock) -> None:
        model_metadata = get_model_by_id_mock.return_value.body["data"]
        generated_result = ModelBenchmarkResultMetadataFactory.create(batchSize=model_metadata["primaryBatchSize"])
        baseline_model_metadata = BaselineModelResponseMetadataFactory.create(
            **{
                **model_metadata,
                "benchmark": {model_metadata["primaryHardware"]["name"]: [generated_result]},
            }
        )
        get_model_by_id_mock.return_value = get_api_response_instance(
            APIResponseBaselineModelResponseMetadataFactory.create(data=baseline_model_metadata),
        )
        result = self.client.get_benchmark_result(model_id=self.job_id)
        print(result)
        self.assertIsInstance(result["batchInfTime"].as_float_oapg, float)
        self.assertNotIn("error", result)
        self.assertEqual(result["batchInfTime"], generated_result["batchInfTime"])
        get_model_by_id_mock.assert_called_once_with(path_params={"model_id": self.job_id})

    def test_get_benchmark_result_model_not_found(self, get_model_by_id_mock: MagicMock) -> None:
        get_model_by_id_mock.return_value = get_api_response_instance(
            APIResponseBaselineModelResponseMetadataFactory.create(success=False)
        )
        result = self.client.get_benchmark_result(model_id=self.job_id)
        self.assertIsNotNone(result["error"])
        self.assertNotIn("batchInfTime", result)
        get_model_by_id_mock.assert_called_once_with(path_params={"model_id": self.job_id})

    def test_get_benchmark_result_optimization_failed(self, get_model_by_id_mock: MagicMock) -> None:
        get_model_by_id_mock.return_value = get_api_response_instance(
            APIResponseBaselineModelResponseMetadataFactory.create(
                data=BaselineModelResponseMetadataFactory.create(
                    optimizationState=ModelOptimizationState.FAILED,
                    baselineModelId=uuid4(),
                )
            )
        )
        result = self.client.get_benchmark_result(model_id=self.job_id)
        self.assertIsNotNone(result["error"])
        self.assertNotIn("batchInfTime", result)
        get_model_by_id_mock.assert_called_once_with(path_params={"model_id": self.job_id})

    def test_get_benchmark_result_benchmark_failed(self, get_model_by_id_mock: MagicMock) -> None:
        get_model_by_id_mock.return_value = get_api_response_instance(
            APIResponseBaselineModelResponseMetadataFactory.create(
                data=BaselineModelResponseMetadataFactory.create(benchmarkState=ModelBenchmarkState.FAILED)
            )
        )
        result = self.client.get_benchmark_result(model_id=self.job_id)
        self.assertIsNotNone(result["error"])
        self.assertNotIn("batchInfTime", result)
        get_model_by_id_mock.assert_called_once_with(path_params={"model_id": self.job_id})

    def test_get_benchmark_result_no_results_for_primary_hardware(self, get_model_by_id_mock: MagicMock) -> None:
        get_model_by_id_mock.return_value = get_api_response_instance(
            APIResponseBaselineModelResponseMetadataFactory.create(
                data=BaselineModelResponseMetadataFactory.create(
                    benchmarkState=ModelBenchmarkState.SUCCEEDED_FULLY,
                )
            )
        )
        with self.assertRaises(BenchmarkResultNotFoundException):
            self.client.get_benchmark_result(model_id=self.job_id)
        get_model_by_id_mock.assert_called_once_with(path_params={"model_id": self.job_id})


@patch.object(
    DeciPlatformClient, "get_benchmark_result", return_value=ModelBenchmarkResultMetadataFactory.create(batch_size=1)
)
class TestWaitForBenchmarkResult(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.job_id = str(uuid4())

    def test_wait_for_benchmark_result(self, get_benchmark_result_mock: MagicMock) -> None:
        result = self.client.wait_for_benchmark_result(model_id=self.job_id)
        self.assertIsInstance(result["batchInfTime"].as_float_oapg, float)
        self.assertEqual(result["batchInfTime"], get_benchmark_result_mock.return_value["batchInfTime"])
        get_benchmark_result_mock.assert_called_once_with(model_id=self.job_id)

    def test_wait_for_benchmark_result_timeout_exceeded(self, get_benchmark_result_mock: MagicMock) -> None:
        get_benchmark_result_mock.side_effect = BenchmarkResultNotFoundException(job_id=self.job_id)
        with self.assertRaises(BenchmarkResultNotFoundException):
            self.client.wait_for_benchmark_result(model_id=self.job_id, timeout=5)
        get_benchmark_result_mock.assert_called_with(model_id=self.job_id)
