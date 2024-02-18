import logging
from typing import List, Optional, cast

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import CasingsList
from cognite.well_model.client.utils._identifier_list import identifier_list
from cognite.well_model.client.utils.constants import DEFAULT_LIMIT
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import (
    CasingFilter,
    CasingFilterRequest,
    CasingIngestionItems,
    CasingItems,
    CasingSchematic,
    CasingSchematicIngestion,
    DeleteSequenceSources,
    SequenceExternalId,
)

logger = logging.getLogger(__name__)


class CasingsAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def _ingest(self, casings: List[CasingSchematicIngestion]) -> List[CasingSchematic]:
        if len(casings) == 0:
            return []
        path = self._get_path("/casings")
        json = CasingIngestionItems(items=casings).json()
        response: Response = self.client.post(path, json)
        return cast(List[CasingSchematic], CasingItems.parse_raw(response.text).items)

    def ingest(self, casings: List[CasingSchematicIngestion]) -> CasingsList:
        """Ingest casings

        Args:
            casings (List[CasingSchematicIngestion]):

        Returns:
            CasingsList:

        Examples:
            Ingesting and delete a casing schematic with assemblies and components:
                >>> from cognite.well_model import CogniteWellsClient
                >>> from cognite.well_model.models import (
                ...     CasingAssembly,
                ...     CasingComponent,
                ...     CasingSchematicIngestion,
                ...     Distance,
                ...     LinearWeight,
                ...     LinearWeightUnit,
                ...     PhaseEnum,
                ...     SequenceSource,
                ... )
                >>> wm = CogniteWellsClient()
                >>> ingestion = CasingSchematicIngestion(
                ...     wellbore_asset_external_id="VOLVE:15/9-F-4",
                ...     source=SequenceSource(
                ...         sequence_external_id="VOLVE:casings-1",
                ...         source_name="VOLVE"
                ...     ),
                ...     phase=PhaseEnum.planned,
                ...     casing_assemblies=[
                ...         CasingAssembly(
                ...             min_inside_diameter=Distance(value=10, unit="inch"),
                ...             min_outside_diameter=Distance(value=11, unit="inch"),
                ...             max_outside_diameter=Distance(value=11, unit="inch"),
                ...             top_measured_depth=Distance(value=8826.79002, unit="foot"),
                ...             base_measured_depth=Distance(value=9687.0, unit="foot"),
                ...             type="conductor",
                ...             report_description="Drill Collar",
                ...             section_type_code="DC",
                ...             components=[
                ...                 CasingComponent(
                ...                     description="Drill Collar 6.5 in, , 105, 91.786",
                ...                     min_inside_diameter=Distance(value=6.5, unit="inch"),
                ...                     max_outside_diameter=Distance(value=6.5, unit="inch"),
                ...                     type_code="DC",
                ...                     top_measured_depth=Distance(value=8826.79002, unit="foot"),
                ...                     base_measured_depht=Distance(value=9687.0, unit="foot"),
                ...                     grade="C-90",
                ...                     connection_name="4 1/2 I",
                ...                     joints=2,
                ...                     manufacturer="BTS Ramco",
                ...
                ...                     # linear weight is 91.7 pounds/foot
                ...                     linear_weight=LinearWeight(
                ...                         value=91.786,
                ...                         unit=LinearWeightUnit(
                ...                             weight_unit="pound",
                ...                             depth_unit="foot"
                ...                         )
                ...                     )
                ...                 )
                ...             ]
                ...         )
                ...     ]
                ... )
                >>> result = wm.casings.ingest([ingestion])
                >>> # Delete the casing again
                >>> _ = wm.casings.delete(["VOLVE:casings-1"])

        """
        return CasingsList(self.client.process_by_chunks(input_list=casings, function=self._ingest, chunk_size=1000))

    def _delete(self, source_external_ids: List[str]) -> List[str]:
        body = DeleteSequenceSources(
            items=[SequenceExternalId(sequence_external_id=external_id) for external_id in source_external_ids]
        )
        path: str = self._get_path("/casings/delete")
        response: Response = self.client.post(url_path=path, json=body.json())
        response_parsed: DeleteSequenceSources = DeleteSequenceSources.parse_raw(response.text)
        return [s.sequence_external_id for s in response_parsed.items]

    def delete(self, source_external_ids: List[str]) -> List[str]:
        """Delete casings

        Args:
            source_external_ids (List[str]): List of casing sources external ids

        Returns:
            List[str]: List of external ids for deleted casings.
        """
        return self.client.process_by_chunks(input_list=source_external_ids, function=self._delete, chunk_size=1000)

    def list(
        self,
        wellbore_asset_external_ids: Optional[List[str]] = None,
        wellbore_matching_ids: Optional[List[str]] = None,
        limit: Optional[int] = DEFAULT_LIMIT,
    ) -> CasingsList:
        """List casings

        Args:
            wellbore_asset_external_ids (Optional[List[str]], optional):
            wellbore_matching_ids (Optional[List[str]], optional):
            limit (Optional[int], optional): Max number of casings.

        Returns:
            CasingsList:
        """

        def request(cursor, limit):
            identifiers = identifier_list(wellbore_asset_external_ids, wellbore_matching_ids)
            path = self._get_path("/casings/list")
            json = CasingFilterRequest(
                filter=CasingFilter(
                    wellbore_ids=identifiers,
                ),
                limit=limit,
                cursor=cursor,
            ).json()
            response: Response = self.client.post(path, json)
            casing_items = CasingItems.parse_raw(response.text)
            return casing_items

        items = cursor_multi_request(
            get_cursor=lambda x: x.next_cursor,
            get_items=lambda x: x.items,
            limit=limit,
            request=request,
        )
        return CasingsList(items)
