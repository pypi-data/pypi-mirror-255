from uuid import uuid4

import factory
from deci_platform_client.models import APIResponseStr


class APIStrResponseFactory(factory.Factory):
    class Meta:
        model = APIResponseStr

    success = True
    data = factory.LazyFunction(lambda: str(uuid4()))
    message = ""
