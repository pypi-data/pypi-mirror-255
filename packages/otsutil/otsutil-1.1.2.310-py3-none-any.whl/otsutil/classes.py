"""よく使うクラスを纏めたモジュールです。
"""

__all__ = (
    "LockableDict",
    "LockableList",
    "ObjectSaver",
    "OtsuNone",
    "Timer",
)
import base64
import pickle
import time

from collections.abc import Iterator
from datetime import datetime, timedelta
from threading import Lock
from typing import Callable, Generic, Iterator, Literal, Type, overload

from _collections_abc import dict_items, dict_keys, dict_values

from .funcs import setup_path
from .types import K, P, R, T, V, hmsValue, pathLike


class __OtsuNoneType:
    """Noneが返るのが正常な場合など、異常なNoneを表す場合に使用するクラス。"""

    __instance = None

    def __new__(cls) -> "__OtsuNoneType":
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __repr__(self) -> str:
        return "OtsuNone"

    def __bool__(self) -> bool:
        return False


OtsuNone = __OtsuNoneType()


class LockableDict(dict[K, V]):
    """要素の操作時にthreading.Lockを使用するdictクラス。

    items, keys, valuesなど、途中でRuntimeErrorを起こす可能性のあるメソッドの結果は、safe_{}というメソッドを使用することでtupleまたはlistとして安全に取得できます。
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__lock = Lock()
        attrs = (
            "clear",
            "copy",
            "fromkeys",
            "get",
            "items",
            "keys",
            "pop",
            "popitem",
            "setdefault",
            "update",
            "values",
        )
        for attr in attrs:
            if (value := getattr(self, attr, None)) is not None:
                setattr(self, attr, self.with_lock(value))

    def __delitem__(self, __key: K) -> None:
        with self.__lock:
            res = super().__delitem__(__key)
            return res

    def __getitem__(self, __key: K) -> V:
        with self.__lock:
            res = super().__getitem__(__key)
            return res

    def __setitem__(self, __key: K, __value: V) -> None:
        with self.__lock:
            res = super().__setitem__(__key, __value)
            return res

    @overload
    def safe_items(self, type_: Type[list]) -> list[tuple[K, V]]: ...

    @overload
    def safe_items(self, type_: Type[tuple]) -> tuple[tuple[K, V], ...]: ...

    @overload
    def safe_items(self) -> tuple[tuple[K, V], ...]: ...

    def safe_items(self, type_: Type[list] | Type[tuple] = tuple) -> list[tuple[K, V]] | tuple[tuple[K, V], ...]:
        """itemsの結果をtype_型にして返す。

        Args:
            type_ (Type[list] | Type[tuple], optional): 戻り値の型。 Defaults to tuple.

        Raises:
            ValueError: type_引数がlist, tuple以外の場合に投げられる。

        Returns:
            list[tuple[K, V]] | tuple[tuple[K, V], ...]: itemsの結果。
        """
        if type_ is list:
            f = list
        elif type_ is tuple:
            f = tuple
        else:
            msg = "type_は[list, tuple]のいずれかである必要があります。"
            raise ValueError(msg)
        with self.__lock:
            return f(super().items())

    @overload
    def safe_keys(self, type_: Type[list]) -> list[K]: ...

    @overload
    def safe_keys(self, type_: Type[tuple]) -> tuple[K, ...]: ...

    @overload
    def safe_keys(self) -> tuple[K, ...]: ...

    def safe_keys(self, type_: Type[list] | Type[tuple] = tuple) -> list[K] | tuple[K, ...]:
        """keysの結果をtype_型にして返す。

        Args:
            type_ (Type[list] | Type[tuple], optional): 戻り値の型。 Defaults to tuple.

        Raises:
            ValueError: type_引数がlist, tuple以外の場合に投げられる。

        Returns:
            list[K] | tuple[K, ...]: keysの結果。
        """
        if type_ is list:
            f = list
        elif type_ is tuple:
            f = tuple
        else:
            msg = "type_は[list, tuple]のいずれかである必要があります。"
            raise ValueError(msg)
        with self.__lock:
            return f(super().keys())

    @overload
    def safe_values(self, type_: Type[list]) -> list[V]: ...

    @overload
    def safe_values(self, type_: Type[tuple]) -> tuple[V, ...]: ...

    @overload
    def safe_values(self) -> tuple[V, ...]: ...

    def safe_values(self, type_: Type[list] | Type[tuple] = tuple) -> list[V] | tuple[V, ...]:
        """valuesの結果をtype_型にして返す。

        Args:
            type_ (Type[list] | Type[tuple], optional): 戻り値の型。 Defaults to tuple.

        Raises:
            ValueError: type_引数がlist, tuple以外の場合に投げられる。

        Returns:
            list[V] | tuple[V, ...]: valuesの結果。
        """
        if type_ is list:
            f = list
        elif type_ is tuple:
            f = tuple
        else:
            msg = "type_は[list, tuple]のいずれかである必要があります。"
            raise ValueError(msg)
        with self.__lock:
            return f(super().values())

    def with_lock(self, f: Callable[P, R]) -> Callable[P, R]:

        def _(*args: P.args, **kwargs: P.kwargs) -> R:
            with self.__lock:
                res = f(*args, **kwargs)
                return res

        return _


class LockableList(list[V]):
    """要素の操作時にthreading.Lockを使用するlistクラス。"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__lock = Lock()
        attrs = (
            "append",
            "clear",
            "copy",
            "count",
            "extend",
            "index",
            "insert",
            "pop",
            "remove",
            "reverse",
            "sort",
        )
        for attr in attrs:
            if (value := getattr(self, attr, None)) is not None:
                setattr(self, attr, self.with_lock(value))

    def with_lock(self, f: Callable[P, R]) -> Callable[P, R]:

        def _(*args: P.args, **kwargs: P.kwargs) -> R:
            with self.__lock:
                res = f(*args, **kwargs)
            return res

        return _


class ObjectSaver(Generic[T]):
    """オブジェクトを保存するファイルを扱うクラス。

    Properties:
        obj (T | None): ファイルに保存されているオブジェクト。
    """

    def __init__(self, file: pathLike) -> None:
        self.__file = setup_path(file)
        if self.__file.exists():
            obj = self.load_file()
        else:
            obj = None
        self.__obj = obj

    @staticmethod
    def dumps(obj: T | None) -> str:
        """オブジェクトのpickle文字列を返します。

        Args:
            obj (T | None): pickle文字列を取得したいオブジェクト。

        Returns:
            str: pickle文字列。
        """
        otb = pickle.dumps(obj, protocol=4)
        return base64.b64encode(otb).decode("utf-8")

    @staticmethod
    def loads(pickle_str: str) -> T | None:
        """pickle文字列をオブジェクト化します。

        Args:
            pickle_str (str): pickle文字列。

        Returns:
            T | None: 復元されたオブジェクト。
        """
        if not pickle_str:
            return None
        stb = base64.b64decode(pickle_str.encode())
        return pickle.loads(stb)

    def load_file(self) -> T | None:
        """ファイルに保存されているデータを読み込み、取得します。

        ファイルが存在しなかった場合にはNoneを保存したファイルを生成し、Noneを返します。

        Returns:
            T | None: ファイルに保存されていたオブジェクト。
        """
        file = self.__file
        if file.exists():
            with file.open("r", encoding="utf-8") as f:
                return self.loads(f.read())
        else:
            self.save_file(None)
        return None

    def save_file(self, obj: T | None) -> bool:
        """ファイルにobjを保存し、成否を返します。

        また、obj属性を更新します。

        Args:
            obj (T | None): 保存したいオブジェクト。

        Returns:
            bool: 保存の成否。
        """
        try:
            bts = self.dumps(obj)
            with self.__file.open("w", encoding="utf-8") as f:
                f.write(bts)
            self.__obj = obj
            return True
        except:
            return False

    @property
    def obj(self) -> T | None:
        """ファイルに保存されているオブジェクト。

        新規ファイルでインスタンス生成した場合の初期値はNoneになります。
        """
        return self.__obj


class Timer:
    """指定時間が経過したかを判定したり指定時間秒処理を停止させるタイマーのクラス。

    Properties:
        delta (timedelta): インスタンスの基準待機時間です。
        start_time (datetime): タイマーを開始した時刻です。
        target_time (datetime): タイマーを終了する時刻です。
    """

    def __init__(self, hours: int = 0, minutes: int = 0, seconds: float = 0) -> None:
        """h時間m分s秒を測るタイマーインスタンスを生成します。

        Args:
            hours (int, optional): h時間 Defaults to 0.
            minutes (int, optional): m分。 Defaults to 0.
            seconds (float, optional): s秒。 Defaults to 0.

        Raises:
            ValueError: マイナス秒になるような時間が指定されている場合に投げられる。
        """
        delta = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        if delta < timedelta(seconds=0):
            msg = f"0秒未満のTimerインスタンスを生成することはできません。 ({delta.total_seconds():0.2f}秒)"
            raise ValueError(msg)
        self.__delta = delta
        self.reset()

    def __bool__(self) -> bool:
        return self.target_time > datetime.now()

    def __str__(self) -> str:
        hms = self.calc_hms(self.delta.total_seconds())
        res = []
        for i, s in zip(hms, ("時間", "分", "秒")):
            if i > 0:
                res.append(f"{i}{s}")
        return "".join(res) + "のタイマーです。"

    @staticmethod
    def calc_hms(seconds: float) -> hmsValue:
        """秒数から時分秒のタプルを返します。

        Args:
            seconds (float): 秒数。

        Returns:
            hmsValue: 時分秒のタプル。
        """
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        h, m = map(int, (h, m))
        return (h, m, s)

    def begin(self, span_seconds: float = 0) -> None:
        """現在から指定時間秒待機します。

        Args:
            span_seconds (float, optional): 待機終了を確認する頻度秒。 Defaults to 0.
        """
        self.reset()
        self.join(span_seconds)

    def join(self, span_seconds: float = 0) -> None:
        """開始時刻から指定時間秒経過するまで待機します。

        Timer.beginと違い、インスタンス生成やTimer.resetからの経過時間に応じて待機時間が減少します。

        Args:
            span_seconds (float, optional): 待機終了を確認する頻度秒。 Defaults to 0.
        """
        span = min(0, span_seconds)
        while self:
            time.sleep(span)

    def reset(self) -> None:
        """タイマーの開始時刻をリセットし、終了時刻を更新します。"""
        self.__start_time = datetime.now()
        self.__target_time = self.start_time + self.delta

    def wiggle_begin(self) -> Iterator[hmsValue]:
        """待機時間を確認後に処理を挟むことのできるTimer.beginです。

        for文などと合わせて使うことができます。

        Yields:
            Iterator[hmsValue]: 指定時刻までの残り時分秒のタプル。
        """
        self.reset()
        yield from self.wiggle_join()

    def wiggle_join(self) -> Iterator[hmsValue]:
        """待機時間を確認後に処理を挟むことのできるTimer.joinです。

        for文などと合わせて使うことができます。

        Yields:
            Iterator[hmsValue]: 指定時刻までの残り時分秒のタプル。
        """
        while self:
            delta = self.target_time - datetime.now()
            yield self.calc_hms(delta.total_seconds())

    @property
    def delta(self) -> timedelta:
        """インスタンスの基準待機時間です。"""
        return self.__delta

    @property
    def start_time(self) -> datetime:
        """タイマーを開始した時刻です。

        この時刻を基準にdelta秒経過したかを判定します。
        インスタンス生成時、またはTimer.begin, Timer.resetメソッドを呼び出した場合にこの属性が更新されます。
        """
        return self.__start_time

    @property
    def target_time(self) -> datetime:
        """タイマーを終了する時刻です。

        インスタンス生成時、またはTimer.begin, Timer.resetメソッドを呼び出した場合にこの属性が更新されます。
        """
        return self.__target_time
