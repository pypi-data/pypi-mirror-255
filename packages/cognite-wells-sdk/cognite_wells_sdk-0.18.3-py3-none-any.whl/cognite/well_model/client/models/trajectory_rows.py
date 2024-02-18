import math

from pandas import DataFrame

from cognite.well_model.client.utils._auxiliary import to_camel_case
from cognite.well_model.models import TrajectoryData


class TrajectoryRows:
    """Custom data class for displaying trajectory data as data frames."""

    def __init__(self, data: TrajectoryData):
        self.sequence_external_id = data.source.sequence_external_id
        self.wellbore_asset_external_id = data.wellbore_asset_external_id
        self.source = data.source
        self.inclination_unit = data.inclination_unit
        self.azimuth_unit = data.azimuth_unit
        self.type = data.type
        self.measured_depth_unit = data.measured_depth_unit
        self.true_vertical_depth_unit = data.true_vertical_depth_unit
        self.equivalent_departure_unit = data.equivalent_departure_unit

        self.rows = data.rows

    def to_pandas(self, camel_case=True) -> DataFrame:
        """Generate pandas DataFrame

        Returns:
            DataFrame:
        """
        column_names = [
            "measured_depth",
            "true_vertical_depth",
            "azimuth",
            "inclination",
            "northOffset",
            "eastOffset",
            "equivalent_departure",
            "northing",
            "easting",
            "dogleg_severity",
        ]
        column_names = [to_camel_case(x) for x in column_names]
        row_values = []
        for r in self.rows:
            row = [
                r.measured_depth,
                r.true_vertical_depth,
                r.azimuth,
                r.inclination,
                r.north_offset,
                r.east_offset,
                r.equivalent_departure,
                r.northing,
                r.easting,
                r.dogleg_severity,
            ]
            row = [x if x is not None else math.nan for x in row]
            row_values.append(row)
        # TODO: set index to MD and remove MD from values?
        return DataFrame(
            row_values,
            columns=column_names,
        )

    def _repr_html_(self):
        return self.to_pandas()._repr_html_()

    def __getitem__(self, item):
        return self.rows[item]

    def __iter__(self):
        return self.rows.__iter__()

    def __repr__(self):
        return_string = [object.__repr__(d) for d in self.rows]
        return f"[{', '.join(r for r in return_string)}]"

    def __len__(self):
        return self.rows.__len__()
