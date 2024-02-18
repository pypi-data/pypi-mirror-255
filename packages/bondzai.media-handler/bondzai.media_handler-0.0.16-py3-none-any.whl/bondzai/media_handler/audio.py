from pathlib import Path

import numpy as np
import audio_metadata
import soundfile as sf
from .base import check_mime


AUDIO_ALLOWED_MIME = [
    "audio/x-wav",
    "audio/wav",
    "audio/mpeg"
]


def get_audio_metadata(file_path: Path) -> dict:
    mime = check_mime(file_path, AUDIO_ALLOWED_MIME)
    audio = audio_metadata.load(file_path)

    return {
        "mime": mime,
        "sample_rate": audio["streaminfo"].sample_rate,
        "channels": audio["streaminfo"].channels,
    }


def get_audio_raw_data(file_path: Path) -> list[float]:
    data, _ = sf.read(file_path)
    return data.flatten().tolist()


def save_audio_raw_data(raw_data: list, metadata: dict, file_path: Path):
    nb_channels = metadata["channels"]
    data = np.reshape(raw_data, (int(len(raw_data) / nb_channels), nb_channels))
    sf.write(file_path, data, metadata["sample_rate"])
