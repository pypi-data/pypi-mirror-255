from ._fishers_or_chi_squared import fishers_or_chi_squared as fishers_or_chi_squared
from pandas import DataFrame as DataFrame, Series as Series
from solas_disparity.types import StatSig as StatSig, StatSigTest as StatSigTest
from typing import List, Optional

def chi_squared_test(group_data: DataFrame, protected_groups: List[str], reference_groups: List[str], group_categories: List[str], outcome: Series, sample_weight: Optional[Series] = ...) -> StatSig: ...
