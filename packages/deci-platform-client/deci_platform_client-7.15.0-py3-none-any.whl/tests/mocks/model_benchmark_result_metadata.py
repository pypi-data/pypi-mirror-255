import random

import factory
from deci_platform_client.models import ModelBenchmarkResultMetadata


class ModelBenchmarkResultMetadataFactory(factory.Factory):
    class Meta:
        model = ModelBenchmarkResultMetadata

    batchInfTime = factory.LazyFunction(lambda: 10 * random.random())
