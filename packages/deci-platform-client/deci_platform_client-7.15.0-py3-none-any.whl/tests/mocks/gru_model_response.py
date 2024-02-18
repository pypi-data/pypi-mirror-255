from uuid import uuid4

import factory
from deci_platform_client.models import APIResponseGruModelResponse, GruModelResponse


class GruModelResponseFactory(factory.Factory):
    class Meta:
        model = GruModelResponse

    optimizedModelIds = factory.LazyFunction(lambda: [str(uuid4())])
    optimizationRequestId = factory.LazyFunction(lambda: str(uuid4()))


class APIResponseGruModelResponseFactory(factory.Factory):
    class Meta:
        model = APIResponseGruModelResponse

    success = True
    data = factory.SubFactory(GruModelResponseFactory)
    message = ""
