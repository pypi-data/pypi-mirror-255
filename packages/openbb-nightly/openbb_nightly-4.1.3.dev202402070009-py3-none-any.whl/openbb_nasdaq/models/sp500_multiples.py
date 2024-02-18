"""Nasdaq SP500 Multiples Model."""

from typing import Any, Dict, List, Optional

import nasdaqdatalink
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.sp500_multiples import (
    SP500MultiplesData,
    SP500MultiplesQueryParams,
)
from openbb_nasdaq.utils.query_params import DataLinkQueryParams
from openbb_nasdaq.utils.series_ids import SP500MULTIPLES


class NasdaqSP500MultiplesQueryParams(SP500MultiplesQueryParams, DataLinkQueryParams):
    """Nasdaq SP500 Multiples Query."""


class NasdaqSP500MultiplesData(SP500MultiplesData):
    """Nasdaq SP500 Multiples Data."""


class NasdaqSP500MultiplesFetcher(
    Fetcher[NasdaqSP500MultiplesQueryParams, List[NasdaqSP500MultiplesData]]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> NasdaqSP500MultiplesQueryParams:
        """Transform the query."""
        return NasdaqSP500MultiplesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: NasdaqSP500MultiplesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Get the raw Nasdaq Data."""
        api_key = credentials.get("nasdaq_api_key") if credentials else ""

        if "Year" in query.series_name:
            query.collapse = "annual"
        if "Quarter" in query.series_name:
            query.collapse = "quarterly"

        data = (
            nasdaqdatalink.get(
                SP500MULTIPLES[query.series_name],
                start_date=query.start_date,
                end_date=query.end_date,
                collapse=query.collapse,
                transform=query.transform,
                api_key=api_key,
                **kwargs,
            )
            .reset_index()
            .rename(columns={"Date": "date", "Value": query.series_name})
        )
        data["date"] = data["date"].dt.strftime("%Y-%m-%d")

        return data.to_dict("records")

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: NasdaqSP500MultiplesQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[NasdaqSP500MultiplesData]:
        """Parse data into the NasdaqSP500MultiplesData format."""
        return [NasdaqSP500MultiplesData.model_validate(d) for d in data]
