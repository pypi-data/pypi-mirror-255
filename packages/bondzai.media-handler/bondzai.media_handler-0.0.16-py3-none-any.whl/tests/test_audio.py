from bondzai.media_handler import save_audio_raw_data, get_audio_raw_data, get_audio_metadata
import tempfile
import pytest
from pathlib import Path
import numpy as np


@pytest.mark.parametrize("format", [(".wav", "audio/wav")])  # Not test for (".mp3", "audio/mpeg") because lossy
def test_audio(format):
    TOLERANCE = 1e-4

    nb_channels = 2
    length = 1024
    fs = 16000

    save_dir = Path(tempfile.mkdtemp())
    data = 2 * np.random.random(length * nb_channels) - 1
    data = data.astype("float32").tolist()
    file_path = save_dir / ("test" + format[0])
    save_audio_raw_data(data, {"mime": format[1], "sample_rate": fs, "channels": nb_channels}, file_path)
    raw_data = get_audio_raw_data(file_path)
    metadata = get_audio_metadata(file_path)
    assert np.max(np.abs(np.asarray(raw_data) - np.asarray(data))) < TOLERANCE
    assert metadata["channels"] == nb_channels
    assert metadata["sample_rate"] == fs
    assert metadata["mime"] == format[1]
