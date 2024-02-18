import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import WellboreSourceList
from cognite.well_model.client.utils.constants import DEFAULT_LIMIT
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import WellboreSourceItems, WellboreSourcesFilter, WellboreSourcesFilterRequest

logger = logging.getLogger(__name__)


class WellboreSourcesAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def list(
        self,
        sources: Optional[List[str]] = None,
        limit: Optional[int] = DEFAULT_LIMIT,
    ) -> WellboreSourceList:
        """Get wellbore sources that matches the filter

        Args:
            sources (Optional[List[str]], optional):
                List of sources to search for wellbore sources.
            limit (Optional[int], optional):
                Max number of wellbore sources to retrieve. Defaults to 100.

        Returns:
            WellboreSourceList: List of wellbore sources.

        Examples:
            Get all wellbore sources
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> wellbore_sources = wm.wellbore_sources.list()

            Get wellbore sources from the EDM or VOLVE sources
                >>> from cognite.well_model import CogniteWellsClient, NotSet
                >>> wm = CogniteWellsClient()
                >>> wellbore_sources = wm.wellbore_sources.list(sources=["EDM", "VOLVE"])
        """

        def request(cursor, limit):
            wellboresource_filter = WellboreSourcesFilterRequest(
                filter=WellboreSourcesFilter(
                    sources=sources,
                ),
                cursor=cursor,
                limit=limit,
            )
            path: str = self._get_path("/wellboresources/list")
            response: Response = self.client.post(url_path=path, json=wellboresource_filter.json())
            wellboresource_items_data: WellboreSourceItems = WellboreSourceItems.parse_raw(response.text)
            return wellboresource_items_data

        items = cursor_multi_request(
            get_cursor=lambda x: x.next_cursor, get_items=lambda x: x.items, limit=limit, request=request
        )
        return WellboreSourceList(items)
