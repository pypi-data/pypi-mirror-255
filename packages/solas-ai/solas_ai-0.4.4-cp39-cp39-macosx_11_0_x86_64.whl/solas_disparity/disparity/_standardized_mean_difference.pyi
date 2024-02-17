from pandas import DataFrame, Series
from solas_disparity import const as const
from solas_disparity.types import Disparity as Disparity, DisparityCalculation as DisparityCalculation, SMDDenominator as SMDDenominator, StatSig as StatSig, StatSigTest as StatSigTest
from solas_disparity.utils import pgrg_ordered as pgrg_ordered
from typing import List, Optional

def standardized_mean_difference(group_data: DataFrame, protected_groups: List[str], reference_groups: List[str], group_categories: List[str], outcome: Series, smd_threshold: float, lower_score_favorable: bool = ..., label: Optional[Series] = ..., sample_weight: Optional[Series] = ..., smd_denominator: SMDDenominator = ...) -> Disparity: ...
