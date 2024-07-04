import numpy as np
import numpy.typing as npt

# noinspection PyProtectedMember
from aviary._utils.types import Coordinate


def collate_batch(
    samples: list[tuple[npt.NDArray, Coordinate, Coordinate]],
) -> tuple[npt.NDArray, npt.NDArray, npt.NDArray]:
    """Collates the list of samples into a batch.

    Notes:
        - A sample contains the data, the minimum x coordinate and the minimum y coordinate of a tile
        - A batch contains the data, the minimum x coordinates and the minimum y coordinates of a batch of tiles

    Parameters:
        samples: list of samples

    Returns:
        batch
    """
    data = np.array(
        [sample[0] for sample in samples],
        dtype=np.float32,
    )
    x_min = np.array(
        [sample[1] for sample in samples],
        dtype=np.int32,
    )
    y_min = np.array(
        [sample[2] for sample in samples],
        dtype=np.int32,
    )
    return data, x_min, y_min
