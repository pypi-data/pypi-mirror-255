from enum import Enum
from typing import Optional, Tuple

from pydantic import BaseModel


class Scale(str, Enum):
    LINER = "linear"
    LOG = "log"


class LegendLoc(str, Enum):
    BEST = "best"
    UPPER_LEFT = "upper left"
    UPPER_RIGHT = "upper right"
    LOWER_LEFT = "lower left"
    LOWER_RIGHT = "lower right"
    CENTER_LEFT = "center left"
    CENTER_RIGHT = "center right"
    LOWER_CENTER = "lower center"
    UPPER_CENTER = "upper center"
    CENTER = "center"


class SpineConfig(BaseModel):
    label: str = ""
    scale: Scale = Scale.LINER
    lim: Optional[Tuple[float, float]] = None
    step: Optional[float] = None
    pow: int = 0
    visible: bool = True
    invert: bool = False


class AxConfig(BaseModel):
    x: SpineConfig = SpineConfig()
    y: SpineConfig = SpineConfig()
    is_visible_legend: bool = True
    legends_loc: LegendLoc = LegendLoc.UPPER_LEFT
    bbox_to_anchor: Tuple[float, float] = (1.2, 1.0)
