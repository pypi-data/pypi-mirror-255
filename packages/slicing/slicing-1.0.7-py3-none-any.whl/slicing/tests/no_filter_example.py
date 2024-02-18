import time
from pathlib import Path

from slicing.factory import SliceFactory


if __name__ == '__main__':
    start = time.perf_counter()
    path = Path("D:\\aws\\eclinical40_auto_testing\\slicing\\src\\slicing\\tests\\resources")
    file = path.joinpath(Path("eclinical_iwrs_prod_113_20240113.sql"))
    tid = SliceFactory.slice(absolute_file_path=file, absolute_out_put_folder=Path("Result"),)

    print(tid)
    print("wait:", time.perf_counter()-start)