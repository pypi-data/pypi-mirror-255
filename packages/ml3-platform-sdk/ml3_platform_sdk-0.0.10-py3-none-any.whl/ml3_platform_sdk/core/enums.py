from enum import Enum


class HTTPMethod(Enum):
    """
    Enum class to represent HTTP methods
    """

    GET = 'GET'
    PUT = 'PUT'
    POST = 'POST'
    PATCH = 'PATCH'
    DELETE = 'DELETE'


class DataCategory(Enum):
    """
    **Fields:**

        - FEATURES
        - PREDICTION
        - TARGET
    """

    FEATURES = 'features'
    PREDICTION = 'prediction'
    TARGET = 'target'


class RawDataSourceType(Enum):
    """
    Enumeration of raw data source types.
    """

    AWS_S3 = 'aws_s3'
    GCS = 'gcs'
    ABS = 'azure_blob_storage'
    LOCAL = 'local'
