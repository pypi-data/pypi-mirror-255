import pandas as pd
from ._gender_estimation import GenderEstimation as GenderEstimation
from ._minority_estimation import MinorityEstimation as MinorityEstimation
from ._race_estimation import RaceEstimation as RaceEstimation
from solas_disparity import const as const
from solas_disparity.types import DemographicEstimation as DemographicEstimation
from typing import Optional

def demographic_estimation(input_data: pd.DataFrame, unique_id_column: str, last_name_column: Optional[str] = ..., first_name_column: Optional[str] = ..., zip9_column: Optional[str] = ..., geoid_column: Optional[str] = ..., latitude_column: Optional[str] = ..., longitude_column: Optional[str] = ..., zip5_column: Optional[str] = ..., census_year: Optional[int] = ..., adult_population_only: Optional[bool] = ..., use_surname_defaults: Optional[bool] = ..., estimate_race_proportion: bool = ..., estimate_gender_proportion: bool = ..., verbose: bool = ...) -> DemographicEstimation: ...
def minority_estimation(input_data: pd.DataFrame, unique_id_column: str, zip9_column: str, census_year: int = ..., adult_population_only: bool = ..., verbose: bool = ...) -> DemographicEstimation: ...
