"""Google bucket implementation of the abstract data source interface."""
from __future__ import annotations

import json
import logging
from pathlib import Path
import tempfile
from typing import List, Optional

from flask import jsonify
from flask import Response
from flask import send_file
from google.api_core.exceptions import NotFound as GoogleNotFound
from google.auth.exceptions import DefaultCredentialsError
from google.cloud.storage import Client
from werkzeug.exceptions import NotFound

from gateway_4d_viewer.interfaces import DataSourceInterface
from gateway_4d_viewer.interfaces import Tile

logger = logging.getLogger(__name__)


def _get_data_set_name_from_path(name: str) -> str:
    # Case ending in slash is parent directory
    if name[-1] == '/':
        return None
    return Path(name).stem


class GoogleBucketDataSource(DataSourceInterface):
    """Implements the data source interface accessing data from a propietary google bucket."""

    data_set_root_path = "api-v1/data-sets/"
    configuration_template = data_set_root_path + "{data_set_id}/configuration.json"

    def __init__(self: GoogleBucketDataSource, bucket_name: str, client: Optional[Client] = None) -> None:
        """
        Instantiate object.

        Parameters
        ----------
        bucket_name : str
            Name of the google bucket to retrieve data from.
        client : Client, optional
            Google client class. A default client is created if not given as a parameter. If this is run in an
            environment that has not authenticated via a service account or the likes of gcloud auth login, an
            anonymous client is created for public bucket access only. If valid credentials exist in a session
            they will be used to create the client object.
        """
        super().__init__()
        self.bucket_name = bucket_name
        if client:
            self.client = client
        else:
            try:
                # When a default client can be created, use its credentials. E.g. service accounts running on cloud run,
                # local development/testing.
                logger.info('Creating google bucket client using existing credentials.')
                self.client = Client()
            except (OSError, DefaultCredentialsError) as err:
                # When a default client can't be created, assuming service is being hosted by someone else and google
                # bucket access is via the anonymous client only (i.e. only support public buckets).
                logger.info('Failed to create authenticated google client instance: %s.', str(err))
                logger.info('Creating anonymous google client instance.')
                self.client = Client.create_anonymous_client()

    def _get_json_from_bucket(self: GoogleBucketDataSource, path: str) -> dict | list:
        blob = self.client.get_bucket(self.bucket_name).blob(path)
        return json.loads(blob.download_as_string())

    def send_file_from_bucket(self: GoogleBucketDataSource, file_path: str) -> Response:
        """Fetch any generic blob from a google bucket.

        Parameters
        ----------
        file_path : str
            The "file path" to the google bucket blob.

        Returns
        -------
        Response
            A generic blob object.

        Raises
        ------
        NotFound
            If resource not found.
        """
        bucket = self.client.get_bucket(self.bucket_name)

        blob = bucket.blob(file_path)
        with tempfile.NamedTemporaryFile() as temp:
            try:
                blob.download_to_filename(temp.name)
                return send_file(temp.name, download_name=file_path)
            except GoogleNotFound as e:
                raise NotFound(e)

    def _list_directories(self: GoogleBucketDataSource, root_directory: str) -> List[str]:
        """Return a list of blob directory "paths" that exist under a specific root path.

        Parameters
        ----------
        root_directory : str
            Path prefix - i.e. the first part of the path to search.
            This should not start with a slash. e.g. "api-v1/data-sets/"

        Returns
        -------
        List[str]
            A list of blob paths.
        """
        blobs = self.client.list_blobs(self.bucket_name, prefix=root_directory, delimiter="/")
        # Blobs must be iterated through for the prefixes to be populated.
        # Implementation feature of HTTPIterator
        for _ in blobs:
            pass

        return_list = []
        for root_directory in blobs.prefixes:
            return_list.append(root_directory)

        return return_list

    def file_urls_in_directory(self: GoogleBucketDataSource, path: str) -> Response:
        """List all files in a google bucket "directory" and return as a json response.

        Parameters
        ----------
        path : str
            The directory under which to look for files.

        Returns
        -------
        Response
            A json list with file names (without extensions).
        """
        blobs = self.client.list_blobs(self.bucket_name, prefix=path)

        return_list = []
        for blob in blobs:
            data_set_name = _get_data_set_name_from_path(blob.name)
            # When file_name is None, this indicates a blob that is actually a directory.
            if data_set_name:
                return_list.append(
                    {
                        'name': data_set_name,
                    })

        return jsonify(return_list)

    def _data_sets(self: GoogleBucketDataSource) -> List[dict]:
        """
        Return a list of datasets.

        Returns
        -------
        List[dict]
            A list of datasets with basic meta data. See the abstract implementation for schema reference.

        Raises
        ------
        NotFound
            If individual configuration resource not found. This implies there are some corrupt/incomplete data sets.
        """
        data_sets = []

        data_set_paths = self._list_directories(self.data_set_root_path)

        for data_set_path in data_set_paths:
            # _list_directories always returns data set directories with a trailing '/'
            data_set_name = data_set_path.split('/')[-2]

            try:
                data_set_config = self._get_json_from_bucket(data_set_path + 'configuration.json')
            except GoogleNotFound as e:
                raise NotFound(f"Configuration file is likely missing for data set: {data_set_name}") from e

            data_set_info = {
                'id': data_set_name,
                'name': data_set_name,
                'ui-path': data_set_config['data-set']['ui-path'],
                'ui-type': data_set_config['data-set']['ui-type'],
                'last-modified': data_set_config['data-set']['last-modified']
            }

            data_sets.append(data_set_info)

        return data_sets

    def _data_set_configuration(self: GoogleBucketDataSource, data_set_id: str) -> dict:
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
        file_path = self.configuration_template.format(data_set_id=data_set_id)

        return self._get_json_from_bucket(file_path)

    def data_set_tiles(self: GoogleBucketDataSource, tile_definition: Tile) -> Response:
        """
        Get single tile of data.

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
            "api-v1/data-sets/{dataset}/tiles/{resolution}/{x}_{y}{z}_{date}.{extension}"

        tile_path = tile_path_template.format(dataset=tile_definition.data_set_id,
                                              resolution=tile_definition.resolution,
                                              x=tile_definition.x,
                                              y=tile_definition.y,
                                              # Optional string item
                                              z=f"_{tile_definition.z}" if tile_definition.z is not None else "",
                                              date=tile_definition.time,
                                              extension=tile_definition.extension
                                              )

        return self.send_file_from_bucket(tile_path)

    def __eq__(self: GoogleBucketDataSource, other_object: object) -> bool:
        """
        Check object for equality.

        We consider two GoogleBucketSource objects equal if they point to the same bucket.

        Parameters
        ----------
        other_object : object
            The object to compare against this one.

        Returns
        -------
        bool
            Whether the two are equal.
        """
        if isinstance(other_object, GoogleBucketDataSource):
            return other_object.bucket_name == self.bucket_name
        return False
