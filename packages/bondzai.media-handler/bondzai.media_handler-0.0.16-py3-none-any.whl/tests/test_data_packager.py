import json
from re import S
import tarfile
from uuid import uuid4

import yaml
from bondzai.media_handler import get_raw_data, save_raw_data
from bondzai.media_handler.base import load_binary
from bondzai.media_handler.data_packager import generate_dataset, create_tar_from_folder, convert_to_binary, create_chunks, get_maestro_file_name
import tempfile
import pytest
from pathlib import Path
import numpy as np


UNKNOWN = "unknown"
LABEL_LIST_FILE_NAME = "LABEL_LIST.json"
TOLERANCE = 1e-4

DATA_GENERATION_DICT = {
    "audio": {"ext": ".wav", "metadata": {"mime": "audio/wav", "sample_rate": 48000, "channels": 16}},
    "image": {"ext": ".png", "metadata": {"mime": "image/png", "width": 128, "height": 64, "mode": "RGB"}},
    "video": {"ext": ".mp4", "metadata": {"mime": "video/mp4", "width": 32, "height": 16, "fps": 20}},
    "generic": {"ext": ".json", "metadata": {"mime": "application/json", "dim": [16]}},
    }

def generate_random_file(data_type: str, save_folder: Path) -> (Path, list[float]):
    save_folder.mkdir(parents=True, exist_ok=True)
    random_data = np.random.randint(0, 255, 16 * 3 * 32 * 16).astype(np.float32) / 256
    save_file = save_folder / str(uuid4())
    save_file = save_file.with_suffix(DATA_GENERATION_DICT[data_type]["ext"])
    save_raw_data(data=random_data, metadata=DATA_GENERATION_DICT[data_type]["metadata"], file_path=save_file)
    retrieved_data = get_raw_data(save_file)
    assert np.max(np.abs(np.asarray(random_data) - np.asarray(retrieved_data))) < TOLERANCE
    return save_file, retrieved_data    


def test_get_files_from_tar():
    # TODO : keep function?
    assert True

@pytest.mark.parametrize("data_type", ["audio", "generic", "video", "image"]) 
def test_create_tar_from_folder(data_type):
    save_folder = Path(tempfile.mkdtemp())
    file_list = [generate_random_file(data_type, save_folder) for _ in range(5)]
    tar_path = Path(tempfile.mkdtemp()) / "save.tar.gz"
    create_tar_from_folder(tar_path, save_folder)
    assert tar_path.exists()
    retrieve_folder = tar_path.parent / "retrieved"
    retrieve_folder.mkdir()
    with tarfile.open(tar_path, "w") as tar:
        tar.extractall(retrieve_folder)
    for index, file in enumerate(retrieve_folder.iterdir()):
        tar_data = get_raw_data(file)
        assert file_list[index][1]  
        assert np.max(np.abs(np.asarray(file_list[index][1]) - np.asarray(tar_data))) < TOLERANCE


@pytest.mark.parametrize("data_type", ["audio", "generic", "video", "image"]) 
def test_convert_to_binary(data_type):
    save_folder = Path(tempfile.mkdtemp())
    save_file, data = generate_random_file(data_type, save_folder)
    bin_file = convert_to_binary(save_file)
    assert bin_file.exists()
    bin_data = list(load_binary(bin_file))
    assert data == bin_data
    bin_file_2 = convert_to_binary(bin_file)
    assert bin_file_2 == bin_file
    bin_data_2 = list(load_binary(bin_file_2))
    assert data == bin_data_2


@pytest.mark.parametrize("data_type", ["audio", "generic", "video"]) 
def test_create_chunks(data_type):
    unit_size = 16 * 32 * 3
    chunk_size = 5 * unit_size
    hop_len = 3 * unit_size

    save_folder = Path(tempfile.mkdtemp())
    save_file, random_data = generate_random_file(data_type, save_folder)
    chunk_folder = save_file.parent / "chunks"
    create_chunks(save_file, chunk_size, hop_len, chunk_folder)
    for index, file in enumerate(chunk_folder.iterdir()):
        chunk_data = get_raw_data(file)
        chopped_data = random_data[hop_len * index: hop_len * index + chunk_size]
        assert np.max(np.abs(np.asarray(chunk_data) - np.asarray(chopped_data))) < TOLERANCE


def test_get_maestro_file_name():
    file_name = get_maestro_file_name(Path("a/b/c/file.txt"), {"key_1": "value_1", "key_2": "value_2"})
    assert file_name == 'file[key_1;value_1][key_2;value_2].txt'


@pytest.mark.parametrize("data_type", ["audio", "generic", "video", "image"]) 
def test_generate_dataset(data_type):

    def compare_output_dicts(d1, d2):
        assert len(d1.keys()) == len(d2.keys())
        for k, v in d1.items():
            if isinstance(v, dict):
                compare_output_dicts(v, d2[k])
            else:
                assert d2[k] == v

    def check_dataset(save_folder, file_list, source_name, convert_to_bin):
        with open(save_folder / "dataset.yml", "r") as f:
            dataset_dict = yaml.safe_load(f)
        assert len(dataset_dict["dataset"]) == len(file_list)
        for data in dataset_dict["dataset"]:
            assert data["source_id"] == source_name
            assert (save_folder / data["data"]).exists()
            for key, value in data["metadata"].items():
                assert DATA_GENERATION_DICT[data_type]["metadata"][key] == value
        for file_path, file_data, file_name in file_list:
            new_file_path = (save_folder / file_name)
            if convert_to_bin:
                new_file_path = new_file_path.with_suffix(".bin")
            assert new_file_path.exists()
            new_data = load_binary(new_file_path) if convert_to_bin else get_raw_data(new_file_path)
            assert np.max(np.abs(np.asarray(new_data) - np.asarray(file_data))) < TOLERANCE
    
    file_list = []
    
    dataset_folder = Path(tempfile.mkdtemp())
    LABELS = {"number": ["1", "2", "3"], "letter": ["a", "b"]}
    output_dict_ref = {}
    for key, value_list in LABELS.items():
        output_dict_ref[key] = {v: idx + 1 for idx, v in enumerate(value_list)}
    label_list = list(LABELS.keys())
    for label_1 in LABELS[label_list[0]]:
        for label_2 in LABELS[label_list[1]]:
            file, file_data = generate_random_file(data_type, dataset_folder / label_1 / label_2)
            file_name = f"{file.stem}[{label_list[1]};{label_2}][{label_list[0]};{label_1}]{file.suffix}"
            file_list.append((file, file_data, file_name))
    
    with open(dataset_folder / LABEL_LIST_FILE_NAME, "w")  as f:
        json.dump(label_list, f)


    save_folder = Path(tempfile.mkdtemp())
    output_dict = generate_dataset(dataset_folder, save_folder, "src_1")
    check_dataset(save_folder, file_list, source_name="src_1", convert_to_bin=True)
    compare_output_dicts(output_dict, output_dict_ref)

    save_folder = Path(tempfile.mkdtemp())
    output_dict = generate_dataset(dataset_folder, save_folder, "src_2", convert_to_bin=False)
    check_dataset(save_folder, file_list, source_name="src_2", convert_to_bin=False)
    compare_output_dicts(output_dict, output_dict_ref)

    save_folder = Path(tempfile.mkdtemp())
    tar_path = Path(tempfile.mkdtemp()) / "dataset.tar.gz"
    create_tar_from_folder(tar_path, dataset_folder)
    output_dict = generate_dataset(tar_path, save_folder, "src_3")
    check_dataset(save_folder, file_list, source_name="src_3", convert_to_bin=True)
    compare_output_dicts(output_dict, output_dict_ref)

    tar_save_path = Path(tempfile.mkdtemp()) / "save.tar.gz"
    output_dict = generate_dataset(dataset_folder, tar_save_path, "src_4")
    save_folder = Path(tempfile.mkdtemp())
    with tarfile.open(tar_save_path, "r") as tar:
        tar.extractall(save_folder)
    check_dataset(save_folder, file_list, source_name="src_4", convert_to_bin=True)
    compare_output_dicts(output_dict, output_dict_ref)

    init_output_dict = {"bool": {"true": 1, "false": 2}, "number": {"0": 2}}
    new_output_dict_ref = output_dict_ref.copy()
    new_output_dict_ref["bool"] = init_output_dict["bool"]
    new_output_dict_ref["number"]["0"] = 2
    new_output_dict_ref["number"]["1"] = 1
    new_output_dict_ref["number"]["2"] = 3
    new_output_dict_ref["number"]["3"] = 4
    save_folder = Path(tempfile.mkdtemp())
    output_dict = generate_dataset(dataset_folder, save_folder, "src_5", init_output_dict=init_output_dict)
    check_dataset(save_folder, file_list, source_name="src_5", convert_to_bin=True)
    compare_output_dicts(output_dict, new_output_dict_ref)
