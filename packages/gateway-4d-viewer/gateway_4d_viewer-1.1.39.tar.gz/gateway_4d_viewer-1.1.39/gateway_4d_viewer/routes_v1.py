"""Definition of endpoints for v1 of the API."""
from http import HTTPStatus
import json
from multiprocessing.pool import ThreadPool
from typing import Tuple

from flask import jsonify
from flask import request
from flask import Response
from schema import Schema
from schema import SchemaError
from werkzeug.exceptions import InternalServerError

from gateway_4d_viewer import app
from gateway_4d_viewer.api_schema import REGISTER_DATA_SOURCE_SCHEMA
from gateway_4d_viewer.google_bucket_source import GoogleBucketDataSource
from gateway_4d_viewer.interfaces import DataSourceInterface
from gateway_4d_viewer.interfaces import Tile
from gateway_4d_viewer.xcube_server_source import XCubeDataSource

DEFAULT_BUCKET_SOURCE = GoogleBucketDataSource(app.config['DEFAULT_GOOGLE_BUCKET_NAME'])
DATA_SOURCE_DELIMITER = '~'

DATA_SOURCES = {
    "DTA": DEFAULT_BUCKET_SOURCE,
    # Further sources can be pre-registered here such as:
    "ESDL": XCubeDataSource(server_url='https://api.earthsystemdatalab.net/api/4d_viewer'),
    "XCUBE-DEV": XCubeDataSource(server_url='https://deep-esdl.api.dev.brockmann-consult.de/api/4d_viewer')
}


@app.errorhandler(InternalServerError)
def handle_internal_server(error: InternalServerError) -> Response:
    """
    Handle InternalServerError to pass error details to client.

    Parameters
    ----------
    error : InternalServerError
        The internally raised error

    Returns
    -------
    Response
        InternalServerError response with additional error information.
    """
    response = jsonify({"Internal error": error.description})
    response.status_code = error.code
    return response


def _split_api_id(compound_data_set_id: str) -> Tuple[DataSourceInterface, str]:
    """Return data source instance and data set name.

    For now this API encodes the data source into a compound data set id. We simply split the string based on the
    delimiter to deduce the dataset str and to find and return the correct data source instance.

    Parameters
    ----------
    compound_data_set_id : str
        A compound data-source + data-set string identifier

    Returns
    -------
    tuple[DataSourceInterface, str]
        (Instance of the DataSourceInterface interface, name of dataset)
    """
    key_split = compound_data_set_id.split(DATA_SOURCE_DELIMITER)
    data_source = DATA_SOURCES[key_split[0]]
    data_set = DATA_SOURCE_DELIMITER.join(key_split[1:])
    return data_source, data_set


@app.route("/api-v1/data-sets", methods=["GET"])
def data_sets() -> Response:
    """
    Get a list of available datasets.

    Returns
    -------
    Response
        A collection of meta data for each data set.
    """
    data_sets = []

    # Determine each data-source's list of datasets in parallel. Each call can be slow, but they're almost entirely
    # bound by processes outside of this service. We may seek to increase the number of threads if we add more
    # data sources.
    pool = ThreadPool(processes=4)
    results = pool.map(lambda data_source: DATA_SOURCES[data_source].data_sets(), DATA_SOURCES)

    for data_source, result in zip(DATA_SOURCES, results):
        # Override id field to use a compound source + data set key. This simplifies future api calls and makes
        # deducing data source from request calls easy in those calls.
        for data_set in result:
            data_set['id'] = data_source + DATA_SOURCE_DELIMITER + data_set['id']

        data_sets += result
        response = jsonify(data_sets)

    return response


@app.route("/api-v1/data-sets/<compound_data_set_id>/configuration", methods=["GET"])
def data_set_configuration(compound_data_set_id: str) -> Response:
    """
    Return dataset configuration.

    Parameters
    ----------
    compound_data_set_id : str
        A compound data-source + data-set string identifier

    Returns
    -------
    Response
        Json response with data set meta data.
    """
    data_source, data_set = _split_api_id(compound_data_set_id)

    return data_source.data_set_configuration(data_set)


@app.route("/api-v1/data-sets/<compound_data_set_id>/tiles/<resolution>_<time>_<x>_<y>_<extension>",
           defaults={'z': None})
@app.route("/api-v1/data-sets/<compound_data_set_id>/tiles/<resolution>_<time>_<x>_<y>_<z>_<extension>",
           methods=["GET"])
def data_set_tiles(compound_data_set_id: str,   # noqa:CFQ002 - many arguments are necessary for endpoint.
                   resolution: str, time: str, x: str, y: str, z: str, extension: str) -> Response:
    """Return an individual tile.

    Parameters
    ----------
    compound_data_set_id : str
        A compound data-source + data-set string identifier
    resolution : str
        The desired resolution, defined as '0', '1', '2' etc as defined by the tile grid.
    time : str
        The time index into the list of times in the tile grid meta data ('0', '1', '2').
    x : str
        The x index as defined by the tile grid ('0', '1', '2').
    y : str
        The y index as defined by the tile grid ('0', '1', '2').
    z : str
        The z index (vertical) as defined by the tile grid ('0', '1', '2'). From an API perspective, z is optional.
    extension : str
        File type extension (typically png, or b)
    Returns
    -------
    Response
        A single tile. The exact object format will differ based on file type.
    """
    data_source, data_set = _split_api_id(compound_data_set_id)
    tile_definition = Tile(data_set_id=data_set, resolution=resolution,
                           x=x, y=y, z=z, extension=extension, time=time)

    return data_source.data_set_tiles(tile_definition)


@app.route("/api-v1/color-maps", methods=["GET"])
def color_maps() -> Response:
    """
    Return list of all available color maps.

    As the url is returned to the user, no need to implement a separate
    GET route for the file itself (authentication pending).

    Returns
    -------
    Response
        Response json containing [ {“name”: “”, “link”: “”},{…} ]
    """
    return DEFAULT_BUCKET_SOURCE.file_urls_in_directory("api-v1/colour-maps/")


@app.route("/api-v1/color-maps/<color_map_id>", methods=["GET"])
def color_map(color_map_id: str) -> Response:
    """
    Return individual colour map image.

    Parameters
    ----------
    color_map_id : str
        The color map id to be returned.

    Returns
    -------
    Response
        image type
    """
    return DEFAULT_BUCKET_SOURCE.send_file_from_bucket(f"api-v1/colour-maps/{color_map_id}.png")


@app.route("/api-v1/configurations", methods=["GET"])
def configurations() -> Response:
    """
    Return list of available configurations.

    Returns
    -------
    Response
        Response json containing [ {“name”: “”, “link”: “”},{…} ]
    """
    return DEFAULT_BUCKET_SOURCE.file_urls_in_directory("api-v1/configurations/")


@app.route("/api-v1/configurations/<configuration_id>", methods=["GET"])
def configuration(configuration_id: str) -> Response:
    """
    Get configuration json used for UI world and story setup.

    Parameters
    ----------
    configuration_id : str
        Configuration Id.

    Returns
    -------
    Response
        json containing ui config.
    """
    return DEFAULT_BUCKET_SOURCE.send_file_from_bucket(f"api-v1/configurations/{configuration_id}.json")


@app.route("/register-data-source/<source_id>", methods=["POST"])
def register_data_source(source_id: str) -> Response:
    """
    Register new data source.

    We can register either a google bucket source, by specifying the name of the bucket, or an xcube server source,
    by specifying the server's externally accessible URL.

    Parameters
    ----------
    source_id : str
        Unique identifier of the new source.

    Returns
    -------
    Response
        Failure message - if the request format is invalid or if a source with the same ID but different content (i.e.
        different bucket name of xcube server url) is already present in list of sources.
        Success message otherwise.
    """
    request_data = json.loads(request.data)
    try:
        Schema(REGISTER_DATA_SOURCE_SCHEMA).validate(request_data)
    except SchemaError as err:
        return f'Format invalid: Error: {err}', HTTPStatus.BAD_REQUEST

    data_source_type = request_data["data_source_type"]
    if data_source_type == "google_bucket_data_source":
        new_data_source = GoogleBucketDataSource(bucket_name=request_data["bucket_name"])
    elif data_source_type == "xcube_server_data_source":
        new_data_source = XCubeDataSource(server_url=request_data["server_url"])

    if source_id in DATA_SOURCES and DATA_SOURCES[source_id] != new_data_source:
        return f"Data source {source_id} already present.", HTTPStatus.BAD_REQUEST

    DATA_SOURCES[source_id] = new_data_source
    return f"Data source {source_id} added.", HTTPStatus.OK


@app.route("/deregister-data-source/<source_id>", methods=["DELETE"])
def deregister_data_source(source_id: str) -> Response:
    """
    Delete data source from list of sources.

    Parameters
    ----------
    source_id : str
        ID of source to delete. Same as the source key in the DATA_SOURCES dictionary.

    Returns
    -------
    Response
        Success/failure message.
    """
    if source_id in DATA_SOURCES:
        DATA_SOURCES.pop(source_id)
        return f"Data source {source_id} deleted.", HTTPStatus.OK
    else:
        return f"Data source {source_id} not present, cannot delete.", HTTPStatus.BAD_REQUEST
