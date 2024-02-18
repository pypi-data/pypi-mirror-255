import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.nds_aggregates import NdsAggregateList, NdsAggregateRowList
from cognite.well_model.client.models.property_filter import PropertyFilter, filter_to_model
from cognite.well_model.client.models.resource_list import NdsList
from cognite.well_model.client.utils._identifier_list import identifier_list
from cognite.well_model.client.utils.constants import DEFAULT_LIMIT
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import (
    DeleteEventSources,
    DistanceRange,
    EventExternalId,
    Nds,
    NdsAggregateEnum,
    NdsAggregateItems,
    NdsAggregateRequest,
    NdsAggregateRequestFilter,
    NdsFilter,
    NdsFilterRequest,
    NdsIngestion,
    NdsIngestionItems,
    NdsItems,
)

logger = logging.getLogger(__name__)


class NdsEventsAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def _ingest(self, nds_events: List[NdsIngestion]) -> List[Nds]:
        if len(nds_events) == 0:
            return []
        path = self._get_path("/nds")
        json = NdsIngestionItems(items=nds_events).json()
        response: Response = self.client.post(path, json)
        return NdsItems.parse_raw(response.text).items

    def ingest(self, nds_events: List[NdsIngestion]) -> NdsList:
        """Ingest NDS events

        Args:
            nds_events (List[NdsIngestion]): list of Nds events to ingest
        Returns:
            NdsList:
        """
        return NdsList(self.client.process_by_chunks(input_list=nds_events, function=self._ingest, chunk_size=1000))

    def list(
        self,
        top_measured_depth: Optional[DistanceRange] = None,
        base_measured_depth: Optional[DistanceRange] = None,
        probabilities: Optional[List[int]] = None,
        severities: Optional[List[int]] = None,
        wellbore_asset_external_ids: Optional[List[str]] = None,
        wellbore_matching_ids: Optional[List[str]] = None,
        risk_types: PropertyFilter = None,
        subtypes: PropertyFilter = None,
        limit: Optional[int] = DEFAULT_LIMIT,
    ) -> NdsList:
        """Get Nds events that matches the filter

        Args:
            top_measured_depth: range of top measured depth.
            base_measured_depth: range of base measured depth.
            probabilities: list of probabilities.
            severities: list of severities.
            wellbore_asset_external_ids: list of wellbore asset external ids.
            wellbore_matching_ids: list of wellbore matching ids.
            limit: optional limit.
                Default is 100. Set to `None` to get everything.
        Returns:
            NdsList:
        """

        def request(cursor, limit):
            nds_filter = NdsFilterRequest(
                filter=NdsFilter(
                    top_measured_depth=top_measured_depth,
                    base_measured_depth=base_measured_depth,
                    probabilities=probabilities,
                    severities=severities,
                    wellbore_ids=identifier_list(wellbore_asset_external_ids, wellbore_matching_ids),
                    risk_type=filter_to_model(risk_types),
                    subtype=filter_to_model(subtypes),
                ),
                cursor=cursor,
                limit=limit,
            )

            path: str = self._get_path("/nds/list")
            response: Response = self.client.post(url_path=path, json=nds_filter.json())
            nds_items: NdsItems = NdsItems.parse_raw(response.text)
            return nds_items

        items = cursor_multi_request(
            get_cursor=self._get_cursor, get_items=self._get_items, limit=limit, request=request
        )
        return NdsList(items)

    def _delete(self, event_external_ids: List[str]) -> List[str]:
        body = DeleteEventSources(items=[EventExternalId(event_external_id=id) for id in event_external_ids])
        path: str = self._get_path("/nds/delete")
        response: Response = self.client.post(url_path=path, json=body.json())
        response_parsed: DeleteEventSources = DeleteEventSources.parse_raw(response.text)
        response_nds_external_ids: List[str] = [e.event_external_id for e in response_parsed.items]
        return response_nds_external_ids

    def delete(self, event_external_ids: List[str]) -> List[str]:
        """Delete NPT events

        Args:
            event_external_ids (List[str]): List of external ids for NDS events

        Returns:
            List[str]: List of external ids for deleted NDS events
        """
        return self.client.process_by_chunks(input_list=event_external_ids, function=self._delete, chunk_size=1000)

    @staticmethod
    def _get_items(nds_items: NdsItems) -> List[Nds]:
        items: List[Nds] = nds_items.items  # For mypy
        return items

    @staticmethod
    def _get_cursor(nds_items: NdsItems) -> Optional[str]:
        next_cursor: Optional[str] = nds_items.next_cursor  # For mypy
        return next_cursor

    def aggregate(
        self,
        wellbore_asset_external_ids: Optional[List[str]] = None,
        wellbore_matching_ids: Optional[List[str]] = None,
        group_by: List[NdsAggregateEnum] = [],
    ) -> NdsAggregateList:
        """Aggregate NDS events for a list of wellbores

        Args:
            wellbore_asset_external_ids (Optional[List[str]], optional): List of wellbore asset external ids
            wellbore_matching_ids (Optional[List[str]], optional): List of wellbore matching ids.
            group_by (List[NdsAggregateEnum], optional): List of aggregation types.
                Allowed values: severity, probability, risk type, subtype.

        Returns:
            NdsAggregateList: List of NDS aggregations

        Examples:
            Aggregate NDS events over severity:
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> aggregates = wm.nds.aggregate(
                ...     group_by=["severity"],
                ...     wellbore_matching_ids=["13/10-F-11 T2"]
                ... )
                >>> aggregates.to_pandas()
                  wellboreMatchingId  count
                0      13/10-F-11 T2      3
                >>> aggregates[0].to_pandas()
                  wellboreMatchingId  count  severity
                0      13/10-F-11 T2      1         3
                1      13/10-F-11 T2      2         5
        """
        path: str = self._get_path("/nds/aggregate")
        request_body = NdsAggregateRequest(
            filter=NdsAggregateRequestFilter(
                wellbore_ids=identifier_list(wellbore_asset_external_ids, wellbore_matching_ids),
            ),
            group_by=group_by,
        )
        response: Response = self.client.post(url_path=path, json=request_body.json())
        aggregate_items = NdsAggregateItems.parse_raw(response.text)
        nds_aggregates = []
        for item in aggregate_items.items:
            nds_aggregates.append(NdsAggregateRowList(item.items, item.wellbore_matching_id))

        return NdsAggregateList(nds_aggregates)
