import factory
from deci_platform_client.models import (
    AccuracyMetric,
    AccuracyMetricKey,
    AccuracyMetricType,
)

from tests.helpers import get_random_enum_value


class AccuracyMetricFactory(factory.Factory):
    class Meta:
        model = AccuracyMetric

    key = factory.LazyFunction(lambda: get_random_enum_value(AccuracyMetricKey))
    type = factory.LazyFunction(lambda: get_random_enum_value(AccuracyMetricType))
    value = factory.Faker("pyfloat", min_value=0.0, max_value=1.0)
    isPrimary = factory.Faker("boolean")
