import pandas as pd
from solas_disparity import const as const
from solas_disparity.types import Disparity as Disparity, DisparityCalculation as DisparityCalculation, ShortfallMethod as ShortfallMethod, StatSig as StatSig, StatSigTest as StatSigTest
from solas_disparity.utils import pgrg_ordered as pgrg_ordered
from typing import List, Optional

def adverse_impact_ratio(group_data: pd.DataFrame, protected_groups: List[str], reference_groups: List[str], group_categories: List[str], outcome: pd.Series, air_threshold: float, percent_difference_threshold: float, label: Optional[pd.Series] = ..., sample_weight: Optional[pd.Series] = ..., max_for_fishers: int = ..., shortfall_method: Optional[ShortfallMethod] = ...) -> Disparity: ...
