from pandas import DataFrame, Series as Series
from solas_disparity import const as const
from solas_disparity.types import StatSig as StatSig, StatSigRegressionType as StatSigRegressionType, StatSigTest as StatSigTest
from solas_disparity.utils import pgrg_ordered as pgrg_ordered
from typing import List, Optional

def stacked_regression(group_data: DataFrame, protected_groups: List[str], reference_groups: List[str], group_categories: List[str], outcome: Series, sample_weight: Optional[Series] = ..., regression_type: StatSigRegressionType = ...) -> StatSig: ...
