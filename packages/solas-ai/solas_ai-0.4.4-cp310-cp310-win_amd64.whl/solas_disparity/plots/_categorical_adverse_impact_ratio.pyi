from plotly.graph_objects import Figure as Figure
from solas_disparity import const as const
from solas_disparity.types import Disparity as Disparity
from typing import List, Optional, Union

def plot_categorical_adverse_impact_ratio(disparity: Disparity, column: str = ..., category: Optional[Union[str, float]] = ..., separate: bool = ..., group: Optional[str] = ...) -> Union[Figure, List[Figure]]: ...
