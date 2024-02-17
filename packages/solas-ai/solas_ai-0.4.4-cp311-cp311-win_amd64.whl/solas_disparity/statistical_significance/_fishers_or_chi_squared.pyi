from pandas import DataFrame, Series
from solas_disparity import const as const
from solas_disparity.types import StatSig as StatSig, StatSigTest as StatSigTest
from solas_disparity.utils import pgrg_ordered as pgrg_ordered
from typing import List, Optional, Union

def fishers_or_chi_squared(group_data: DataFrame, protected_groups: List[str], reference_groups: List[str], group_categories: List[str], outcome: Series, sample_weight: Optional[Series] = ..., max_for_fishers: Union[int, float] = ...) -> StatSig: ...
