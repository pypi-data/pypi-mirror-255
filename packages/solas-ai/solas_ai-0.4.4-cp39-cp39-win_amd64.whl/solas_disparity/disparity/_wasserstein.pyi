from pandas import DataFrame, Series
from solas_disparity import const as const
from solas_disparity.types import Disparity as Disparity, DisparityCalculation as DisparityCalculation
from solas_disparity.utils import pgrg_ordered as pgrg_ordered
from typing import List, Optional

def wasserstein(group_data: DataFrame, protected_groups: List[str], reference_groups: List[str], group_categories: List[str], outcome: Series, label: Optional[Series] = ..., sample_weight: Optional[Series] = ..., lower_score_favorable: bool = ...) -> Disparity: ...
