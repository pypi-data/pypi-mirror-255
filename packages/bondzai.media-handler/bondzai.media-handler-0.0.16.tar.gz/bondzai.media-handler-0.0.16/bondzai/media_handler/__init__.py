from pathlib import Path

from .base import get_file_mime, load_binary, save_binary, iter_data
from .audio import AUDIO_ALLOWED_MIME, get_audio_metadata, get_audio_raw_data, save_audio_raw_data
from .image import IMAGE_ALLOWED_MIME, get_image_metadata, get_image_raw_data, save_image_raw_data
from .video import VIDEO_ALLOWED_MIME, get_video_metadata, get_video_raw_data, save_video_raw_data
from .generic import GENERIC_ALLOWED_MIME, get_generic_metadata, get_generic_raw_data, save_generic_raw_data


__version__ = "0.0.16"


def get_raw_data(file_path: Path) -> list[float]:
    """
    Get raw data as list from file
    Args:
        file_path: path of the file
    Returns:
        raw_data: raw_data contained in file
    """
    mime = get_file_mime(file_path)
    if mime in AUDIO_ALLOWED_MIME:
        return get_audio_raw_data(file_path)
    elif mime in IMAGE_ALLOWED_MIME:
        return get_image_raw_data(file_path)
    elif mime in VIDEO_ALLOWED_MIME:
        return get_video_raw_data(file_path)
    elif mime in GENERIC_ALLOWED_MIME:
        return get_generic_raw_data(file_path)
    raise Exception(f"File mime '{mime}' is not supported")


def save_raw_data(data: list, metadata: dict, file_path: Path):
    """
    Save raw data in file
    Args:
        data: raw data
        metadata: metadata of the future file
        file_path: path of the future file
    """
    mime = metadata["mime"]
    if mime in AUDIO_ALLOWED_MIME:
        return save_audio_raw_data(data, metadata, file_path)
    elif mime in IMAGE_ALLOWED_MIME:
        return save_image_raw_data(data, metadata, file_path)
    elif mime in VIDEO_ALLOWED_MIME:
        return save_video_raw_data(data, metadata, file_path)
    elif mime in GENERIC_ALLOWED_MIME:
        return save_generic_raw_data(data, metadata, file_path)
    else:
        raise Exception(f"File mime '{mime}' is not supported")


def get_metadata(file_path: Path) -> dict:
    """
    Get metadata of a file
    Args:
        file_path: path of the future file
    Returns:
        metadata: metadata a dict
    """
    mime = get_file_mime(file_path)
    if mime in AUDIO_ALLOWED_MIME:
        return get_audio_metadata(file_path)
    elif mime in IMAGE_ALLOWED_MIME:
        return get_image_metadata(file_path)
    elif mime in VIDEO_ALLOWED_MIME:
        return get_video_metadata(file_path)
    elif mime in GENERIC_ALLOWED_MIME:
        return get_generic_metadata(file_path)
    raise Exception(f"File mime '{mime}' is not supported")
