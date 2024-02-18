import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import WellSourceList
from cognite.well_model.client.utils.constants import DEFAULT_LIMIT
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import WellSourceItems, WellSourcesFilter, WellSourcesFilterRequest

logger = logging.getLogger(__name__)


class WellSourcesAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def list(
        self,
        sources: Optional[List[str]] = None,
        limit: Optional[int] = DEFAULT_LIMIT,
    ) -> WellSourceList:
        """Get well sources that matches the filter

        Args:
            sources (Optional[List[str]], optional):
                List of sources to search for well sources.
            limit (Optional[int], optional):
                Max number of well sources to retrieve. Defaults to 100.

        Returns:
            WellSourceList: List of well sources.

        Examples:
            Get all well sources
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> well_sources = wm.well_sources.list()

            Get well sources from the EDM or VOLVE sources
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> well_sources = wm.well_sources.list(sources=["EDM", "VOLVE"])
        """

        def request(cursor, limit):
            wellsource_filter = WellSourcesFilterRequest(
                filter=WellSourcesFilter(
                    sources=sources,
                ),
                cursor=cursor,
                limit=limit,
            )
            path: str = self._get_path("/wellsources/list")
            response: Response = self.client.post(url_path=path, json=wellsource_filter.json())
            wellsource_items_data: WellSourceItems = WellSourceItems.parse_raw(response.text)
            return wellsource_items_data

        items = cursor_multi_request(
            get_cursor=lambda x: x.next_cursor, get_items=lambda x: x.items, limit=limit, request=request
        )
        return WellSourceList(items)
