"""The module defines abstract interfaces and objects used throughout the middle tier."""
from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import List

from flask import Response
from schema import Schema

from gateway_4d_viewer.api_schema import CONFIGURATION_SCHEMA
from gateway_4d_viewer.api_schema import DATA_SETS_SCHEMA


@dataclass
class Tile:
    """Encapsulates tile data specification (and simplifies function signatures)."""

    data_set_id: str
    resolution: str
    time: str
    x: str
    y: str
    z: str
    extension: str


class DataSourceInterface(ABC):
    """Abstract class definition for data source implementations.

    Note - obscure implementation specific exceptions should be caught and reraised with standard exception objects
    from werkzeug.exceptions.
    e.g. the following for missing resources:
    from werkzeug.exceptions import NotFound
    """

    def data_sets(self: DataSourceInterface) -> List[dict]:
        """
        Query available data sets for a given child data source implementation.

        Results are validated by the schema before being returned.

        Returns
        -------
        List[dict]
            Data sets from child implementation with added schema validation.
        """
        data_sets = self._data_sets()
        Schema(DATA_SETS_SCHEMA).validate(data_sets)
        return data_sets

    @ abstractmethod
    def _data_sets(self: DataSourceInterface) -> List[dict]:
        """Return data sets information. Child must implement this! See data_sets() for more detail."""
        raise NotImplementedError  # pragma: no cover

    def data_set_configuration(self: DataSourceInterface, data_set_id: str) -> dict:
        """
        Return data set configuration info.

        Results of child implementation are validated before being returned.

        Parameters
        ----------
        data_set_id : str
            Data set identifier.

        Returns
        -------
        dict
            Data set configuration dictionary.
        """
        configuration = self._data_set_configuration(data_set_id)
        Schema(CONFIGURATION_SCHEMA).validate(configuration)
        return configuration

    @ abstractmethod
    def _data_set_configuration(self: DataSourceInterface, _data_set_id: str) -> dict:
        """Return configuration/meta data for a given dataset. Child must implement this.

        See data_set_configuration for more detail.
        """
        raise NotImplementedError  # pragma: no cover

    @ abstractmethod
    def data_set_tiles(self: DataSourceInterface, _tile_definition: Tile) -> Response:
        """Fetch individual tiles."""
        raise NotImplementedError  # pragma: no cover

    @ abstractmethod
    def __eq__(self: DataSourceInterface, _other_object: object) -> bool:
        """
        Check object for equality.

        Two source objects should be equal if they point to the same source, e.g. the same google bucket or xcube
        server url.

        Parameters
        ----------
        _other_object : object
            The object to compare against this one.

        Returns
        -------
        bool
            Whether the two are equal
        """
        raise NotImplementedError  # pragma: no cover
