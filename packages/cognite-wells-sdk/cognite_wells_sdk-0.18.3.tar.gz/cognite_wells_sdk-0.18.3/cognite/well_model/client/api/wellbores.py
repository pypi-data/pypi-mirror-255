import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.api.merge_rules.wellbores import WellboreMergeRulesAPI
from cognite.well_model.client.models.resource_list import WellboreList
from cognite.well_model.client.models.wellbore_merge_details import WellboreMergeDetailList, WellboreMergeDetailResource
from cognite.well_model.client.utils._auxiliary import extend_class
from cognite.well_model.client.utils._identifier_list import (
    create_identifier,
    identifier_items_from_ids,
    identifier_items_single,
    identifier_list,
)
from cognite.well_model.client.utils.exceptions import CogniteInvalidInput
from cognite.well_model.models import (
    Identifier,
    IdentifierItems,
    Wellbore,
    WellboreItems,
    WellboreMergeDetailItems,
    WellboreMergeDetails,
    WellboreSource,
    WellboreSourceItems,
)

logger = logging.getLogger(__name__)


class WellboresAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)
        self.merge_rules = WellboreMergeRulesAPI(client)

        @extend_class(Wellbore)
        def merge_details(this: Wellbore) -> WellboreMergeDetailResource:
            _md = self.merge_details(matching_id=this.matching_id)
            assert _md is not None
            return _md

    def _ingest(self, ingestions: List[WellboreSource]) -> WellboreList:
        if len(ingestions) == 0:
            return WellboreList([])
        path = self._get_path("/wellbores")
        json = WellboreSourceItems(items=ingestions).json()
        response: Response = self.client.post(path, json)
        wellbore_items: WellboreItems = WellboreItems.parse_obj(response.json())
        wellbores: List[Wellbore] = wellbore_items.items
        return WellboreList(wellbores)

    def ingest(self, ingestions: List[WellboreSource]) -> WellboreList:
        """Ingest wellbores

        Args:
            ingestions (List[WellboreSource]):

        Returns:
            WellboreList:
        """
        return WellboreList(self.client.process_by_chunks(input_list=ingestions, function=self._ingest, chunk_size=100))

    def _retrieve_multiple(self, items: List[Identifier], ignore_unknown_ids: bool = False) -> List[Wellbore]:
        path: str = self._get_path("/wellbores/byids")
        chunk_identifiers = IdentifierItems(items=items, ignore_unknown_ids=ignore_unknown_ids)
        response: Response = self.client.post(url_path=path, json=chunk_identifiers.json())
        wellbore_items: WellboreItems = WellboreItems.parse_raw(response.text)
        wellbores: List[Wellbore] = wellbore_items.items
        return wellbores

    def retrieve(
        self,
        asset_external_id: Optional[str] = None,
        matching_id: Optional[str] = None,
    ) -> Wellbore:
        """Get wellbore by asset external id or matching id.

        Args:
            asset_external_id (Optional[str], optional)
            matching_id (Optional[str], optional)

        Returns:
            Wellbore:
        """
        items = [create_identifier(asset_external_id, matching_id)]
        # TODO: We should change this to ignore_unknown_ids=True and return None
        # if it isn't found.
        return self._retrieve_multiple(items=items, ignore_unknown_ids=False)[0]

    def retrieve_multiple(
        self,
        asset_external_ids: Optional[List[str]] = None,
        matching_ids: Optional[List[str]] = None,
        ignore_unknown_ids: bool = False,
    ) -> WellboreList:
        """Get wellbores by a list assets external ids and matching ids

        Args:
            asset_external_ids (Optional[List[str]]): list of wellbore asset external ids
            matching_ids (Optional[List[str]]): List of wellbore matching ids
            ignore_unknown_ids (bool): Set to true to ignore wellbores that aren't found.
        Returns:
            WellboreList:
        """
        items = identifier_list(asset_external_ids, matching_ids)
        if not items:
            raise CogniteInvalidInput("Identifier list can't be empty")

        return WellboreList(
            self.client.process_by_chunks(
                input_list=items,
                function=self._retrieve_multiple,
                chunk_size=1000,
                ignore_unknown_ids=ignore_unknown_ids,
            )
        )

    def merge_details(
        self,
        asset_external_id: Optional[str] = None,
        matching_id: Optional[str] = None,
    ) -> Optional[WellboreMergeDetailResource]:
        """Retrieve merge details for a wellbore

        Args:
            asset_external_id (str, optional)
            matching_id (str, optional)
        Returns:
            Optional[WellboreMergeDetailResource]: merge details if the wellbore exists.

        Examples:
            Get merge details for a single wellbore
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> details = wm.wellbores.merge_details(matching_id="11/5-F-5")

            Get merge details for a Wellbore object
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> details = wm.wellbores.retrieve(matching_id="11/5-F-5").merge_details()
        """
        identifiers = identifier_items_single(
            asset_external_id=asset_external_id,
            matching_id=matching_id,
        )
        identifiers.ignore_unknown_ids = True

        path = self._get_path("/wellbores/mergedetails")
        response = self.client.post(path, json=identifiers.json())

        items = WellboreMergeDetailItems.parse_raw(response.content)
        if len(items.items) == 0:
            return None
        assert len(items.items) == 1
        return WellboreMergeDetailResource(items.items[0])

    def _merge_details_multiple(
        self,
        ids: Optional[List[Identifier]],
        ignore_unknown_ids: Optional[bool] = False,
    ) -> List[WellboreMergeDetails]:
        identifiers = identifier_items_from_ids(ids)
        identifiers.ignore_unknown_ids = ignore_unknown_ids

        path = self._get_path("/wellbores/mergedetails")
        response = self.client.post(path, json=identifiers.json())

        items = WellboreMergeDetailItems.parse_raw(response.content)
        return items.items

    def merge_details_multiple(
        self,
        asset_external_ids: Optional[List[str]] = None,
        matching_ids: Optional[List[str]] = None,
        ignore_unknown_ids: Optional[bool] = False,
    ) -> WellboreMergeDetailList:
        """Retrieve merge details for multiple wellbores

        Args:
            asset_external_ids: list of wellbore asset external ids.
            matching_ids: List of wellbore matching ids.
            ignore_unknown_ids (Optional[bool]): If set to True,
                it will ignore unknown wells.

        Returns:
            WellboreMergeDetailList: List-like object of merge details

        Examples:
            Get merge details for a single well
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> details = wm.wellbores.merge_details_multiple(matching_ids=["11/5-F-5"])
        """
        ids = identifier_list(asset_external_ids, matching_ids)

        items = self.client.process_by_chunks(
            input_list=ids,
            function=self._merge_details_multiple,
            chunk_size=1000,
            ignore_unknown_ids=ignore_unknown_ids,
        )
        return WellboreMergeDetailList([WellboreMergeDetailResource(item) for item in items])
