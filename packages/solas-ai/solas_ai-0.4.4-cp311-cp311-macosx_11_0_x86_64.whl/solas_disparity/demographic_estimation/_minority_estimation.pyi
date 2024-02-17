import pandas as pd
from ._cache import Cache as Cache
from ._zip9_mixin import ZIP9MatchMixin as ZIP9MatchMixin
from _typeshed import Incomplete
from solas_disparity import const as const
from typing import Tuple

class MinorityEstimation(ZIP9MatchMixin):
    data: Incomplete
    unique_id_column: Incomplete
    zip9_column: Incomplete
    adult_population_only: Incomplete
    census_year: Incomplete
    verbose: Incomplete
    report: Incomplete
    def __init__(self, input_data: pd.DataFrame, unique_id_column: str, zip9_column: str, census_year: int = ..., adult_population_only: bool = ..., verbose: bool = ...) -> None: ...
    def estimate(self) -> Tuple[pd.DataFrame, pd.DataFrame]: ...
