from mfire.text.wind.reducers.wind_summary_builder.helpers import WindType


class WindFingerprint:
    """WindFingerprint class.

    It contains the typle of the term types and can be serialized as a string.
    """

    def __init__(self, wind_types: list[WindType] | set[WindType] | tuple[WindType]):
        self.data = tuple(wind_types)

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return "".join((str(wind_type.value) for wind_type in self.data))

    def __repr__(self):
        return self.__str__()
