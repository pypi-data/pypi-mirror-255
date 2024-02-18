from unittest import TestCase

from deci_platform_client.client.helpers import get_accuracy_metric_key
from deci_platform_client.models import AccuracyMetricKey, DeepLearningTask


class TestGetAccuracyMetricKey(TestCase):
    def test_classification(self) -> None:
        self.assertEqual(
            get_accuracy_metric_key(DeepLearningTask.CLASSIFICATION),
            AccuracyMetricKey.M_AP,
        )

    def test_semantic_segmentation(self) -> None:
        self.assertEqual(
            get_accuracy_metric_key(DeepLearningTask.SEMANTIC_SEGMENTATION),
            AccuracyMetricKey.M_IO_U,
        )

    def test_nlp(self) -> None:
        self.assertEqual(get_accuracy_metric_key(DeepLearningTask.NLP), AccuracyMetricKey.TOP1)

    def test_random(self) -> None:
        self.assertEqual(get_accuracy_metric_key("not a real task"), AccuracyMetricKey.TOP1)
