"""Unit tests interaces."""
from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from schema import SchemaError

from gateway_4d_viewer.interfaces import DataSourceInterface
from gateway_4d_viewer.interfaces import Tile


class DummyDataSourceInterface(DataSourceInterface):
    """Dummy datasource to implement abstract class."""

    def _data_set_configuration(self: DummyDataSourceInterface, _: str) -> dict:
        return None

    def _data_sets(self: DummyDataSourceInterface) -> dict:
        return None

    # This abstract method isn't validated so we leave a stub here
    # The doc string D102 requirement is suppressed as unnecessary here.
    def data_set_tiles(self: DummyDataSourceInterface, _tile_definition: Tile) -> str:   # noqa:D102 - dummy method.
        return None

    def __eq__(self: DummyDataSourceInterface, _other_file: object) -> bool:   # noqa:D105 - dummy method.
        return True


def _fetch_json(file_path: str) -> list | dict:
    with open(file_path) as json_file:
        contents = json.load(json_file)
    return contents


def test_data_set_configuration():
    with patch.object(DummyDataSourceInterface, "_data_set_configuration") as mock_data_set_configuration:

        example_configuration = _fetch_json('tests/json_response_examples/configuration.json')
        mock_data_set_configuration.return_value = example_configuration

        interface = DummyDataSourceInterface()
        interface.data_set_configuration("test")


def test_data_set_configuration_2d():
    with patch.object(DummyDataSourceInterface, "_data_set_configuration") as mock_data_set_configuration:

        example_configuration = _fetch_json('tests/json_response_examples/configuration_2d.json')
        mock_data_set_configuration.return_value = example_configuration
        DummyDataSourceInterface().data_set_configuration("test")


def test_data_set_configuration_fail():
    interface = DummyDataSourceInterface()
    with pytest.raises(SchemaError):
        interface.data_set_configuration("test")


def test_data_sets():
    with patch.object(DummyDataSourceInterface, "_data_sets") as mock_data_set_configuration:

        example_data_sets = _fetch_json('tests/json_response_examples/data_sets.json')
        mock_data_set_configuration.return_value = example_data_sets

        DummyDataSourceInterface().data_sets()


def test_data_sets_fail():
    interface = DummyDataSourceInterface()
    with pytest.raises(SchemaError):
        interface.data_sets()
