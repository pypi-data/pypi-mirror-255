"""Tests for xcube server source."""
import json
from unittest.mock import patch

import pytest
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.models import Response
from werkzeug.exceptions import ServiceUnavailable

from gateway_4d_viewer.interfaces import Tile
from gateway_4d_viewer.xcube_server_source import XCubeDataSource


@pytest.fixture()
def example_xcube_data_source() -> XCubeDataSource:
    return XCubeDataSource(server_url="http://please-give-data:8000/4d_viewer")


@pytest.fixture()
def example_data_set_meta_data() -> dict:
    return {
        "id": "local.c2rcc_flags",
        "last_modified": "2023-04-02T15:19:07.575709Z",
        "name": "Local OLCI L2C cube for region SNS C2RCC quality flags",
        "ui-type": "heatmap",
        "ui-path": "/user/local/c2rcc_flags"
    }


@pytest.fixture()
def example_data_set_config():
    return {
        "data-set": {
            "units": "",
            "value-range": {
                "min": 0.0,
                "max": 1.0
            },
            "times": [
                "2017-01-16T10:09:22Z",
                "2017-01-25T09:35:51Z",
                "2017-01-26T10:50:17Z",
                "2017-01-28T09:58:11Z",
                "2017-01-30T10:46:34Z"
            ],
            "ui-path": "/user/local/c2rcc_flags/",
            "ui-type": "heatmap",
            "last-modified": "2023-04-02T15:27:31.274803Z"
        },
        "tile-grid": {
            "extent": {
                "x": {
                    "min": 0,
                    "max": 5
                },
                "y": {
                    "min": 50,
                    "max": 52.5
                }
            },
            "origin": {
                "x": 0,
                "y": 52.5
            },
            "tile-size": {
                "x": 250,
                "y": 250
            },
            "lowest-resolution-tile-extent": {
                "x": 2.5,
                "y": 2.5
            },
            "tile-orientation": {
                "x": "positive",
                "y": "negative"
            },
            "number-of-resolutions": 3,
            "projection": "EPSG:4567",
        }
    }


def test__get_response_from_server(example_xcube_data_source: XCubeDataSource):
    with patch("gateway_4d_viewer.xcube_server_source.requests.get") as mock_get:

        mock_response = Response()
        mock_response.status_code = 200
        mock_response._content = b'All good'

        mock_get.return_value = mock_response
        response = example_xcube_data_source._get_data_from_server("dummy_endpoint", request_data={"give": "data"})
        assert response == "All good"
        mock_get.assert_called_once_with(url="http://please-give-data:8000/4d_viewer/dummy_endpoint",
                                         data=json.dumps({"give": "data"}), timeout=(5, 15))


def test__get_response_from_server_connection_error(example_xcube_data_source: XCubeDataSource):
    with patch("gateway_4d_viewer.xcube_server_source.requests.get") as mock_get:

        mock_response = Response()
        mock_response.status_code = 200
        mock_response._content = b'All good'

        mock_get.side_effect = RequestsConnectionError("Server unavailable")
        with pytest.raises(ServiceUnavailable, match="Server unavailable"):
            example_xcube_data_source._get_data_from_server("dummy_endpoint", request_data={"give": "data"})


def test_data_set_configuration(example_xcube_data_source: XCubeDataSource, example_data_set_config: dict):
    with patch.object(XCubeDataSource, '_get_data_from_server') as mock_get_data_from_server:

        mock_get_data_from_server.return_value = json.dumps(example_data_set_config)
        example_xcube_data_source.data_set_configuration(data_set_id="dummy_data_set_id")
        mock_get_data_from_server.assert_called_once_with(endpoint_string="dummy_data_set_id/configuration")


def test_data_sets(example_xcube_data_source: XCubeDataSource,
                   example_data_set_meta_data: dict):
    with patch.object(XCubeDataSource, '_get_data_from_server') as mock_get_data_from_server:

        mock_get_data_from_server.return_value = json.dumps({"variables": [example_data_set_meta_data]})

        example_xcube_data_source._data_sets()

        mock_get_data_from_server.assert_called_once_with(endpoint_string="variables")


def test_data_set_tiles(example_xcube_data_source: XCubeDataSource):
    with patch.object(XCubeDataSource, '_get_data_from_server') as mock_get_data_from_server:
        example_xcube_data_source.data_set_tiles(Tile("mock_dataset", "mock_resolution", "t", "x", "y", "z", "png"))
        mock_get_data_from_server.assert_called_once_with(
            endpoint_string="mock_dataset/tiles/mock_resolution/x_y_z_t_png",
            as_flask_response=True)
