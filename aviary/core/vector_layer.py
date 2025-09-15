from __future__ import annotations

import weakref
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import geopandas as gpd

# noinspection PyProtectedMember
from aviary._utils.validators import validate_layer_name

if TYPE_CHECKING:
    from aviary.core.vector import Vector


class VectorLayer:
    """Layer that contains vector data

    Notes:
        - The `data` property returns a reference to the data
        - The `metadata` property returns a reference to the metadata
    """
    __hash__ = None

    def __init__(
        self,
        data: gpd.GeoDataFrame,
        name: str,
        metadata: dict[str, object] | None = None,
        copy: bool = False,
    ) -> None:
        """
        Parameters:
            data: Data
            name: Name
            metadata: Metadata
            copy: If True, the data and metadata are copied during initialization
        """
        self._data = data
        self._name = name
        self._metadata = {} if metadata is None else metadata
        self._copy = copy

        self._validate()

        if self._copy:
            self._copy_data()
            self._copy_metadata()

        self._observer_vector = None

    def _validate(self) -> None:
        """Validates the layer."""
        validate_layer_name(
            channel_name=self._name,
            param='name',
            description='name',
        )

    def _copy_data(self) -> None:
        """Copies `data`."""
        self._data = self._data.copy()

    def _copy_metadata(self) -> None:
        """Copies `metadata`."""
        self._metadata = self._metadata.copy()

    def _register_observer_vector(
        self,
        observer_vector: Vector,
    ) -> None:
        """Registers the observer vector.

        Parameters:
            observer_vector: Observer vector
        """
        self._observer_vector = weakref.ref(observer_vector)

    def _unregister_observer_vector(self) -> None:
        """Unregisters the observer vector."""
        self._observer_vector = None

    @property
    def data(self) -> gpd.GeoDataFrame:
        """
        Returns:
            Data
        """
        return self._data

    @property
    def name(self) -> str:
        """
        Returns:
            Name
        """
        return self._name

    @name.setter
    def name(
        self,
        name: str,
    ) -> None:
        """
        Parameters:
            name: Name
        """
        self._name = name
        validate_layer_name(
            channel_name=self._name,
            param='name',
            description='name',
        )

        if self._observer_vector is None:
            return

        observer_vector = self._observer_vector()

        if observer_vector is None:
            return

        # noinspection PyProtectedMember
        observer_vector._validate()  # noqa: SLF001

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
            If True, the data and metadata are copied during initialization
        """
        return self._copy

    @property
    def is_in_vector(self) -> bool:
        """
        Returns:
            True if the layer is inside vector, False otherwise
        """
        if self._observer_vector is None:
            return False

        return self._observer_vector() is not None

    def __repr__(self) -> str:
        """Returns the string representation.

        Returns:
            String representation
        """
        data_repr = len(self._data)
        return (
            'VectorLayer(\n'
            f'    data={data_repr},\n'
            f'    name={self._name},\n'
            f'    metadata={self._metadata},\n'
            f'    copy={self._copy},\n'
            ')'
        )

    def __getstate__(self) -> dict:
        """Gets the state for pickling.

        Returns:
            State
        """
        state = self.__dict__.copy()
        state['_observer_vector'] = None
        return state

    def __setstate__(
        self,
        state: dict,
    ) -> None:
        """Sets the state for unpickling.

        Parameters:
            state: State
        """
        self.__dict__ = state
