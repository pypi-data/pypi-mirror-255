import pytest

from mfire.composite import ComparisonOperator
from mfire.text.comment.monozone import Monozone


class TestMonozone:
    @pytest.mark.parametrize(
        "param,expected",
        [
            # Plain cases
            ({"plain": {"value": 1.5, "operator": ComparisonOperator.SUP}}, True),
            ({"plain": {"value": 2.5, "operator": ComparisonOperator.INF}}, True),
            ({"plain": {"value": 1.5, "operator": ComparisonOperator.INF}}, False),
            ({"plain": {"value": 2.5, "operator": ComparisonOperator.SUP}}, False),
            # Mountain cases
            (
                {
                    "plain": {"value": 2.0, "operator": ComparisonOperator.INFEGAL},
                    "mountain": {"value": 0.5, "operator": ComparisonOperator.SUP},
                },
                True,
            ),
            (
                {
                    "plain": {"value": 2.0, "operator": ComparisonOperator.INFEGAL},
                    "mountain": {"value": 1.5, "operator": ComparisonOperator.INF},
                },
                True,
            ),
            (
                {
                    "plain": {"value": 2.0, "operator": ComparisonOperator.INFEGAL},
                    "mountain": {"value": 0.5, "operator": ComparisonOperator.INF},
                },
                False,
            ),
            (
                {
                    "plain": {"value": 2.0, "operator": ComparisonOperator.INFEGAL},
                    "mountain": {"value": 1.5, "operator": ComparisonOperator.SUP},
                },
                False,
            ),
        ],
    )
    def test_compare_param(self, param, expected):
        max_val = {"plain": {"value": 2.0}, "mountain": {"value": 1.0}}
        assert Monozone.compare_param(max_val, param) == expected
