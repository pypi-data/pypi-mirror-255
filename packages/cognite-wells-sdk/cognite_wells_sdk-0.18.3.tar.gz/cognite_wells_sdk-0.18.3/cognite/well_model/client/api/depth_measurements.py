import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.depth_measurement_rows import DepthMeasurementRows
from cognite.well_model.client.models.resource_list import DepthMeasurementList
from cognite.well_model.client.utils._auxiliary import extend_class
from cognite.well_model.client.utils._identifier_list import identifier_list
from cognite.well_model.client.utils.constants import DEFAULT_LIMIT
from cognite.well_model.client.utils.exceptions import CogniteInvalidInput
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import (
    ContainsAllOrAny,
    DeleteSequenceSources,
    DepthMeasurement,
    DepthMeasurementData,
    DepthMeasurementDataRequest,
    DepthMeasurementFilter,
    DepthMeasurementFilterRequest,
    DepthMeasurementHoleSectionFilter,
    DepthMeasurementIngestion,
    DepthMeasurementIngestionItems,
    DepthMeasurementItems,
    DepthMeasurementWellTopsFilter,
    DistanceRange,
    DistanceUnit,
    SequenceExternalId,
    SequenceExternalIdItems,
)

logger = logging.getLogger(__name__)


class DepthMeasurementsAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

        @extend_class(DepthMeasurement)
        def data(
            this: DepthMeasurement,
            measured_depth: Optional[DistanceRange] = None,
            depth_unit: Optional[DistanceUnit] = None,
            top_surface_name: Optional[str] = None,
            measurement_types: Optional[List[str]] = None,
            column_external_ids: Optional[List[str]] = None,
            limit: int = DEFAULT_LIMIT,
        ):
            return self.list_data(
                sequence_external_id=this.source.sequence_external_id,
                measured_depth=measured_depth,
                column_external_ids=column_external_ids,
                depth_unit=depth_unit,
                measurement_types=measurement_types,
                top_surface_name=top_surface_name,
                limit=limit,
            )

    def _ingest(self, measurements: List[DepthMeasurementIngestion]) -> List[DepthMeasurement]:
        if len(measurements) == 0:
            return []
        path = self._get_path("/measurements/depth")
        json = DepthMeasurementIngestionItems(items=measurements).json()
        response: Response = self.client.post(path, json)
        return DepthMeasurementItems.parse_raw(response.text).items

    def ingest(self, measurements: List[DepthMeasurementIngestion]) -> DepthMeasurementList:
        """Ingest depth measurements

        Args:
            measurements (List[DepthMeasurementIngestion]):

        Returns:
            DepthMeasurementList:
        """
        return DepthMeasurementList(
            self.client.process_by_chunks(input_list=measurements, function=self._ingest, chunk_size=10)
        )

    def retrieve(self, sequence_external_id: str) -> Optional[DepthMeasurement]:
        """Retrieve a single depth measurement by sequence external id

        Args:
            sequence_external_id (str): Sequence external id

        Returns:
            Optional[DepthMeasurement]: DepthMeasurement if found, else None.

        Examples:
            Retrieve a depth measurement
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> measurement = wm.depth_measurements.retrieve("VOLVE:seq1")
        """
        path = self._get_path("/measurements/depth/byids")
        json = SequenceExternalIdItems(
            items=[SequenceExternalId(sequence_external_id=sequence_external_id)], ignore_unknown_ids=True
        ).json()
        response: Response = self.client.post(path, json)
        items: List[DepthMeasurement] = DepthMeasurementItems.parse_raw(response.text).items
        return items[0] if items else None

    def _retrieve_multiple(self, sequence_external_ids: List[str], ignore_unknown_ids=False) -> List[DepthMeasurement]:
        path = self._get_path("/measurements/depth/byids")
        json = SequenceExternalIdItems(
            items=[SequenceExternalId(sequence_external_id=x) for x in sequence_external_ids],
            ignore_unknown_ids=ignore_unknown_ids,
        ).json()
        response: Response = self.client.post(path, json)
        return DepthMeasurementItems.parse_raw(response.text).items

    def retrieve_multiple(self, sequence_external_ids: List[str], ignore_unknown_ids=False) -> DepthMeasurementList:
        """Retrieve multiple depth measurements by sequence external ids.

        Args:
            sequence_external_ids (List[str]): List of sequence external ids.
            ignore_unknown_ids (bool, optional): Ignore unknown ids. Defaults to False.

        Returns:
            DepthMeasurementList: List of matching depth measurements

        Examples:
            Retrieve two depth measurements
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> measurements = wm.depth_measurements.retrieve_multiple([
                ...    "VOLVE:seq1",
                ...    "VOLVE:seq2"
                ... ])
                >>> len(measurements)
                2
        """
        return DepthMeasurementList(
            self.client.process_by_chunks(
                input_list=sequence_external_ids,
                function=self._retrieve_multiple,
                chunk_size=1000,
                ignore_unknown_ids=ignore_unknown_ids,
            )
        )

    def list(
        self,
        wellbore_asset_external_ids: Optional[List[str]] = None,
        wellbore_matching_ids: Optional[List[str]] = None,
        measurement_types: Optional[List[str]] = None,
        hole_sections: Optional[DepthMeasurementHoleSectionFilter] = None,
        well_tops: Optional[List[str]] = None,
        limit: Optional[int] = DEFAULT_LIMIT,
    ) -> DepthMeasurementList:
        """List depth measurements

        Args:
            wellbore_asset_external_ids (Optional[List[str]], optional):
            wellbore_matching_ids (Optional[List[str]], optional):
            measurement_types (Optional[List[str]], optional): Only get measurements with *any* of these measurement
                types.
            hole_sections (Optional[DepthMeasurementHoleSectionFilter], optional): Only get Depth Measurements that have
                values within a hole section with given properties.
            well_tops (Optional[List[str]], optional): EXPERIMENTAL Only get Depth Measurements that
                penetrate any of the given surfaces. Supports up to 10 well top names.
            limit (Optional[int], optional):

        Returns:
            DepthMeasurementList:
        """

        well_tops_internal = None
        if well_tops is not None:
            if len(well_tops) > 10:
                raise CogniteInvalidInput("Depth measurement well tops filter supports up to 10 well top names")
            else:
                well_tops_internal = DepthMeasurementWellTopsFilter(
                    surface_names=ContainsAllOrAny(contains_any=well_tops)
                )

        def request(cursor, limit):
            identifiers = identifier_list(wellbore_asset_external_ids, wellbore_matching_ids)
            path = self._get_path("/measurements/depth/list")
            json = DepthMeasurementFilterRequest(
                filter=DepthMeasurementFilter(
                    wellbore_ids=identifiers,
                    measurement_types=measurement_types,
                    hole_sections=hole_sections,
                    well_tops=well_tops_internal,
                ),
                limit=limit,
                cursor=cursor,
            ).json()
            response: Response = self.client.post(path, json)
            measurement_items = DepthMeasurementItems.parse_raw(response.text)
            return measurement_items

        items = cursor_multi_request(
            get_cursor=lambda x: x.next_cursor,
            get_items=lambda x: x.items,
            limit=limit,
            request=request,
        )
        return DepthMeasurementList(items)

    def _delete(self, source_external_ids: List[str]) -> List[str]:
        body = DeleteSequenceSources(
            items=[SequenceExternalId(sequence_external_id=external_id) for external_id in source_external_ids]
        )
        path: str = self._get_path("/measurements/depth/delete")
        response: Response = self.client.post(url_path=path, json=body.json())
        response_parsed: DeleteSequenceSources = DeleteSequenceSources.parse_raw(response.text)
        return [s.sequence_external_id for s in response_parsed.items]

    def delete(self, source_external_ids: List[str]) -> List[str]:
        """Delete depth measurements

        Args:
            source_external_ids (List[str]): List of external ids for sources to depth measurements to be deleted

        Returns:
            List[str]: List of external ids for deleted depth measurements.
        """
        return self.client.process_by_chunks(input_list=source_external_ids, function=self._delete, chunk_size=1000)

    def list_data(
        self,
        sequence_external_id: str,
        measured_depth: Optional[DistanceRange] = None,
        depth_unit: Optional[DistanceUnit] = None,
        measurement_types: Optional[List[str]] = None,
        column_external_ids: Optional[List[str]] = None,
        top_surface_name: Optional[str] = None,
        limit: int = DEFAULT_LIMIT,
    ) -> DepthMeasurementRows:
        """Get depth measurement data.

        Note: It is not supported to filter on both measurement types and column external IDs in the same query.

        Args:
            sequence_external_id (str): Sequence external ID.
            measured_depth (Optional[DistanceRange], optional): measured depth range.
            depth_unit (Optional[DistanceUnit], optional): Unit and factor for the depth values.
            measurement_types (Optional[List[str]], optional):
                Only retrieve columns matching any of these measurement types.
            column_external_ids (Optional[List[str]], optional): Only retrieve these columns.
            top_surface_name (Optional[str], optional): If set, only get the rows
                inside the range defined by the top surface.
            limit (int, optional): Max number of rows to get. Defaults to 100.

        Returns:
            DepthMeasurementRows: Depth measurement with data. An iterator over rows.

        Examples:
            Get depth measurement data
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> data = wm.depth_measurements.list_data(
                ...     sequence_external_id="VOLVE:seq1"
                ... )
                >>> df = data.to_pandas()

            Get depth measurement data using ``.data()``
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> depth_measurement = wm.depth_measurements.list()[0]
                >>> data = depth_measurement.data()
                >>> df = data.to_pandas()

            Get depth measurement data in MD range
                Only get the rows between 150.0 and 500.0 meters MD

                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> depth_measurement = wm.depth_measurements.list()[0]
                >>> data = depth_measurement.data(
                ...     measured_depth={
                ...         "min": 150.0,
                ...         "max": 500.0,
                ...         "unit": "meter",
                ...     }
                ... )

            Get only gamma ray measurements
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> data = wm.depth_measurements.list_data(
                ...     sequence_external_id="VOLVE:seq1",
                ...     measurement_types=["gamma ray"],
                ... )
                >>> df = data.to_pandas()

            Get only RMED measurements
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> data = wm.depth_measurements.list_data(
                ...     sequence_external_id="VOLVE:seq1",
                ...     column_external_ids=["RMED"],
                ... )
                >>> df = data.to_pandas()

            Filter and retrieve only gamma ray measurements
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> depth_measurements = wm.depth_measurements.list(
                ...     measurement_types=["gamma ray"]
                ... )
                >>> dm = depth_measurements[0]
                >>> # Will only retrieve the "gamma ray" columns.
                >>> data = dm.data(measurement_types=["gamma ray"])
        """

        class LastResponse:
            # Using a class with a static variable due to python scoping rules.
            value: DepthMeasurementData = None

        def request(cursor, limit):
            path = self._get_path("/measurements/depth/data")
            json = DepthMeasurementDataRequest(
                sequence_external_id=sequence_external_id,
                measured_depth=measured_depth,
                depth_unit=depth_unit,
                measurement_types=measurement_types,
                column_external_ids=column_external_ids,
                top_surface_name=top_surface_name,
                limit=limit,
                cursor=cursor,
            ).json()
            response: Response = self.client.post(path, json)
            data = DepthMeasurementData.parse_raw(response.text)
            LastResponse.value = data
            return data

        all_rows = cursor_multi_request(
            get_cursor=lambda x: x.next_cursor,
            get_items=lambda x: x.rows,
            limit=limit,
            request=request,
        )
        LastResponse.value.rows = all_rows
        return DepthMeasurementRows.from_measurement_data(LastResponse.value)
