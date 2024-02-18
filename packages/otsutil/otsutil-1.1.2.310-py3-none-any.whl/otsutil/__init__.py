"""個人的によく使う関数、クラス、型ヒントを纏めたライブラリ。
"""

__all__ = (
    "FLOAT_INT",
    "K",
    "LockableDict",
    "LockableList",
    "ObjectSaver",
    "OtsuNone",
    "P",
    "R",
    "T",
    "Timer",
    "V",
    "deduplicate",
    "hmsValue",
    "load_json",
    "pathLike",
    "read_lines",
    "same_path",
    "save_json",
    "setup_path",
    "str_to_path",
    "write_lines",
)
from .classes import LockableDict, LockableList, ObjectSaver, OtsuNone, Timer
from .funcs import (
    deduplicate,
    load_json,
    read_lines,
    same_path,
    save_json,
    setup_path,
    str_to_path,
    write_lines,
)
from .types import FLOAT_INT, K, P, R, T, V, hmsValue, pathLike
