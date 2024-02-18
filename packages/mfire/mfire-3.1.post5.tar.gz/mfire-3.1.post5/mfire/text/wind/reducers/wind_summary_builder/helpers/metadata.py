from pydantic import BaseModel, Extra


class MetaData(BaseModel, extra=Extra.allow):
    """MetaData class.

    Used to store the metadata ot the WindSummaryBuilder instances.
    """

    data_points_counter: int
    threshold_accumulated: float = 0.0
    threshold_hours_max: float = 0.0
    threshold: float = 0.0
    filtering_threshold_t2: float = 0.0
    filtering_threshold_t3: float = 0.0
    t2_percent_max_detection: float = 0.0
    t3_percent_max_detection: float = 0.0
    t3_percent_max_confirmation: float = 0.0

    def to_string(self) -> str:
        """Get metadata most interesting elements as a formatted string.

        Elements as ordered as following:
        threshold_accumulated, threshold_hours_max, threshold, t3_percent_max_detection,
        t3_percent_max_confirmation
        """
        output: list[str] = [
            "/".join(
                [
                    str(self.threshold_accumulated),
                    str(self.threshold_hours_max),
                    str(self.threshold),
                ]
            ),
            str(self.t3_percent_max_detection),
            str(self.t3_percent_max_confirmation),
        ]

        return ", ".join(output)
