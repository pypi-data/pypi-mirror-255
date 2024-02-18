"""Unit tests for gateway_4d_viewer.routes_v1.py."""
from http import HTTPStatus
import json
from unittest.mock import Mock
from unittest.mock import patch

from flask.testing import FlaskClient
import pytest
from werkzeug.exceptions import InternalServerError, NotFound

from gateway_4d_viewer import app
from gateway_4d_viewer import routes_v1
from gateway_4d_viewer.google_bucket_source import GoogleBucketDataSource
from gateway_4d_viewer.interfaces import DataSourceInterface
from gateway_4d_viewer.interfaces import Tile
from gateway_4d_viewer.xcube_server_source import XCubeDataSource


@pytest.fixture()
def client() -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def file_urls_in_directory_example():
    return json.dumps([
        {'name': 'a', 'url': 'url_a'},
        {'name': 'b', 'url': 'url_b'}])


@pytest.fixture()
def mock_data_source():
    # Simple mock data source instance to use throughout tests.
    mock_source = Mock(spec=DataSourceInterface)
    mock_source.data_sets.return_value = [{'id': 'test_dataset'}]
    mock_source.data_set_configuration.return_value = {"att": "value"}
    return mock_source


@pytest.fixture()
def mock_data_sources(mock_data_source: Mock):
    # Mocks the DATA_SOURCES dictionary when required.
    with patch.dict('gateway_4d_viewer.routes_v1.DATA_SOURCES', {'source': mock_data_source}, clear=True):
        yield None


@pytest.fixture()
def mock_split_api_id(mock_data_source: Mock):
    # For endpoints that derive data set/sourve from the url, this mocks out values returned from _split_api_id
    with patch('gateway_4d_viewer.routes_v1._split_api_id') as mock_split_api_id:
        data_set = "A"
        mock_split_api_id.return_value = mock_data_source, data_set
        yield None


def test_api_catches_internal_error(client: FlaskClient):
    # use a simple end point to mimic an internal error.
    with patch.object(GoogleBucketDataSource, 'send_file_from_bucket') as mock_send_file:
        mock_send_file.side_effect = InternalServerError("Howdy")
        response = client.get("/api-v1/color-maps/id")
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert "Howdy" in response.text


@pytest.mark.usefixtures("mock_data_sources")
def test_get_data_source(mock_data_source: Mock):

    data_source, data_set = routes_v1._split_api_id(f"source{routes_v1.DATA_SOURCE_DELIMITER}set")
    assert data_source == mock_data_source
    assert data_set == "set"


@pytest.mark.usefixtures("mock_data_sources")
def test_get_data_sets(client: FlaskClient):

    response = client.get("/api-v1/data-sets")
    expected_api_id = f'source{routes_v1.DATA_SOURCE_DELIMITER}test_dataset'
    assert json.loads(response.get_data())[0]['id'] == expected_api_id


@pytest.mark.usefixtures("mock_data_sources")
def test_get_data_sets_catches_notfound(client: FlaskClient, mock_data_source: Mock):
    # Override data_sets side effect for this test only
    mock_data_source.data_sets.side_effect = NotFound("")
    response = client.get("/api-v1/data-sets")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.usefixtures("mock_split_api_id")
def test_get_data_set_configuration(client: FlaskClient, mock_data_source: Mock):

    response = client.get("/api-v1/data-sets/any_api_key/configuration")
    # Check datasource method called
    mock_data_source.data_set_configuration.assert_called_once_with("A")
    # Check response is jsonified
    assert json.loads(response.get_data()) == {"att": "value"}


@pytest.mark.usefixtures("mock_split_api_id")
def test_get_data_set_configuration_catches_notfound(client: FlaskClient, mock_data_source: Mock):
    mock_data_source.data_set_configuration.side_effect = NotFound("")
    response = client.get("/api-v1/data-sets/any_api_key/configuration")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.usefixtures("mock_split_api_id")
def test_return_tile(client: FlaskClient, mock_data_source: Mock):

    client.get("/api-v1/data-sets/any_api_key/tiles/resolution_time_x_y_png")

    # Check the mock data source is called correctly
    mock_data_source.data_set_tiles.assert_called_once_with(
        Tile(data_set_id="A", resolution="resolution", time="time", x="x", y="y", z=None, extension="png"))


@pytest.mark.usefixtures("mock_split_api_id")
def test_return_tile_with_z(client: FlaskClient, mock_data_source: Mock):

    client.get("/api-v1/data-sets/dataset_id/tiles/resolution_time_x_y_z_ewv")

    # Check the mock data source is called correctly
    mock_data_source.data_set_tiles.assert_called_once_with(
        Tile(data_set_id="A", resolution="resolution", time="time", x="x", y="y", z="z", extension="ewv"))


@pytest.mark.usefixtures("mock_split_api_id")
def test_return_tile_catches_notfound(client: FlaskClient, mock_data_source: Mock):

    mock_data_source.data_set_tiles.side_effect = NotFound("")
    response = client.get("/api-v1/data-sets/any_api_key/tiles/resolution_time_x_y_png")
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_color_maps(client: FlaskClient, file_urls_in_directory_example: dict):

    with patch.object(GoogleBucketDataSource, 'file_urls_in_directory') as file_urls_in_directory:
        file_urls_in_directory.return_value = file_urls_in_directory_example
        response = client.get("/api-v1/color-maps")
        response_data = json.loads(response.get_data())
        assert response_data[0]['name'] == 'a'
        assert response_data[1]['url'] == 'url_b'


def test_color_map(client: FlaskClient):
    with patch.object(GoogleBucketDataSource, 'send_file_from_bucket') as mock_send_file:
        client.get("/api-v1/color-maps/id")
        mock_send_file.assert_called_once_with("api-v1/colour-maps/id.png")


def test_color_map_catches_notfound(client: FlaskClient):
    with patch.object(GoogleBucketDataSource, 'send_file_from_bucket') as mock_send_file:
        mock_send_file.side_effect = NotFound("")
        response = client.get("/api-v1/color-maps/id")
        assert response.status_code == HTTPStatus.NOT_FOUND


def test_configurations(client: FlaskClient, file_urls_in_directory_example: dict):

    with patch.object(GoogleBucketDataSource, 'file_urls_in_directory') as file_urls_in_directory:
        file_urls_in_directory.return_value = file_urls_in_directory_example
        response = client.get("/api-v1/configurations")
        response_data = json.loads(response.get_data())
        assert response_data[0]['name'] == 'a'
        assert response_data[1]['url'] == 'url_b'


def test_configuration(client: FlaskClient):
    with patch.object(GoogleBucketDataSource, 'send_file_from_bucket') as mock_send_file:
        client.get("/api-v1/configurations/id")
        mock_send_file.assert_called_once_with("api-v1/configurations/id.json")


def test_configuration_catches_notfound(client: FlaskClient):
    with patch.object(GoogleBucketDataSource, 'send_file_from_bucket') as mock_send_file:
        mock_send_file.side_effect = NotFound()
        response = client.get("/api-v1/configurations/id")
        assert response.status_code == HTTPStatus.NOT_FOUND


def test_register_xcube_data_source(client: FlaskClient, mock_data_source: Mock):
    with patch.dict('gateway_4d_viewer.routes_v1.DATA_SOURCES', {'source': mock_data_source}, clear=True)\
            as mock_data_sources:
        resp = client.post("/register-data-source/mock_xcube_source",
                           data=json.dumps({"data_source_type": "xcube_server_data_source",
                                            "server_url": "http://dummy-url:5000"}))
        assert resp.status_code == 200
        assert resp.text.endswith("mock_xcube_source added.")
        assert "mock_xcube_source" in mock_data_sources
        added_xcube_source = mock_data_sources["mock_xcube_source"]
        assert isinstance(added_xcube_source, XCubeDataSource)
        assert added_xcube_source.server_url == "http://dummy-url:5000"


def test_register_bucket_data_source(client: FlaskClient, mock_data_source: Mock):
    with patch.dict('gateway_4d_viewer.routes_v1.DATA_SOURCES', {'source': mock_data_source}, clear=True)\
            as mock_data_sources:
        resp = client.post("/register-data-source/mock_bucket_source",
                           data=json.dumps({"data_source_type": "google_bucket_data_source",
                                            "bucket_name": "mock_bucket_name"}))
        assert resp.status_code == 200
        assert resp.text.endswith("mock_bucket_source added.")
        assert "mock_bucket_source" in mock_data_sources
        added_bucket_source = mock_data_sources["mock_bucket_source"]
        assert isinstance(added_bucket_source, GoogleBucketDataSource)
        assert added_bucket_source.bucket_name == "mock_bucket_name"


def test_register_invalid_data_source(client: FlaskClient, mock_data_source: Mock):
    with patch.dict('gateway_4d_viewer.routes_v1.DATA_SOURCES', {'source': mock_data_source}, clear=True):
        resp = client.post("/register-data-source/mock_bucket_source",
                           data=json.dumps({"data_source_type": "invalid_source_type",
                                            "bucket_name": "mock_bucket_name"}))
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert "Format invalid" in resp.text


@pytest.mark.usefixtures("mock_data_sources")
def test_register_data_source_error(client: FlaskClient):
    resp = client.post("/register-data-source/source",
                       data=json.dumps({"data_source_type": "google_bucket_data_source",
                                        "bucket_name": "mock_bucket_name"}))
    assert resp.status_code == 400
    assert resp.text.endswith("source already present.")


def test_deregister_data_source(client: FlaskClient, mock_data_source: Mock):
    with patch.dict('gateway_4d_viewer.routes_v1.DATA_SOURCES', {'source': mock_data_source}, clear=True)\
            as mock_data_sources:
        resp = client.delete("/deregister-data-source/source")
        assert resp.status_code == 200
        assert resp.text.endswith("source deleted.")
        assert "source" not in mock_data_sources


@pytest.mark.usefixtures("mock_data_sources")
def test_deregister_data_source_error(client: FlaskClient):
    resp = client.delete("/deregister-data-source/non-existent-source")
    assert resp.status_code == 400
    assert resp.text.endswith("non-existent-source not present, cannot delete.")
