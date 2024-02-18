import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import RigOperationList
from cognite.well_model.client.utils._identifier_list import identifier_list
from cognite.well_model.client.utils.constants import DEFAULT_LIMIT
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import (
    GeneralExternalId,
    GeneralExternalIdItems,
    RigOperation,
    RigOperationFilter,
    RigOperationFilterRequest,
    RigOperationIngestion,
    RigOperationIngestionItems,
    RigOperationItems,
    TimeRange,
)

logger = logging.getLogger(__name__)


class RigOperationsAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def _ingest(self, rig_operations: List[RigOperationIngestion]) -> List[RigOperation]:
        if len(rig_operations) == 0:
            return []
        path = self._get_path("/rigoperations")
        json = RigOperationIngestionItems(items=rig_operations).json()
        response: Response = self.client.post(path, json)
        return RigOperationItems.parse_raw(response.text).items

    def ingest(self, rig_operations: List[RigOperationIngestion]) -> RigOperationList:
        """Ingest Rig Operations

        Args:
            rig_operations (List[RigOperationIngestion])

        Returns:
            RigOperationList: Ingested Rig Operations
        """
        return RigOperationList(
            self.client.process_by_chunks(input_list=rig_operations, function=self._ingest, chunk_size=1000)
        )

    def list(
        self,
        rig_names: Optional[List[str]] = None,
        start_time: Optional[TimeRange] = None,
        end_time: Optional[TimeRange] = None,
        wellbore_asset_external_ids: Optional[List[str]] = None,
        wellbore_matching_ids: Optional[List[str]] = None,
        limit: Optional[int] = DEFAULT_LIMIT,
    ) -> RigOperationList:
        """Get Rig Operations matching the arguments

        Args:
            rig_names (Optional[List[str]], optional)
            start_time (Optional[TimeRange], optional)
            end_time (Optional[TimeRange], optional)
            wellbore_asset_external_ids (Optional[List[str]], optional)
            wellbore_matching_ids (Optional[List[str]], optional)
            limit (Optional[int], optional)

        Returns:
            RigOperationList: List of matched Rig Operations

        Examples:
            Get Rig Operations with ``start_time``.
                >>> from cognite.well_model import CogniteWellsClient, NotSet
                >>> wm = CogniteWellsClient()
                >>> rig_operations = wm.rig_operations.list(
                ...     start_time=TimeRange(min=1609603200000, max=1609761600000)
                ... )

            Get Rig Operations with ``rig_names`` and ``wellbores``
                >>> from cognite.well_model import CogniteWellsClient, NotSet
                >>> wm = CogniteWellsClient()
                >>> rig_operations = wm.rig_operations.list(
                ...     rig_names=["ABCD", "DEFG"],
                ...     wellbore_matching_ids=["13/10-F-11 T2"]
                ... )
        """

        def request(cursor, limit):
            rig_operations_filter = RigOperationFilterRequest(
                filter=RigOperationFilter(
                    rig_names=rig_names,
                    start_time=start_time,
                    end_time=end_time,
                    wellbore_ids=identifier_list(wellbore_asset_external_ids, wellbore_matching_ids),
                ),
                cursor=cursor,
                limit=limit,
            )

            path: str = self._get_path("/rigoperations/list")
            response: Response = self.client.post(url_path=path, json=rig_operations_filter.json())
            rig_operations_items: RigOperationItems = RigOperationItems.parse_raw(response.text)
            return rig_operations_items

        items = cursor_multi_request(
            get_cursor=self._get_cursor, get_items=self._get_items, limit=limit, request=request
        )
        return RigOperationList(items)

    def _delete(self, external_ids: List[GeneralExternalId]) -> List[GeneralExternalId]:
        body = GeneralExternalIdItems(items=external_ids)
        path: str = self._get_path("/rigoperations/delete")
        response: Response = self.client.post(url_path=path, json=body.json())
        response_parsed: GeneralExternalIdItems = GeneralExternalIdItems.parse_raw(response.text)
        return response_parsed.items

    def delete(self, external_ids: List[GeneralExternalId]) -> List[GeneralExternalId]:
        """Delete Rig Operations

        Args:
            external_ids (List[GeneralExternalId]): List of external ids for Rig Operations.

        Returns:
            List[GeneralExternalId]: List of external ids of deleted Rig Operations.
        """
        return self.client.process_by_chunks(input_list=external_ids, function=self._delete, chunk_size=1000)

    @staticmethod
    def _get_items(rig_operations_items: RigOperationItems) -> List[RigOperation]:
        return rig_operations_items.items

    @staticmethod
    def _get_cursor(rig_operations_items: RigOperationItems) -> Optional[str]:
        return rig_operations_items.next_cursor
