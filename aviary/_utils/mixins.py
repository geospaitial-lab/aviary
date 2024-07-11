from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pydantic


class FromConfigMixin:
    """Mixin for classes that can be created from a configuration"""

    @classmethod
    def from_config(
        cls,
        config: pydantic.BaseModel,
    ) -> FromConfigMixin:
        """Creates an instance of the class from a configuration.

        Parameters:
            config: configuration

        Returns:
            instance of the class
        """
        config = config.model_dump()
        # noinspection PyArgumentList
        return cls(**config)
