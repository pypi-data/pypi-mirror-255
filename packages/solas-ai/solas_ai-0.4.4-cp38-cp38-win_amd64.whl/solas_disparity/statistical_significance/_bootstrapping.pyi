from pandas import DataFrame as DataFrame, Series as Series
from solas_disparity import const as const
from solas_disparity.types import StatSig as StatSig
from typing import List, Optional, Union

def bootstrapping(group_data: DataFrame, protected_groups: List[str], reference_groups: List[str], group_categories: List[str], outcome: Series, sample_weight: Optional[Series] = ..., resamples: int = ..., sample: Union[float, int] = ..., seed: Optional[int] = ..., replace: bool = ...) -> StatSig: ...
