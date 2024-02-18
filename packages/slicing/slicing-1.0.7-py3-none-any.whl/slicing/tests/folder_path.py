from pathlib import Path

from slicing.factory import SliceFactory


if __name__ == "__main__":
    print(SliceFactory.is_valid_folder_name(Path("/tmp/tmpbd87pdd5")))
