"""Schemas that define messages received via the API."""
from schema import Optional, Or, Regex


REGISTER_DATA_SOURCE_SCHEMA = Or({
    "data_source_type": "google_bucket_data_source",
    "bucket_name": str,
},
    {
    "data_source_type": "xcube_server_data_source",
    "server_url": str
})


# Iso date format "2023-03-08T01:39:51.352554Z" - sub second accuracy is optional.
ISO_DATE_SCHEMA = Regex(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}.*Z')
# Must start and end with a /
UI_PATH_SCHEMA = Regex(r'^/.*/$')
# Accepted layer types in the UI
UI_TYPE_SCHEMA = Or('flux',
                    'flux3d',
                    'heatmap',
                    'heatmap3d',
                    'heightmap',
                    'mesh')
# Used typically for floats that may or may not be persisted/cast as ints (e.g. resolution 500.0 vs 500)
NUMBER_SCHEMA = Or(float, int)

DATA_SET_SCHEMA = {
    # Unique identifier within the data source
    "id": str,
    # Datetime of last data set update
    "last-modified": ISO_DATE_SCHEMA,
    # Pretty name for the client
    "name": str,
    # Hierarchical path-like string to manage large number of datasets in the client.
    "ui-path": UI_PATH_SCHEMA,
    # Intended use by the client to determine what can be done with a given dataset.
    "ui-type": UI_TYPE_SCHEMA
}

DATA_SETS_SCHEMA = [DATA_SET_SCHEMA]

CONFIGURATION_SCHEMA = {
    "data-set": {
        # The units of the data values in the data set.
        "units": str,
        # This is the min/max value range of the data in the data set.
        # The main current use case is for denormalisation of data compressed into png/byte ranges.
        # e.g. a min: 5, max 10 would mean a png value byte would translate from 0->5 and 255->10.
        "value-range": {
            "min": float,
            "max": float
        },
        # A list of datetimes for which the data exists. (This tends to not be a regular axis)
        "times": [ISO_DATE_SCHEMA],
        # Hierarchical path-like string to manage large number of datasets in the client.
        "ui-path": UI_PATH_SCHEMA,
        # Intended use by the client to determine what can be done with a given dataset.
        "ui-type": UI_TYPE_SCHEMA,
        # Datetime of last data set update
        "last-modified": ISO_DATE_SCHEMA
    },
    "tile-grid": {
        # The extent of the dataset. Note: not necessarily a whole number of tiles!
        "extent": {
            "x": {
                "min": NUMBER_SCHEMA,
                "max": NUMBER_SCHEMA
            },
            "y": {
                "min": NUMBER_SCHEMA,
                "max": NUMBER_SCHEMA
            },
            Optional("z"): {
                "min": NUMBER_SCHEMA,
                "max": NUMBER_SCHEMA
            }
        },
        # The coordinates of the corner of the first tile in the tile grid. Whether that's the top/bottom, left/right is
        # determined by tile-orientation,
        "origin": {
            "x": NUMBER_SCHEMA,
            "y": NUMBER_SCHEMA,
            Optional("z"): NUMBER_SCHEMA
        },
        # The number of 'pixels' in each tile
        "tile-size": {
            "x": int,
            "y": int,
            Optional("z"): int
        },
        # The real-world size of a given tile at the lowest resolution. Other resolutions are deduced from this.
        "lowest-resolution-tile-extent": {
            "x": NUMBER_SCHEMA,
            "y": NUMBER_SCHEMA,
            Optional("z"): NUMBER_SCHEMA
        },
        # How the tile grid and the contents of each tile are oriented. By default, we try and follow the convention
        # that pngs are y-affine negative and x-affine positive. z is prefered as positive, too.
        "tile-orientation": {
            "x": Or("positive", "negative"),
            "y": Or("positive", "negative"),
            Optional("z"): Or("positive", "negative")
        },
        # How many resolution levels of data exist.
        "number-of-resolutions": int,
        # Which projection the tiles are served in. Must be in EPSG: or blank for now.
        Optional("projection"): Regex(r"^$|EPSG:[0-9]{4,5}$")
    }
}
