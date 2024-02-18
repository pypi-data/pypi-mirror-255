import mimetypes
import struct as st
from pathlib import Path


def check_mime(file_path: Path, allowed_mime: list) -> str:
    """
    Check if mime of the file is among the allowed ones
    Args:
        file_path: path of the file to be checked
        allowed_mime: list of allowed mime
    Returns:
        mime: mime value, if allowed, otherwise raise exception
    """
    mime = get_file_mime(file_path)
    if mime not in allowed_mime:
        raise Exception(f"'{mime}' not supported")
    return mime


def get_file_mime(file_path: Path):
    """
    Get mime of the file
    Args:
        file_path: path of the file to be checked
    Returns:
        mime: mime value
    """
    mime, _ = mimetypes.guess_type(file_path)
    return mime


def load_binary(file_path: Path) -> tuple[float]:
    """
    Load .bin file
    Args:
        file_path: bin file path
    Returns:
        data: data loaded from the bin file

    """
    with open(file_path, "rb") as f:
        d = f.read()
    data = tuple(float(_[0]) for _ in st.iter_unpack("<f", d))
    return data


def save_binary(file_path: Path, data: list[float]):
    """
    Save data to a bin file
    Args:
        file_path: file_path: bin file path
        data: data to be saved
    """
    d = st.pack(f"{len(data)}f", *data)
    with open(file_path, "+wb") as f:
        f.write(d)


def iter_data(data: list, chunk_size: int, hop_len: int):
    """
    From data as list, iter over data, rendering <chunk_size>-long data every <hop_len> samples
    Args:
        data: input data
        chunk_size: size of the chunk to be rendered
        hop_len: nb of samples to move extracting window
    """
    data_size = len(data)
    for i in range(0, data_size, hop_len):
        if i + chunk_size <= data_size:
            _data = data[i: i + chunk_size]
            yield _data
