from ._adverse_impact_ratio import adverse_impact_ratio as adverse_impact_ratio
from pandas import DataFrame as DataFrame, Series as Series
from solas_disparity import const as const
from solas_disparity.types import Disparity as Disparity, DisparityCalculation as DisparityCalculation, ShortfallMethod as ShortfallMethod
from typing import List, Optional

def relative_rate(group_data: DataFrame, protected_groups: List[str], reference_groups: List[str], group_categories: List[str], outcome: Series, ratio_threshold: float, percent_difference_threshold: float, label: Optional[Series] = ..., sample_weight: Optional[Series] = ..., max_for_fishers: int = ..., shortfall_method: Optional[ShortfallMethod] = ...) -> Disparity: ...
