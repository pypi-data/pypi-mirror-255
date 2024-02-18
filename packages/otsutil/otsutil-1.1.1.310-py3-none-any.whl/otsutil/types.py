"""よく使う型ヒントや定義を纏めたモジュールです。
"""

__all__ = (
    "FLOAT_INT",
    "K",
    "P",
    "R",
    "T",
    "V",
    "hmsValue",
    "pathLike",
)

from pathlib import Path
from typing import ParamSpec, TypeVar

# ジェネリクス
FLOAT_INT = TypeVar("FLOAT_INT", float, int)
K = TypeVar("K")
P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")
V = TypeVar("V")

# タイプエイリアス
hmsValue = tuple[int, int, float]
pathLike = Path | str
