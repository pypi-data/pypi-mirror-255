from mfire import composite
from mfire.configuration.config_composite import get_aggregation, get_new_threshold

# Basic tests configuration


class Test_get_new_threshold:
    """New class for testing the config composite step"""

    def test_get_new_threshold(self):
        threshold = {"threshold": 0, "comparisonOp": "sup", "units": "m"}
        ref = composite.Threshold(
            threshold=threshold["threshold"],
            comparison_op=threshold["comparisonOp"],
            units=threshold["units"],
        )
        result = get_new_threshold(threshold)
        assert result == ref
        threshold = {"threshold": 8, "comparisonOp": "sup", "units": "m"}
        result = get_new_threshold(threshold)
        assert result != ref

    def test_get_aggregation(self):
        aggregation = {"kwargs": {"dr": 0.05}, "method": "requiredDensity"}
        ref = composite.Aggregation(**aggregation)
        mask_file = None
        grid_name = None
        result = get_aggregation(aggregation, mask_file, grid_name)
        assert result == ref
        aggregation = {"kwargs": {"dr": 5}, "method": "requiredDensity"}
        result = get_aggregation(aggregation, mask_file, grid_name)
        assert result == ref
        aggregation = {"kwargs": {"dr": 12}, "method": "requiredDensity"}
        result = get_aggregation(aggregation, mask_file, grid_name)
        assert result != ref
        pass
