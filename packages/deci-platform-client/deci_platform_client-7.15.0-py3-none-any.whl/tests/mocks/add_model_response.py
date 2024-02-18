from uuid import uuid4

import factory
from deci_platform_client.models import (
    AddModelResponse,
    APIResponseAddModelResponse,
)


class AddModelResponseFactory(factory.Factory):
    class Meta:
        model = AddModelResponse

    modelId = factory.LazyFunction(lambda: str(uuid4()))
    benchmarkRequestId = factory.LazyFunction(lambda: str(uuid4()))


class APIResponseAddModelResponseFactory(factory.Factory):
    class Meta:
        model = APIResponseAddModelResponse

    success = True
    data = factory.SubFactory(AddModelResponseFactory)
    message = ""
