from typing import List, Optional, Any

import pandas as pd
from requests import Response

from spotlight.api.data.__util import (
    _query_dataset_csv_request_info,
    _query_timeseries_request_info,
    _query_distinct_fields_request_info,
    _sdr_health_request_info,
)
from spotlight.api.data.model import TimeseriesQueryRequest, DistinctQueryRequest
from spotlight.core.common.decorators import data_request
from spotlight.core.common.requests import __get_request, __post_request


def _query_timeseries(request: TimeseriesQueryRequest):
    """
    Query timeseries dataset by timeseries query request.

    Args:
        request (TimeseriesQueryRequest): Timeseries query request

    Returns:
        Response: Response
    """
    request_info = _query_timeseries_request_info(request)
    return __post_request(**request_info)


def _query_distinct_fields(
    request: DistinctQueryRequest, use_cache: Optional[bool] = None
):
    """
    Query dataset for distinct values of a specified field.

    Args:
        request (DistinctQueryRequest): Distinct query request
        use_cache (Optional[bool]): Flag to determine whether data cache should be used in fetching unique values

    Returns:
        Response: Response
    """
    request_info = _query_distinct_fields_request_info(request, use_cache)
    return __post_request(**request_info)


@data_request
def query_timeseries(request: TimeseriesQueryRequest) -> List[Any]:
    """
    Query timeseries dataset by timeseries query request.

    Args:
        request (TimeseriesQueryRequest): Timeseries query request

    Returns:
        pd.DataFrame: Timeseries DataFrame
    """
    return _query_timeseries(request)


def query_dataset_csv(id: str, request: TimeseriesQueryRequest) -> Response:
    """
    Query dataset CSV by ID.

    Args:
        id (str): Dataset ID
        request (TimeseriesQueryRequest): Timeseries query request

    Returns:
        Response: HTTP response object
    """
    request_info = _query_dataset_csv_request_info(id, request)
    return __get_request(**request_info)


@data_request
def query_distinct_fields(
    request: DistinctQueryRequest, use_cache: Optional[bool] = None
) -> List[str]:
    """
    Query dataset for distinct values of a specified field.

    Args:
        request (DistinctQueryRequest): Distinct query request
        use_cache (Optional[bool]): Flag to determine whether data cache should be used in fetching unique values

    Returns:
        pd.DataFrame: Timeseries DataFrame
    """
    return _query_distinct_fields(request, use_cache)


@data_request
def sdr_health() -> List[dict]:
    """
    Get SDR Data health.

    Returns:
        List[dict]: Data response
    """
    request_info = _sdr_health_request_info()
    return __get_request(**request_info)
