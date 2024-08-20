from __future__ import annotations

import warnings
from typing import Any, List, Union, Tuple

from tcod._internal import deprecate
from tcod.cffi import lib


class Color(List[int]):
    """Extended libtcodpy color class with optional alpha channel.

    Args:
        r (int): Red value, from 0 to 255.
        g (int): Green value, from 0 to 255.
        b (int): Blue value, from 0 to 255.
        a (int, optional): Alpha value, from 0 to 255. Defaults to 255 (fully opaque).
    """

    def __init__(self, r: int = 0, g: int = 0, b: int = 0, a: int = 255) -> None:
        super().__init__([r & 0xFF, g & 0xFF, b & 0xFF, a & 0xFF])

    @property
    def r(self) -> int:
        """int: Red value, always normalized to 0-255.

        .. deprecated:: 9.2
            Color attributes will not be mutable in the future.
        """
        return self[0]

    @r.setter
    @deprecate("Setting color attributes has been deprecated.", FutureWarning)
    def r(self, value: int) -> None:
        self[0] = value & 0xFF

    @property
    def g(self) -> int:
        """int: Green value, always normalized to 0-255.

        .. deprecated:: 9.2
            Color attributes will not be mutable in the future.
        """
        return self[1]

    @g.setter
    @deprecate("Setting color attributes has been deprecated.", FutureWarning)
    def g(self, value: int) -> None:
        self[1] = value & 0xFF

    @property
    def b(self) -> int:
        """int: Blue value, always normalized to 0-255.

        .. deprecated:: 9.2
            Color attributes will not be mutable in the future.
        """
        return self[2]

    @b.setter
    @deprecate("Setting color attributes has been deprecated.", FutureWarning)
    def b(self, value: int) -> None:
        self[2] = value & 0xFF

    @property
    def a(self) -> int:
        """int: Alpha value, always normalized to 0-255."""
        return self[3]

    @a.setter
    @deprecate("Setting color attributes has been deprecated.", FutureWarning)
    def a(self, value: int) -> None:
        self[3] = value & 0xFF

    @classmethod
    def _new_from_cdata(cls, cdata: Any) -> Color:  # noqa: ANN401
        return cls(cdata.r, cdata.g, cdata.b, getattr(cdata, "a", 255))

    def __getitem__(self, index: Union[int, str, slice]) -> Any:
        """Return a color channel.

        .. deprecated:: 9.2
            Accessing colors via a letter index is deprecated.
        """
        if isinstance(index, str):
            warnings.warn(
                "Accessing colors via a letter index is deprecated",
                DeprecationWarning,
                stacklevel=2,
            )
            return super().__getitem__("rgba".index(index))
        return super().__getitem__(index)

    @deprecate("This class will not be mutable in the future.", FutureWarning)
    def __setitem__(self, index: Union[int, str, slice], value: Any) -> None:
        if isinstance(index, str):
            super().__setitem__("rgba".index(index), value & 0xFF)
        else:
            super().__setitem__(index, value)

    def __eq__(self, other: Any) -> bool:
        """Compare equality between colors.

        Also compares with standard sequences such as 3-item or 4-item tuples or lists.
        """
        if not isinstance(other, (Color, list, tuple)):
            return NotImplemented
        return len(self) == len(other) and all(a == b for a, b in zip(self, other))

    @deprecate("Use NumPy instead for color math operations.", FutureWarning)
    def __add__(self, other: Union[Color, List[int], Tuple[int, ...]]) -> Color:
        """Add two colors together.

        .. deprecated:: 9.2
            Use NumPy instead for color math operations.
        """
        if not isinstance(other, (Color, list, tuple)):
            return NotImplemented
        r = min(self.r + other[0], 255)
        g = min(self.g + other[1], 255)
        b = min(self.b + other[2], 255)
        a = min(self.a + (other[3] if len(other) > 3 else 255), 255)
        return Color(r, g, b, a)

    @deprecate("Use NumPy instead for color math operations.", FutureWarning)
    def __sub__(self, other: Union[Color, List[int], Tuple[int, ...]]) -> Color:
        """Subtract one color from another.

        .. deprecated:: 9.2
            Use NumPy instead for color math operations.
        """
        if not isinstance(other, (Color, list, tuple)):
            return NotImplemented
        r = max(self.r - other[0], 0)
        g = max(self.g - other[1], 0)
        b = max(self.b - other[2], 0)
        a = max(self.a - (other[3] if len(other) > 3 else 0), 0)
        return Color(r, g, b, a)

    @deprecate("Use NumPy instead for color math operations.", FutureWarning)
    def __mul__(
        self, other: Union[Color, List[int], Tuple[int, ...], float, int]
    ) -> Color:
        """Multiply with a scalar or another color.

        .. deprecated:: 9.2
            Use NumPy instead for color math operations.
        """
        if isinstance(other, (Color, list, tuple)):
            r = min(int(self.r * other[0] / 255), 255)
            g = min(int(self.g * other[1] / 255), 255)
            b = min(int(self.b * other[2] / 255), 255)
            a = min(int(self.a * (other[3] if len(other) > 3 else 255) / 255), 255)
        elif isinstance(other, (int, float)):
            r = min(int(self.r * other), 255)
            g = min(int(self.g * other), 255)
            b = min(int(self.b * other), 255)
            a = min(int(self.a * other), 255)
        else:
            return NotImplemented
        return Color(r, g, b, a)

    def __repr__(self) -> str:
        """Return a printable representation of the current color."""
        return f"{self.__class__.__name__}({self.r}, {self.g}, {self.b}, {self.a})"
