from pandas import DataFrame, Series
from solas_disparity import const as const
from solas_disparity.statistical_significance import fishers_or_chi_squared as fishers_or_chi_squared
from solas_disparity.types import DifferenceCalculation as DifferenceCalculation, Disparity as Disparity, DisparityCalculation as DisparityCalculation, RatioCalculation as RatioCalculation, StatSig as StatSig, StatSigTest as StatSigTest
from solas_disparity.utils import pgrg_ordered as pgrg_ordered
from typing import Any, Callable, Dict, List, Optional, Union

def custom_disparity_metric(group_data: DataFrame, protected_groups: List[str], reference_groups: List[str], group_categories: List[str], outcome: Series, metric: Callable[..., Union[int, float]], label: Optional[Series] = ..., sample_weight: Optional[Series] = ..., difference_calculation: Optional[DifferenceCalculation] = ..., difference_threshold: Optional[Callable[[Union[int, float]], bool]] = ..., ratio_calculation: Optional[RatioCalculation] = ..., ratio_threshold: Optional[Callable[[Union[int, float]], bool]] = ..., statistical_significance_test: Optional[StatSigTest] = ..., p_value_threshold: float = ..., statistical_significance_arguments: Dict[str, Any] = ...) -> Disparity: ...
def resample(data: Union[DataFrame, Series], resamples: int = ..., sample: Union[float, int] = ..., seed: Optional[int] = ..., replace: bool = ...) -> DataFrame: ...
