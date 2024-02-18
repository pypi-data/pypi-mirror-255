from pathlib import Path
import json
import numpy as np
from .base import check_mime

GENERIC_ALLOWED_MIME = [
    "application/json"
]


def get_generic_metadata(file_path: Path) -> dict:
    mime = check_mime(file_path, GENERIC_ALLOWED_MIME)
    with open(file_path, "r") as f:
        obj = json.load(f)
    dim = []
    while isinstance(obj, list):
        dim.append(len(obj))
        obj = obj[0] if len(obj) else None
    return {"mime": mime, "dim": dim[1:]}


def get_generic_raw_data(file_path: Path) -> list[float]:
    with open(file_path, "r") as f:
        data = json.load(f)
    data = np.asarray(data).flatten().tolist()
    return data


def save_generic_raw_data(raw_data: list, metadata: dict, file_path: Path):
    data = np.reshape(raw_data, [int(len(raw_data) / np.prod(metadata["dim"]))] + metadata["dim"]).tolist()
    with open(file_path, "w") as f:
        json.dump(data, f)
