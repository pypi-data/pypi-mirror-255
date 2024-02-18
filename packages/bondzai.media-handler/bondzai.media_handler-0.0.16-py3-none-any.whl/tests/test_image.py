from bondzai.media_handler import save_image_raw_data, get_image_raw_data, get_image_metadata
from bondzai.media_handler.image import GREYSCALE_8BIT_MODE, RGB_8BIT_MODE
import tempfile
import pytest
from pathlib import Path
import numpy as np


@pytest.mark.parametrize("mode", [GREYSCALE_8BIT_MODE, RGB_8BIT_MODE])
@pytest.mark.parametrize("format", [(".png", "image/png")])  # Not test for (".jpg", "image/jpeg") because lossy
def test_image(format, mode):
    TOLERANCE = 1e-4

    width = 24
    height = 32
    depth = len(mode)

    save_dir = Path(tempfile.mkdtemp())
    data = np.random.randint(0, 255, width * height * depth)
    data = (data.astype("float32") / 2 ** 8).tolist()
    file_path = save_dir / ("test" + format[0])
    save_image_raw_data(data, {"mime": format[1], "width": width, "height": height, "mode": mode}, file_path)
    raw_data = get_image_raw_data(file_path)
    metadata = get_image_metadata(file_path)
    assert np.max(np.abs(np.asarray(raw_data) - np.asarray(data))) < TOLERANCE
    assert metadata["width"] == width
    assert metadata["height"] == height
    assert metadata["mode"] == mode
    assert metadata["mime"] == format[1]
