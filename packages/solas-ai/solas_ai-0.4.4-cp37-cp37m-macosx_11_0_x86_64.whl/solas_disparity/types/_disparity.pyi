from ._difference_calculation import DifferenceCalculation as DifferenceCalculation
from ._disparity_calculation import DisparityCalculation as DisparityCalculation
from ._ratio_calculation import RatioCalculation as RatioCalculation
from ._residual_smd_denominator import ResidualSMDDenominator as ResidualSMDDenominator
from ._shortfall_method import ShortfallMethod as ShortfallMethod
from ._smd_denominator import SMDDenominator as SMDDenominator
from ._stat_sig import StatSig as StatSig
from ._stat_sig_test import StatSigTest as StatSigTest
from pandas import DataFrame
from pathlib import Path
from solas_disparity import const as const
from typing import Callable, List, Optional, Tuple, Union

class Disparity:
    @property
    def plot(self): ...
    @plot.setter
    def plot(self, value) -> None: ...
    disparity_type: DisparityCalculation
    summary_table: DataFrame
    protected_groups: List[str]
    reference_groups: List[str]
    group_categories: List[str]
    statistical_significance: Optional[StatSig]
    smd_threshold: Optional[float]
    residual_smd_threshold: Optional[float]
    smd_denominator: Optional[str]
    residual_smd_denominator: Optional[str]
    lower_score_favorable: Optional[bool]
    odds_ratio_threshold: Optional[float]
    air_threshold: Optional[float]
    percent_difference_threshold: Optional[float]
    max_for_fishers: Optional[int]
    shortfall_method: Optional[ShortfallMethod]
    fdr_threshold: Optional[float]
    metric: Callable[..., Union[int, float]]
    difference_calculation: Optional[DifferenceCalculation]
    difference_threshold: Optional[float]
    ratio_calculation: Optional[RatioCalculation]
    ratio_threshold: Optional[float]
    statistical_significance_test: Optional[StatSigTest]
    p_value_threshold: float
    shift_zeros: bool
    drop_small_groups: bool
    small_group_table: DataFrame
    unknown_table: DataFrame
    @property
    def affected_groups(self) -> List[str]: ...
    @property
    def affected_reference(self) -> List[str]: ...
    @property
    def affected_categories(self) -> Optional[List[str]]: ...
    @property
    def report(self) -> Tuple[DataFrame, DataFrame, DataFrame]: ...
    def to_excel(self, file_path: Union[str, Path]): ...
    def show(self) -> None: ...
    def __rich__(self) -> None: ...
    def __init__(self, disparity_type, summary_table, protected_groups, reference_groups, group_categories, statistical_significance, smd_threshold, residual_smd_threshold, smd_denominator, residual_smd_denominator, lower_score_favorable, odds_ratio_threshold, air_threshold, percent_difference_threshold, max_for_fishers, shortfall_method, fdr_threshold, metric, difference_calculation, difference_threshold, ratio_calculation, ratio_threshold, statistical_significance_test, p_value_threshold, shift_zeros, drop_small_groups, small_group_table, unknown_table) -> None: ...
    def __lt__(self, other): ...
    def __le__(self, other): ...
    def __gt__(self, other): ...
    def __ge__(self, other): ...
