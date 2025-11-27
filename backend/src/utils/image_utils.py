# decode/encode helpers for images used by the pipeline
import cv2
import numpy as np
from typing import Tuple
import io

def decode_image(image_bytes: bytes) -> np.ndarray:
    """
    Decode bytes (JPEG/PNG) into OpenCV BGR ndarray.
    """
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Failed to decode image bytes")
    return img


def encode_image_to_jpeg_bytes(image: np.ndarray, quality: int = 90) -> bytes:
    """
    Encode BGR ndarray to JPEG bytes.
    """
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    success, buffer = cv2.imencode('.jpg', image, encode_params)
    if not success:
        raise ValueError("Failed to encode image to JPEG")
    return buffer.tobytes()


def resize_image_max(image: np.ndarray, max_dim: int = 1600) -> np.ndarray:
    """
    Resize image preserving aspect ratio so that the longer side <= max_dim.
    If image already smaller, returns as-is.
    """
    h, w = image.shape[:2]
    max_side = max(h, w)
    if max_side <= max_dim:
        return image
    scale = max_dim / float(max_side)
    new_w = int(w * scale)
    new_h = int(h * scale)
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return resized