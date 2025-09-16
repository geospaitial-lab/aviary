from __future__ import annotations

from collections.abc import (
    Iterable,
)

from aviary.core.exceptions import AviaryUserError
from aviary.core.vector_layer import (
    VectorLayer,
)


class Vector(Iterable[VectorLayer]):
    """TODO

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
