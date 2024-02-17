from ._adverse_impact_ratio import adverse_impact_ratio as adverse_impact_ratio
from pandas import DataFrame, Series
from solas_disparity import const as const
from solas_disparity.types import Disparity as Disparity, DisparityCalculation as DisparityCalculation, StatSig as StatSig, StatSigTest as StatSigTest
from solas_disparity.utils import pgrg_ordered as pgrg_ordered
from typing import List, Optional

def categorical_adverse_impact_ratio(group_data: DataFrame, protected_groups: List[str], reference_groups: List[str], group_categories: List[str], outcome: Series, air_threshold: float, percent_difference_threshold: float, category_order: List[str], label: Optional[Series] = ..., sample_weight: Optional[Series] = ..., max_for_fishers: int = ...) -> Disparity: ...
