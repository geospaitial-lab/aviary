#  Copyright (C) 2026 Marius Maryniak
#
#  This file is part of aviary.
#
#  aviary is free software: you can redistribute it and/or modify it under the terms of the
#  GNU General Public License as published by the Free Software Foundation,
#  either version 3 of the License, or (at your option) any later version.
#
#  aviary is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with aviary.
#  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

from aviary._utils.lifecycle import experimental
from aviary.core.mixins import IDMixin


@experimental(
    since='1.9.0',
)
class Object(IDMixin):
    """An object specifies its spatial extent."""

    __hash__ = None

    def __init__(
        self,
        label: int | str,
        x_center: float,
        y_center: float,
        width: float,
        height: float,
        rotation: float | None = None,
        confidence: float | None = None,
    ) -> None:
        """
        Parameters:
            label: Label
            x_center: Center x coordinate in meters
            y_center: Center y coordinate in meters
            width: Width in meters
            height: Height in meters
            rotation: Rotation in radians
            confidence: Confidence
        """
        self._label = label
        self._x_center = x_center
        self._y_center = y_center
        self._width = width
        self._height = height
        self._rotation = rotation
        self._confidence = confidence

        super().__init__()

    @property
    def label(self) -> int | str:
        """
        Returns:
            Label
        """
        return self._label

    @property
    def x_center(self) -> float:
        """
        Returns:
            Center x coordinate in meters
        """
        return self._x_center

    @property
    def y_center(self) -> float:
        """
        Returns:
            Center y coordinate in meters
        """
        return self._y_center

    @property
    def width(self) -> float:
        """
        Returns:
            Width in meters
        """
        return self._width

    @property
    def height(self) -> float:
        """
        Returns:
            Height in meters
        """
        return self._height

    @property
    def rotation(self) -> float:
        """
        Returns:
            Rotation in radians
        """
        return self._rotation

    @property
    def confidence(self) -> float | None:
        """
        Returns:
            Confidence
        """
        return self._confidence

    @property
    def area(self) -> float:
        """
        Returns:
            Area in square meters
        """
        return self._width * self._height

    def __repr__(self) -> str:
        """Returns the string representation.

        Returns:
            String representation
        """
        return (
            'Object(\n'
            f'    label={self._label},\n'
            f'    x_center={self._x_center},\n'
            f'    y_center={self._y_center},\n'
            f'    width={self._width},\n'
            f'    height={self._height},\n'
            f'    rotation={self._rotation},\n'
            f'    confidence={self._confidence},\n'
            ')'
        )

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """Compares the objects.

        Parameters:
            other: Other object

        Returns:
            True if the objects are equal, False otherwise
        """
        if not isinstance(other, Object):
            return False

        conditions = [
            self._label == other.label,
            self._x_center == other.x_center,
            self._y_center == other.y_center,
            self._width == other.width,
            self._height == other.height,
            self._rotation == other.rotation,
            self._confidence == other.confidence,
        ]
        return all(conditions)
