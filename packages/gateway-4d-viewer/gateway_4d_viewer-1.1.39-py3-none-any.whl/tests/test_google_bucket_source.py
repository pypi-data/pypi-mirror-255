"""Tests for google bucket source."""
import json
from unittest.mock import ANY
from unittest.mock import MagicMock
from unittest.mock import patch

from google.api_core import exceptions
from google.auth.exceptions import DefaultCredentialsError
from google.cloud.storage import Blob
from google.cloud.storage import Bucket
from google.cloud.storage import Client
import pytest
from werkzeug.exceptions import NotFound

from gateway_4d_viewer import app
from gateway_4d_viewer.google_bucket_source import _get_data_set_name_from_path
from gateway_4d_viewer.google_bucket_source import GoogleBucketDataSource
from gateway_4d_viewer.interfaces import Tile


@pytest.fixture()
def mock_client() -> MagicMock(Client):
    """
    Handle all client mocking in one place for the various use cases in tests.

    Returns
    -------
    MagicMock(Client)
        Mocked google Client object
    """
    blob_1 = MagicMock(spec=Blob)
    blob_1.name = "a/a.png"
    blob_1.public_url = "https://a/a.png"
    blob_2 = MagicMock(spec=Blob)
    blob_2.name = "a/b.png"
    blob_2.public_url = "https://a/b.png"
    blob_3 = MagicMock(spec=Blob)
    blob_3.name = "a/c/"
    blob_3.public_url = "shouldn't appear"

    # Blobs can be iterated for each blob or queried for prefixes
    mock_blobs = MagicMock()
    mock_blobs.__iter__.return_value = [blob_1, blob_2, blob_3]
    mock_blobs.prefixes = ['a/', 'b/']

    mock_client = MagicMock(spec=Client)
    mock_client.list_blobs.return_value = mock_blobs

    # Mock bucket calls
    mock_bucket = MagicMock(spec=Bucket)
    blob_1.download_to_filename.return_value = None
    blob_1.download_as_string.return_value = '{"A": "test"}'
    mock_bucket.blob.return_value = blob_1
    mock_client.get_bucket.return_value = mock_bucket

    return mock_client


@pytest.fixture()
def test_google_bucket_data_source(mock_client: MagicMock(Client)) -> GoogleBucketDataSource:
    return GoogleBucketDataSource("test_bucket", client=mock_client)


def test_create_instance_handles_credentials_error():
    with patch.object(Client, "__init__") as mock_client, \
            patch.object(Client, "create_anonymous_client") as mock_anonymous_client:
        mock_client.side_effect = DefaultCredentialsError('mocked error')
        GoogleBucketDataSource("test")
        # Expect attempt to create anonymous client instead
        mock_anonymous_client.assert_called_once()


def test_get_data_set_name_from_path():
    assert _get_data_set_name_from_path("/a/blah") == "blah"
    assert _get_data_set_name_from_path("/a/blah/") is None


def test_get_json_from_bucket(test_google_bucket_data_source: GoogleBucketDataSource):
    result = test_google_bucket_data_source._get_json_from_bucket("test/path")
    assert result == {'A': 'test'}


def test_send_file_from_bucket(test_google_bucket_data_source: GoogleBucketDataSource):
    with app.test_request_context() as _, \
            patch('gateway_4d_viewer.google_bucket_source.send_file') as mock_send_file:
        test_google_bucket_data_source.send_file_from_bucket("tmp.txt")
        mock_send_file.assert_called_once_with(ANY, download_name='tmp.txt')


def test_send_file_from_bucket_raises_not_found(test_google_bucket_data_source: GoogleBucketDataSource):

    # Reuse the existing mocked methods in the mock_client object but change the behaviour of download_to_filename
    mock_client = test_google_bucket_data_source.client
    mock_client.get_bucket().blob().download_to_filename.side_effect = exceptions.NotFound("")

    with app.test_request_context(), pytest.raises(NotFound):
        test_google_bucket_data_source.send_file_from_bucket("")


def test_data_set_configuration(test_google_bucket_data_source: GoogleBucketDataSource):
    with patch.object(GoogleBucketDataSource, '_get_json_from_bucket') as mock_get_json_from_bucket:
        test_google_bucket_data_source._data_set_configuration('data-set')
        mock_get_json_from_bucket.assert_called_once_with("api-v1/data-sets/data-set/configuration.json")


def test_data_sets(test_google_bucket_data_source: GoogleBucketDataSource):
    with patch.object(GoogleBucketDataSource, '_list_directories') as mock_paths, \
            patch.object(GoogleBucketDataSource, '_get_json_from_bucket') as mock_json:

        mock_paths.return_value = ['/a/b/c/']
        mock_json.return_value = {'data-set': {
            'ui-path': 'path',
            'ui-type': 'type',
            'last-modified': '1'
        }}

        data_sets = test_google_bucket_data_source._data_sets()

        assert data_sets[0]['id'] == 'c'
        assert data_sets[0]['last-modified'] == '1'
        assert data_sets[0]['ui-path'] == 'path'
        assert data_sets[0]['ui-type'] == 'type'


def test_data_sets_not_found_error(test_google_bucket_data_source: GoogleBucketDataSource):
    # Ensure google not found error is reraised as werkzeug NotFound
    with patch.object(GoogleBucketDataSource, '_list_directories') as mock_paths, \
            patch.object(GoogleBucketDataSource, '_get_json_from_bucket') as mock_json:

        mock_paths.return_value = ['/a/b/c/']
        mock_json.side_effect = exceptions.NotFound("")

        with pytest.raises(NotFound):
            test_google_bucket_data_source._data_sets()


def test_file_urls_in_directory(test_google_bucket_data_source: GoogleBucketDataSource):
    with app.test_request_context():
        results = test_google_bucket_data_source.file_urls_in_directory("A")     # Inputs here aren't used

    assert json.loads(results.get_data()) == [
        {'name': 'a'},
        {'name': 'b'}]


def test_list_blobs_with_prefix(test_google_bucket_data_source: GoogleBucketDataSource):
    results = test_google_bucket_data_source._list_directories("A")   # Inputs aren't used
    assert results == ['a/', 'b/']


def test_data_set_tiles(test_google_bucket_data_source: GoogleBucketDataSource):
    with patch.object(GoogleBucketDataSource, 'send_file_from_bucket') as mock_send_file:
        test_google_bucket_data_source.data_set_tiles(Tile("a", "r", "t", "x", "y", "z", "png"))
        mock_send_file.assert_called_once_with("api-v1/data-sets/a/tiles/r/x_y_z_t.png")
