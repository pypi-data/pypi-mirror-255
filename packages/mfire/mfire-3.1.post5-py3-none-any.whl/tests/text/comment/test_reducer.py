import numpy as np

from mfire.text.comment import Reducer
from tests.composite.factories import RiskComponentCompositeFactory


class TestCommentReducer:
    def test_compute_distance(self):
        np.random.seed(42)
        reducer = Reducer(component=RiskComponentCompositeFactory())
        reducer.compute_distance(norm_risk=[1, 1, 1, 0, 0, 0, 0])
        assert reducer.reduction == {
            "distance": 0.0,
            "path": [(0, 0), (1, 0), (2, 0), (3, 1), (4, 1), (5, 1), (6, 1)],
            "template": "Zone en alerte jusqu’à {B0_stop}. {B0_val}.",
            "centroid": (1.0, 0.0),
            "type": "general",
        }
