from decimal import Decimal

from analysis.race_distance import RaceDistance
from analysis.weight_for_age import WeightForAgeConverter


class WeightForAgeTable(WeightForAgeConverter):
    """
    A class that represents a weight for age table, such as may be found issued by a horseracing authority or form analyst.

    Inherits from WeightForAgeConverter and adds the ability to lookup weights from a table based on age, distance, and date.
    """

    def _process(self, key: range, val: int, age_in_days: int) -> Decimal:
        return Decimal(str(val))

    @classmethod
    def create(
        cls,
        row_headers: list[RaceDistance],
        column_headers: list[range],
        data: list[list[int]],
    ):
        """
        Creates a new WeightForAgeTable from a list of row headers, column headers, and data.

        Args:
            row_headers: A list of race distances.
            column_headers: A list of age-in-days ranges.
            data: A list of lists of weight allowances.

        Returns:
            A new WeightForAgeTable object.
        """
        table = WeightForAgeTable()
        if len(row_headers) != len(data):
            raise ValueError(
                "The number of row headers must equal the number of data rows."
            )

        for i, row in enumerate(data):
            if len(row) != len(column_headers):
                raise ValueError(
                    f"The number of data columns for row {i} must equal the number of row headers."
                )
            table.add(
                row_headers[i],
                {column_headers[j]: col for j, col in enumerate(row)},
            )
        return table
