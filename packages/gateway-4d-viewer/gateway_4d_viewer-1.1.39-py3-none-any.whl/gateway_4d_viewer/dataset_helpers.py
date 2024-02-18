"""
Wrapper functions for dataset information.

This file and package will be deleted once v0 of the API is deprecated.
"""
import json

from google.cloud.storage import Client

from gateway_4d_viewer.google_bucket_source import GoogleBucketDataSource


def get_datasets(client: Client, bucket: str, path: str) -> str:
    """Build a list of available datasets and return as json.

    Parameters
    ----------
    client : Client
        A google cloud storage client instance
    bucket : str
        Google bucket
    path : str
        Google blob path prefix

    Returns
    -------
    str
        Json string.
    """
    delimiter = '/'
    bucket_data_source = GoogleBucketDataSource(bucket, client=client)
    sub_folders = bucket_data_source._list_directories(root_directory=path)
    clean_sub_folders = [sub_folder.replace(path, '', 1).replace(delimiter, '', 1) for sub_folder in sub_folders]
    clean_sub_folders.sort()

    dataset_items = []

    for sub_folder in clean_sub_folders:
        dataset = {
            'id': sub_folder,
            'title': sub_folder
        }

        dataset_items.append(dataset)

    datasets = {'datasets': dataset_items}

    return json.dumps(datasets)
