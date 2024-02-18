"""Unit tests for gateway_4d_viewer.helpers.datasets.py."""
from unittest.mock import patch

from gateway_4d_viewer import dataset_helpers
from gateway_4d_viewer.google_bucket_source import GoogleBucketDataSource


def test_get_datasets():
    with patch.object(GoogleBucketDataSource, '_list_directories') as mock_list_blobs_with_prefix:
        mock_list_blobs_with_prefix.return_value = ['gateway-4d-viewer/datasets/A/', 'gateway-4d-viewer/datasets/B/']
        result = dataset_helpers.get_datasets(None, "not_used", 'gateway-4d-viewer/datasets/')

        assert result == '{"datasets": [{"id": "A", "title": "A"}, {"id": "B", "title": "B"}]}'
