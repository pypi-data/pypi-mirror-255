from pydantic import BaseModel
from solas_disparity import const as const
from solas_disparity.types import ResidualSMDDenominator as ResidualSMDDenominator, SMDDenominator as SMDDenominator, ShortfallMethod as ShortfallMethod, StatSigTest as StatSigTest
from typing import Any, Dict, List, Optional

class RequestBase(BaseModel):
    group_data: str
    protected_groups: str
    reference_groups: str
    group_categories: str
    outcome: str
    label: Optional[str]
    autodelete_data: bool

class RequestBaseSampleWeight(RequestBase):
    sample_weight: Optional[str]

class RequestWasserstein(RequestBaseSampleWeight):
    lower_score_favorable: bool

class RequestOddsRatio(RequestBaseSampleWeight):
    odds_ratio_threshold: float
    percent_difference_threshold: float
    max_for_fishers: int
    lower_score_favorable: bool

class RequestAir(RequestBaseSampleWeight):
    air_threshold: float
    percent_difference_threshold: float
    max_for_fishers: int
    shortfall_method: Optional[ShortfallMethod]

class RequestRr(RequestBaseSampleWeight):
    ratio_threshold: float
    percent_difference_threshold: float
    max_for_fishers: int
    shortfall_method: Optional[ShortfallMethod]

class RequestAirByQuantile(RequestAir):
    quantiles: List[float]
    lower_score_favorable: bool
    merge_bins: bool

class RequestCategoricalAdverseImpactRatio(RequestAir):
    category_order: List[str]

class RequestSegmentedAdverseImpactRatio(RequestAir):
    fdr_threshold: float
    segment: str
    shift_zeros: bool

class RequestSmd(RequestBaseSampleWeight):
    smd_threshold: float
    lower_score_favorable: bool
    smd_denominator: SMDDenominator

class RequestResidualSmd(RequestBaseSampleWeight):
    residual_smd_threshold: float
    lower_score_favorable: bool
    residual_smd_denominator: ResidualSMDDenominator
    prediction: str

class RequestRateBase(RequestBaseSampleWeight):
    ratio_threshold: float
    difference_threshold: float
    statistical_significance_test: Optional[StatSigTest]
    p_value_threshold: float
    statistical_significance_arguments: Dict[str, Any]

class RequestPrecision(RequestRateBase):
    statistical_significance_test: Optional[StatSigTest]
    p_value_threshold: float
    statistical_significance_arguments: Dict[str, Any]

class RequestFalseDiscoveryRate(RequestRateBase): ...
class RequestFalseNegativeRate(RequestRateBase): ...
class RequestFalsePositiveRate(RequestRateBase): ...
class RequestTrueNegativeRate(RequestRateBase): ...
class RequestTruePositiveRate(RequestRateBase): ...
