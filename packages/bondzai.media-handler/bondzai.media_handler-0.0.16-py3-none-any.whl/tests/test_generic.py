from bondzai.media_handler import save_generic_raw_data, get_generic_raw_data, get_generic_metadata
import tempfile
import pytest
from pathlib import Path
import numpy as np


@pytest.mark.parametrize("format", [(".json", "application/json")])
def test_generic(format):
    TOLERANCE = 1e-4
    dim = [24, 3]
    length = 18

    save_dir = Path(tempfile.mkdtemp())
    data = 2 * np.random.random(length * np.prod(dim)) - 1
    data = data.astype("float32").tolist()
    file_path = save_dir / ("test" + format[0])
    save_generic_raw_data(data, {"mime": format[1], "dim": dim}, file_path)
    raw_data = get_generic_raw_data(file_path)
    metadata = get_generic_metadata(file_path)
    assert np.max(np.abs(np.asarray(raw_data) - np.asarray(data))) < TOLERANCE
    assert metadata["mime"] == format[1]
    assert metadata["dim"] == dim
