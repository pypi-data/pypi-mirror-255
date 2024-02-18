from random import choice, randint, sample
from uuid import uuid4

from deci_platform_client.models import (
    APIResponseBaselineModelResponseMetadata,
    BaselineModelResponseMetadata,
    DeepLearningTask,
    DeepLearningTaskLabel,
    FrameworkType,
    HardwareEnvironment,
    HardwareGroup,
    HardwareOut,
    HardwareType,
    HardwareVendor,
    InferenceHardware,
    InferyVersion,
    ModelMetadata,
)
from factory import Factory, Faker, LazyFunction, SubFactory

from tests.helpers import get_enum_values, lazy_enum


class HardwareOutFactory(Factory):
    class Meta:
        model = HardwareOut

    name = lazy_enum(HardwareType)
    family = lazy_enum(InferenceHardware)
    machineModel = Faker("name")
    environment = lazy_enum(HardwareEnvironment)
    vendor = lazy_enum(HardwareVendor)
    jobLabel = Faker("name")
    taint = Faker("name")
    label = Faker("name")
    group = lazy_enum(HardwareGroup)
    inferyVersion = lazy_enum(InferyVersion)
    defaultBatchSizeList = LazyFunction(lambda: sample([1, 2, 4, 8, 16, 32], 3))
    deprecated = False
    machine = Faker("name")


class ModelMetadataFactory(Factory):
    class Meta:
        model = ModelMetadata

    name = LazyFunction(lambda: str(uuid4()))
    framework = LazyFunction(lambda: choice([v for v in get_enum_values(FrameworkType) if v != "pytorch"]))
    dlTask = lazy_enum(DeepLearningTask)
    primaryHardware = lazy_enum(HardwareType)
    inputDimensions = LazyFunction(lambda: [[randint(1, 100) for _ in range(3)]])
    primaryBatchSize = Faker("pyint", min_value=1, max_value=64)


class BaselineModelResponseMetadataFactory(Factory):
    class Meta:
        model = BaselineModelResponseMetadata

    name = Faker("name")
    benchmark = LazyFunction(dict)
    framework = LazyFunction(lambda: choice([v for v in get_enum_values(FrameworkType) if v != "pytorch"]))
    dlTask = lazy_enum(DeepLearningTask)
    dlTaskLabel = lazy_enum(DeepLearningTaskLabel)
    primaryHardware = SubFactory(HardwareOutFactory)
    inputDimensions = LazyFunction(lambda: [randint(1, 100) for _ in range(3)])
    primaryBatchSize = Faker("pyint", min_value=1, max_value=64)


class APIResponseBaselineModelResponseMetadataFactory(Factory):
    class Meta:
        model = APIResponseBaselineModelResponseMetadata

    success = True
    data = SubFactory(BaselineModelResponseMetadataFactory)
    message = ""
