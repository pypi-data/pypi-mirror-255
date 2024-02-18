from pathlib import Path
import numpy as np
from imageio.v3 import imread, immeta, imwrite

from .base import check_mime


IMAGE_ALLOWED_MIME = [
    "image/jpeg",
    "image/png"
]

GREYSCALE_8BIT_MODE = "L"
RGB_8BIT_MODE = "RGB"


def get_image_metadata(file_path: Path) -> dict:
    mime = check_mime(file_path, IMAGE_ALLOWED_MIME)
    img = immeta(file_path)
    mode = img['mode']
    if mode not in [GREYSCALE_8BIT_MODE, RGB_8BIT_MODE]:
        raise ValueError(f"Mode \"{mode}\" not taken into account")
    return {
        "mime": mime,
        "width": img['shape'][0],
        "height": img['shape'][1],
        "mode": img['mode']
    }


def get_image_raw_data(file_path: Path) -> list[float]:
    return process_raw_img_data(imread(file_path))


def process_raw_img_data(data) -> list[float]:
    data = (data.astype("float32") / (2 ** 8)).flatten().tolist()
    return data


def save_image_raw_data(raw_data: list, metadata: dict, file_path: Path):
    depth = len(metadata["mode"])
    dim = [metadata["height"], int(metadata["width"])]
    if depth > 1:
        dim.append(depth)
    img = (np.reshape(raw_data, dim) * (2 ** 8)).astype("uint8")
    imwrite(file_path, img)
