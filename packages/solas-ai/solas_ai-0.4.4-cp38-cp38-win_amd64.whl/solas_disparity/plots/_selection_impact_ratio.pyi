from plotly.graph_objects import Figure as Figure
from solas_disparity import const as const
from solas_disparity.types import Disparity as Disparity
from typing import List, Optional, Union

def plot_selection_impact_ratio(disparity: Disparity, column: str = ..., group_category: Optional[Union[str, float]] = ..., separate: bool = ...) -> Union[Figure, List[Figure]]: ...
