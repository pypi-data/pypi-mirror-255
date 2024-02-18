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
from spotlight.core.common.decorators import async_data_request
from spotlight.core.common.requests import __async_get_request, __async_post_request


async def _async_query_timeseries(request: TimeseriesQueryRequest):
    """
    Asynchronously query timeseries dataset by timeseries query request.

    Args:
        request (TimeseriesQueryRequest): Timeseries query request

    Returns:
        Response: Response
    """
    request_info = _query_timeseries_request_info(request)
    return await __async_post_request(**request_info)


async def _async_query_distinct_fields(
    request: DistinctQueryRequest, use_cache: Optional[bool] = None
):
    """
    Asynchronously query dataset for distinct values of a specified field.

    Args:
        request (DistinctQueryRequest): Distinct query request
        use_cache (Optional[bool]): Flag to determine whether data cache should be used in fetching unique values

    Returns:
        Response: Response
    """
    request_info = _query_distinct_fields_request_info(request, use_cache)
    return await __async_post_request(**request_info)


@async_data_request
async def async_query_timeseries(request: TimeseriesQueryRequest) -> List[Any]:
    """
    Asynchronously query timeseries dataset by timeseries query request.

    Args:
        request (TimeseriesQueryRequest): Timeseries query request

    Returns:
        pd.DataFrame: Timeseries DataFrame
    """
    return await _async_query_timeseries(request)


async def async_query_dataset_csv(id: str, request: TimeseriesQueryRequest) -> Response:
    """
    Asynchronously query dataset CSV by ID.

    Args:
        id (str): Dataset ID
        request (TimeseriesQueryRequest): Timeseries query request

    Returns:
        Response: HTTP response object
    """
    request_info = _query_dataset_csv_request_info(id, request)
    return await __async_get_request(**request_info)


@async_data_request
async def async_query_distinct_fields(
    request: DistinctQueryRequest, use_cache: Optional[bool] = None
) -> List[str]:
    """
    Asynchronously query dataset for distinct values of a specified field.

    Args:
        request (DistinctQueryRequest): Distinct query request
        use_cache (Optional[bool]): Flag to determine whether data cache should be used in fetching unique values

    Returns:
        pd.DataFrame: Timeseries DataFrame
    """
    return await _async_query_distinct_fields(request, use_cache)


@async_data_request
async def async_sdr_health() -> List[dict]:
    """
    Asynchronously get SDR Data health.

    Returns:
        List[dict]: Data response
    """
    request_info = _sdr_health_request_info()
    return await __async_get_request(**request_info)
