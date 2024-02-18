"""Google bucket implementation of the abstract data source interface."""
from __future__ import annotations

import json
from typing import Dict, List

from flask import Response
import requests
from werkzeug.exceptions import ServiceUnavailable

from gateway_4d_viewer.interfaces import DataSourceInterface
from gateway_4d_viewer.interfaces import Tile


class XCubeDataSource(DataSourceInterface):
    """Implements the data source interface accessing data from an xcube server."""

    def __init__(self: XCubeDataSource, server_url: str) -> None:
        """
        Instantiate object.

        Parameters
        ----------
        server_url : str
            URL of the Xcube server to query for data.
        """
        super().__init__()
        self.server_url = server_url

    def _get_data_from_server(self: XCubeDataSource, endpoint_string: str, request_data: Dict = None,
                              as_flask_response: bool = False) -> str | Response:
        try:
            request_url = f"{self.server_url}/{endpoint_string}"
            request_data = json.dumps(request_data) if request_data is not None else None
            response = requests.get(url=request_url, data=request_data, timeout=(5, 15))
            assert response.ok
        except (requests.exceptions.ConnectionError, AssertionError, requests.exceptions.ReadTimeout) as exc:
            print(f"Failed to reach xcube server at {self.server_url}")
            raise ServiceUnavailable(exc)

        if as_flask_response:
            # translate from requests.Response to flask.Response - flask will throw an error otherwise
            return Response(response=response.content,
                            status=response.status_code,
                            headers=dict(response.headers))
        else:
            return response.text

    def _data_sets(self: XCubeDataSource) -> List[dict]:
        """
        Return a list of datasets.

        Returns
        -------
        List[dict]
            A list of datasets with basic meta data. See the abstract implementation for schema reference.
        """
        # protection for production - if xcube server unreachable, just exclude it from sources passed to the 4D client
        # without raising an error
        try:
            # xcube server doesn't allow endpoints to return a list, so we wrap it in a dict and unwrap here
            return json.loads(self._get_data_from_server(endpoint_string="variables"))["variables"]
        except ServiceUnavailable:
            return []

    def _data_set_configuration(self: XCubeDataSource, data_set_id: str) -> dict:
        """
        Return data set meta data for a specific data set id.

        Parameters
        ----------
        data_set_id : str
            Unique identifier of the data set

        Returns
        -------
        dict
            A meta data dictionary.
        """
        return json.loads(self._get_data_from_server(endpoint_string=f"{data_set_id}/configuration"))

    def data_set_tiles(self: XCubeDataSource, tile_definition: Tile) -> Response:
        """
        Get single tile of data.

        For now, if z is not set, it will be set to a string "None" in the server endpoint path. This is temporary;
        need to figure out if it is possible to assign multiple routes to a route handler within xcube. If not, we might
        end up with two separate endpoints instead - a 2d and a 3d one. TODO: update once sorted.

        Parameters
        ----------
        tile_definition : Tile
            Specification of the tile to retrieve.

        Returns
        -------
        Response
            Http response with object.
        """
        tile_path_template = \
            "{data_set_id}/tiles/{resolution}/{x}_{y}_{z}_{date}_{extension}"

        tile_path = tile_path_template.format(data_set_id=tile_definition.data_set_id,
                                              resolution=tile_definition.resolution,
                                              x=tile_definition.x,
                                              y=tile_definition.y,
                                              z=tile_definition.z if tile_definition.z is not None else "None",
                                              date=tile_definition.time,
                                              extension=tile_definition.extension
                                              )

        return self._get_data_from_server(endpoint_string=tile_path, as_flask_response=True)

    def __eq__(self: XCubeDataSource, other_object: object) -> bool:
        """
        Check object for equality.

        We consider two XCubeDataSource objects equal if they point to the same server url.

        Parameters
        ----------
        other_object : object
            The object to compare against this one.

        Returns
        -------
        bool
            Whether the two are equal.
        """
        if isinstance(other_object, XCubeDataSource):
            return other_object.server_url == self.server_url
        return False
