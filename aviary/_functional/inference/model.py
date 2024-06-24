import numpy as np
import numpy.typing as npt
import onnxruntime as ort

# noinspection PyProtectedMember
from aviary._utils.exceptions import AviaryUserError
# noinspection PyProtectedMember
from aviary._utils.types import (
    BufferSize,
    Device,
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
    buffer_size: BufferSize,
) -> npt.NDArray:
    """Runs the model.

    Parameters:
        model: ONNX model
        model_input_name: name of the model input
        model_output_name: name of the model output
        inputs: batched inputs
        buffer_size: buffer size in pixels (specifies the area around the tile that is additionally fetched)

    Returns:
        batched predictions
    """
    preds = model.run([model_output_name], {model_input_name: inputs})
    preds = np.array(preds)
    preds = np.squeeze(preds, axis=0)

    if buffer_size > 0:
        preds = _remove_buffer(
            preds=preds,
            buffer_size=buffer_size,
        )

    preds = np.argmax(preds, axis=-1).astype(np.uint8)
    return preds


def _remove_buffer(
    preds: npt.NDArray,
    buffer_size: BufferSize,
) -> npt.NDArray:
    """Removes the buffer.

    Parameters:
        preds: batched predictions
        buffer_size: buffer size in pixels (specifies the area around the tile that is additionally fetched)

    Returns:
        batched predictions without the buffer
    """
    return preds[
        :,
        buffer_size:-buffer_size,
        buffer_size:-buffer_size,
        :,
    ]
