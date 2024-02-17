from ._custom_disparity_metric import custom_disparity_metric as custom_disparity_metric
from pandas import DataFrame as DataFrame, Series as Series
from solas_disparity.types import DifferenceCalculation as DifferenceCalculation, Disparity as Disparity, DisparityCalculation as DisparityCalculation, RatioCalculation as RatioCalculation, StatSigTest as StatSigTest
from typing import Any, Dict, List, Optional

def true_positive_rate(group_data: DataFrame, protected_groups: List[str], reference_groups: List[str], group_categories: List[str], outcome: Series, label: Series, ratio_threshold: float, difference_threshold: float, sample_weight: Optional[Series] = ..., statistical_significance_test: Optional[StatSigTest] = ..., p_value_threshold: float = ..., statistical_significance_arguments: Dict[str, Any] = ...) -> Disparity: ...
