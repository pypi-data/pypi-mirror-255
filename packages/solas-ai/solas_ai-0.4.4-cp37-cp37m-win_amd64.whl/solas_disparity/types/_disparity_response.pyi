from ._disparity import Disparity as Disparity
from ._disparity_calculation import DisparityCalculation as DisparityCalculation
from ._shortfall_method import ShortfallMethod as ShortfallMethod
from ._smd_denominator import SMDDenominator as SMDDenominator
from sqlmodel import SQLModel
from typing import List, Optional

class DisparityResponse(SQLModel):
    disparity_type: DisparityCalculation
    summary_table_json: str
    summary_table_json_flat: str
    protected_groups: List[str]
    reference_groups: List[str]
    group_categories: List[str]
    outcome: Optional[str]
    air_threshold: Optional[float]
    percent_difference_threshold: Optional[float]
    label: Optional[str]
    sample_weight: Optional[str]
    max_for_fishers: Optional[int]
    shortfall_method: Optional[ShortfallMethod]
    smd_threshold: Optional[float]
    lower_score_favorable: Optional[bool]
    smd_denominator: Optional[SMDDenominator]
    plot_json: Optional[str]
    @staticmethod
    def from_disparity(disparity: Disparity, *args, **kwargs) -> DisparityResponse: ...
