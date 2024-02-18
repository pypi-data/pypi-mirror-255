from typing import TYPE_CHECKING

from tqdm import tqdm

from deci_platform_client.models import (
    KPI,
    AccuracyMetric,
    AccuracyMetricKey,
    AccuracyMetricType,
    DeepLearningTask,
    FrameworkType,
    GruRequestForm,
    HardwareType,
    Metric,
    ModelMetadataIn,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any, Optional, Union
    from uuid import UUID

    # This package can be supposedly used with Python3.7, Protocol was added in 3.8, shrug:
    from typing_extensions import Protocol  # noqa: UP035

    from deci_platform_client.models import DatasetName, QuantizationLevel

    class MetaEnum(Protocol):
        enum_value_to_name: dict[str, str]

    class OpenApiPseudoEnum(Protocol):
        MetaOapg: type[MetaEnum]

    Hardware = Union[HardwareType, str]


class TqdmUpTo(tqdm):
    DOWNLOAD_PARAMS = {
        "unit": "B",
        "unit_scale": True,
        "unit_divisor": 1024,
        "miniters": 1,
        "bar_format": "{l_bar}{bar:20}{r_bar}",
    }

    """Provides `update_to(n)` which uses `tqdm.update(delta_n)`."""

    def update_to(self, b: int = 1, bsize: int = 1, tsize: "Optional[int]" = None):
        """
        b  : int, optional
            Number of blocks transferred so far [default: 1].
        bsize  : int, optional
            Size of each block (in tqdm units) [default: 1].
        tsize  : int, optional
            Total size (in tqdm units). If [default: None] remains unchanged.
        """
        if tsize is not None:
            self.total = tsize
        return self.update(b * bsize - self.n)  # also sets self.n = b * bsize


_DL_TASK_TO_LABEL = {
    DeepLearningTask.CLASSIFICATION: AccuracyMetricKey.M_AP,
    DeepLearningTask.SEMANTIC_SEGMENTATION: AccuracyMetricKey.M_IO_U,
}

DEFAULT_HARDWARE: "Hardware" = HardwareType.T4


def default_hardware_list() -> "list[Hardware]":
    return [DEFAULT_HARDWARE]


def get_accuracy_metric_key(dl_task: DeepLearningTask) -> AccuracyMetricKey:
    return _DL_TASK_TO_LABEL.get(dl_task, AccuracyMetricKey.TOP1)  # type: ignore[arg-type]


def build_model_metadata(
    *,
    framework: "FrameworkType" = FrameworkType.PYTORCH,
    name: str,
    dl_task: DeepLearningTask,
    input_dimensions: "Union[Sequence[int], Sequence[Sequence[int]]]",
    primary_hardware: "Optional[Hardware]" = None,
    channel_first: bool = True,
    accuracy: "Optional[float]" = None,
    accuracy_key: "Optional[AccuracyMetricKey]" = None,
    description: "Optional[str]" = None,
    dataset_name: "Optional[DatasetName]" = None,
    target_metric: "Optional[Metric]" = None,
    target_metric_value: "Optional[float]" = None,
    model_size: "Optional[float]" = None,
    memory_footprint: "Optional[float]" = None,
) -> "ModelMetadataIn":
    accuracy_metrics = []
    if accuracy is not None:
        accuracy_metrics.append(
            AccuracyMetric(
                key=accuracy_key or get_accuracy_metric_key(dl_task),
                isPrimary=True,
                value=accuracy,
                type=AccuracyMetricType.PERCENTAGE,  # type: ignore[arg-type]
            )
        )
    kpis = []
    if target_metric is not None and target_metric_value is not None:
        kpis.append(KPI(metric=target_metric, value=target_metric_value))
    if model_size is not None:
        kpis.append(KPI(metric=Metric.MODEL_SIZE, value=model_size))  # type: ignore[arg-type]
    if memory_footprint is not None:
        kpis.append(KPI(metric=Metric.MEMORY_FOOTPRINT, value=memory_footprint))  # type: ignore[arg-type]
    model_metadata = {}
    if description is not None:
        model_metadata["description"] = description
    if dataset_name is not None:
        model_metadata["datasetName"] = dataset_name

    return ModelMetadataIn(
        name=name,
        framework=framework,
        dlTask=dl_task,
        inputDimensions=input_dimensions,
        channelFirst=channel_first,
        primaryHardware=primary_hardware or DEFAULT_HARDWARE,
        accuracyMetrics=accuracy_metrics,
        kpis=kpis,
        **model_metadata,
    )


def build_gru_request_form(
    *,
    batch_size: int,
    quantization_level: "QuantizationLevel",
    target_hardware_types: "Optional[list[Hardware]]" = None,
    raw_format: bool,
    target_metric: Metric = Metric.THROUGHPUT,
    name: "Optional[str]" = None,
    conversion_parameters: "Optional[dict[str, Any]]" = None,
    autonac_run_id: "Optional[Union[UUID, str]]" = None,
) -> GruRequestForm:
    additional_parameters: "dict[str, Union[UUID, str, dict[str, Any]]]" = {}
    if conversion_parameters is not None:
        additional_parameters["conversionParameters"] = conversion_parameters
    if name is not None:
        additional_parameters["name"] = name
    if autonac_run_id is not None:
        additional_parameters["autonacRunId"] = autonac_run_id
    return GruRequestForm(
        optimizeAutonac=False,
        optimizeModelSize=False,
        quantizationLevels=[quantization_level],
        targetBatchSizes=[batch_size],
        targetHardwares=target_hardware_types or default_hardware_list(),
        targetMetric=target_metric,
        rawFormat=raw_format,
        **additional_parameters,
    )


def enum_values(openapi_enum: "OpenApiPseudoEnum") -> "list[str]":
    return list(openapi_enum.MetaOapg.enum_value_to_name.keys())
