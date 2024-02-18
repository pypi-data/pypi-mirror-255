import imageio
from pathlib import Path

import numpy as np
from imageio.v3 import immeta, improps

from bondzai.media_handler.registry import Registry

from .image import process_raw_img_data
from .base import check_mime


VIDEO_ALLOWED_MIME = [
    "video/mp4",
    "video/quicktime",
    "video/webm"
]


def get_video_metadata(file_path: Path) -> dict:
    mime = check_mime(file_path, VIDEO_ALLOWED_MIME)
    img = immeta(file_path)
    props = improps(file_path)
    return {
        "mime": mime,
        "width": img['size'][0],
        "height": img['size'][1],
        "fps": img['fps']
    }


def get_video_raw_data(file_path: Path) -> list[float]:
    video = np.asarray(imageio.mimread(file_path))
    results = process_raw_img_data(video)
    return results


def save_video_raw_data(raw_data: list, metadata: dict, file_path: Path):
    dim = [metadata["height"], metadata["width"], 3]
    dim = [(int(len(raw_data) / np.prod(dim)))] + dim
    vid = (np.reshape(raw_data, dim) * (2 ** 8)).astype("uint8")
    imageio.mimwrite(file_path, vid, fps=metadata["fps"], codec="libx264rgb", 
                     output_params= Registry.registered("video_args"))
