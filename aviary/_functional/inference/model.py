import numpy as np
import numpy.typing as npt
import onnxruntime as ort

from aviary.core.exceptions import AviaryUserError

# noinspection PyProtectedMember
from aviary._utils.types import (
    BufferSize,
    Device,
    GroundSamplingDistance,
)


def get_providers(
    device: Device,
) -> list[str]:
    """Returns the ONNX providers.

    Parameters:
        device: device (`CPU` or `CUDA`)

    Returns:
        ONNX providers

    Raises:
        AviaryUserError: Invalid device
    """
    if device == Device.CPU:
        return ['CPUExecutionProvider']

    if device == Device.CUDA:
        return ['CUDAExecutionProvider', 'CPUExecutionProvider']

    message = 'Invalid device!'
    raise AviaryUserError(message)


def onnx_segmentation_model(
    model: ort.InferenceSession,
    model_input_name: str,
    model_output_name: str,
    inputs: npt.NDArray,
    ground_sampling_distance: GroundSamplingDistance,
    buffer_size: BufferSize = 0,
) -> npt.NDArray:
    """Runs the model.

    Parameters:
        model: ONNX model
        model_input_name: name of the model input
        model_output_name: name of the model output
        inputs: batched inputs
        ground_sampling_distance: ground sampling distance in meters
        buffer_size: buffer size in meters (specifies the area around the tile that is additionally fetched)

    Returns:
        batched predictions
    """
    preds = model.run([model_output_name], {model_input_name: inputs})
    preds = np.array(preds)
    preds = np.squeeze(preds, axis=0)

    if buffer_size > 0:
        buffer_size_pixels = _compute_buffer_size_pixels(
            buffer_size=buffer_size,
            ground_sampling_distance=ground_sampling_distance,
        )
        preds = _remove_buffer(
            preds=preds,
            buffer_size=buffer_size_pixels,
        )

    return np.argmax(preds, axis=-1).astype(np.uint8)


def _compute_buffer_size_pixels(
    buffer_size: BufferSize,
    ground_sampling_distance: GroundSamplingDistance,
) -> int:
    """Computes the buffer size in pixels.

    Parameters:
        buffer_size: buffer size in meters (specifies the area around the tile that is additionally fetched)
        ground_sampling_distance: ground sampling distance in meters

    Returns:
        buffer size in pixels
    """
    return int(buffer_size / ground_sampling_distance)


def _remove_buffer(
    preds: npt.NDArray,
    buffer_size: BufferSize,
) -> npt.NDArray:
    """Removes the buffer.

    Parameters:
        preds: batched predictions
        buffer_size: buffer size in pixels (specifies the area around the tile that is additionally fetched)

    Returns:
        batched predictions
    """
    return preds[
        :,
        buffer_size:-buffer_size,
        buffer_size:-buffer_size,
        :,
    ]
