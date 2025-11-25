#  Copyright (C) 2024-2025 Marius Maryniak
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

from collections.abc import (
    Iterable,
    Iterator,
)

from aviary.core.enums import _coerce_layer_names
from aviary.core.exceptions import AviaryUserError
from aviary.core.vector_layer import (
    VectorLayer,
)


class Vector(Iterable[VectorLayer]):
    """The vector specifies the layers.

    Notes:
        - The `layers` property returns a reference to the layers
        - The `metadata` property returns a reference to the metadata
        - The dunder methods `__getattr__`, `__getitem__`, and `__iter__` return or yield a reference to a layer
    """
    __hash__ = None

    def __init__(
        self,
        layers: list[VectorLayer],
        metadata: dict[str, object] | None = None,
        copy: bool = False,
    ) -> None:
        """
        Parameters:
            layers: Layers
            metadata: Metadata
            copy: If True, the layers and metadata are copied during initialization
        """
        self._layers = layers
        self._layers_dict = None
        self._metadata = {} if metadata is None else metadata
        self._copy = copy

        self._validate()

        if self._copy:
            self._copy_layers()
            self._copy_metadata()

        for layer in self:
            # noinspection PyProtectedMember
            layer._register_observer_vector(observer_vector=self)  # noqa: SLF001

    def _validate(self) -> None:
        """Validates the vector."""
        self._validate_layers()
        self._invalidate_cache()

    def _validate_layers(self) -> None:
        """Validates `layers`.

        Raises:
            AviaryUserError: Invalid `layers` (the layers contain duplicate layer names)
        """
        if not self:
            return

        layer_names = [layer.name for layer in self]
        unique_layer_names = set(layer_names)

        if len(layer_names) != len(unique_layer_names):
            message = (
                'Invalid layers! '
                'The layers must contain unique layer names.'
            )
            raise AviaryUserError(message)

    def _copy_layers(self) -> None:
        """Copies `layers`."""
        self._layers = [layer.copy() for layer in self]

    def _copy_metadata(self) -> None:
        """Copies `metadata`."""
        self._metadata = self._metadata.copy()

    def _invalidate_cache(self) -> None:
        """Invalidates the cache."""
        self._layers_dict = None

    @property
    def layers(self) -> list[VectorLayer]:
        """
        Returns:
            Layers
        """
        return self._layers

    @property
    def metadata(self) -> dict[str, object]:
        """
        Returns:
            Metadata
        """
        return self._metadata

    @metadata.setter
    def metadata(
        self,
        metadata: dict[str, object] | None,
    ) -> None:
        """
        Parameters:
            metadata: Metadata
        """
        self._metadata = metadata

    @property
    def is_copied(self) -> bool:
        """
        Returns:
            If True, the layers and metadata are copied during initialization
        """
        return self._copy

    @property
    def layer_names(self) -> set[str]:
        """
        Returns:
            Layer names
        """
        return {layer.name for layer in self}

    @classmethod
    def from_vectors(
        cls,
        vectors: list[Vector],
        copy: bool = False,
    ) -> Vector:
        """Creates vector from vectors.

        Parameters:
            vectors: Vectors
            copy: If True, the layers and metadata are copied during initialization

        Returns:
            Vector

        Raises:
            AviaryUserError: Invalid `vectors` (the vectors contain no vectors)
        """
        if not vectors:
            message = (
                'Invalid vectors! '
                'The vectors must contain at least one vector.'
            )
            raise AviaryUserError(message)

        layers = [layer for vector in vectors for layer in vector]
        metadata: dict[str, object] = {}

        for vector in vectors:
            metadata.update(vector.metadata)

        return cls(
            layers=layers,
            metadata=metadata,
            copy=copy,
        )

    def __repr__(self) -> str:
        """Returns the string representation.

        Returns:
            String representation
        """
        if self:
            layers_repr = '\n'.join(
                f'        {layer.name}: {type(layer).__name__},'
                for layer in self
            )
            layers_repr = '\n' + layers_repr
        else:
            layers_repr = ','

        return (
            'Vector(\n'
            f'    layers={layers_repr}\n'
            f'    metadata={self._metadata},\n'
            f'    copy={self._copy},\n'
            ')'
        )

    def __getstate__(self) -> dict:
        """Gets the state for pickling.

        Returns:
            State
        """
        return self.__dict__

    def __setstate__(
        self,
        state: dict,
    ) -> None:
        """Sets the state for unpickling.

        Parameters:
            state: State
        """
        self.__dict__ = state

        for layer in self:
            # noinspection PyProtectedMember
            layer._register_observer_vector(observer_vector=self)  # noqa: SLF001

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """Compares the vectors.

        Parameters:
            other: Other vector

        Returns:
            True if the vectors are equal, False otherwise
        """
        if not isinstance(other, Vector):
            return False

        conditions = [
            self._layers == other.layers,
            self._metadata == other.metadata,
        ]
        return all(conditions)

    def __len__(self) -> int:
        """Computes the number of layers.

        Returns:
            Number of layers
        """
        return len(self._layers)

    def __bool__(self) -> bool:
        """Checks if the vector contains layers.

        Returns:
            True if the vector contains layers, False otherwise
        """
        return bool(len(self))

    def __contains__(
        self,
        layer_name: str,
    ) -> bool:
        """Checks if the layer is in the vector.

        Parameters:
            layer_name: Layer name

        Returns:
            True if the layer is in the vector, False otherwise
        """
        return layer_name in self.layer_names

    def __getattr__(
        self,
        layer_name: str,
    ) -> VectorLayer:
        """Returns the layer.

        Parameters:
            layer_name: Layer name

        Returns:
            Layer
        """
        try:
            return self[layer_name]
        except KeyError as error:
            raise AttributeError from error

    def __getitem__(
        self,
        layer_name: str,
    ) -> VectorLayer:
        """Returns the layer.

        Parameters:
            layer_name: Layer name

        Returns:
            Layer
        """
        if self._layers_dict is None:
            self._layers_dict = {layer.name: layer for layer in self}

        return self._layers_dict[layer_name]

    def __iter__(self) -> Iterator[VectorLayer]:
        """Iterates over the layers.

        Yields:
            Layer
        """
        yield from self._layers

    def __add__(
        self,
        other: Vector,
    ) -> Vector:
        """Adds the vectors.

        Parameters:
            other: Other vector

        Returns:
            Vector
        """
        layers = self._layers + other.layers
        metadata: dict[str, object] = {}
        metadata.update(self._metadata)
        metadata.update(other.metadata)
        return Vector(
            layers=layers,
            metadata=metadata,
            copy=True,
        )

    def append(
        self,
        layers: VectorLayer | list[VectorLayer],
        inplace: bool = False,
    ) -> Vector:
        """Appends the layers.

        Parameters:
            layers: Layers
            inplace: If True, the layers are appended inplace

        Returns:
            Vector
        """
        if not isinstance(layers, list):
            layers = [layers]

        if inplace:
            self._layers.extend(layers)
            self._validate()

            for layer in layers:
                # noinspection PyProtectedMember
                layer._register_observer_vector(observer_vector=self)  # noqa: SLF001

            return self

        layers = self._layers + layers
        return Vector(
            layers=layers,
            metadata=self._metadata,
            copy=True,
        )

    def copy(self) -> Vector:
        """Copies the vector.

        Returns:
            Vector
        """
        return Vector(
            layers=self._layers,
            metadata=self._metadata,
            copy=True,
        )

    def remove(
        self,
        layer_names: str | set[str] | bool | None = True,
        inplace: bool = False,
    ) -> Vector:
        """Removes the layers.

        Parameters:
            layer_names: Layer name, layer names, no layers (False or None), or all layers (True)
            inplace: If True, the layers are removed inplace

        Returns:
            Vector
        """
        layer_names = _coerce_layer_names(layer_names=layer_names)

        if layer_names is True:
            layer_names = self.layer_names

        layer_names = self.layer_names - layer_names
        return self.select(
            layer_names=layer_names,
            inplace=inplace,
        )

    def select(
        self,
        layer_names: str | set[str] | bool | None = True,
        inplace: bool = False,
    ) -> Vector:
        """Selects the layers.

        Parameters:
            layer_names: Layer name, layer names, no layers (False or None), or all layers (True)
            inplace: If True, the layers are selected inplace

        Returns:
            Vector
        """
        layer_names = _coerce_layer_names(layer_names=layer_names)

        if layer_names is True:
            layer_names = self.layer_names

        if inplace:
            removed_layer_names = self.layer_names - layer_names
            removed_layers = [layer for layer in self if layer.name in removed_layer_names]
            self._layers = [layer for layer in self if layer.name in layer_names]
            self._validate()

            for layer in removed_layers:
                # noinspection PyProtectedMember
                layer._unregister_observer_vector()  # noqa: SLF001

            return self

        layers = [layer for layer in self if layer.name in layer_names]
        return Vector(
            layers=layers,
            metadata=self._metadata,
            copy=True,
        )
