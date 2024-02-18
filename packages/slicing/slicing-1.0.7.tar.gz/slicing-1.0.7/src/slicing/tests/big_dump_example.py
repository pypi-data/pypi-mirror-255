import time
from pathlib import Path

from slicing.factory import SliceFactory
from slicing.reader.dump_reader import DumpReader

if __name__ == "__main__":
    start = time.perf_counter()
    path = Path("D:\\aws\\eclinical40_auto_testing\\slicing\\src\\slicing\\tests\\resources")
    file = path.joinpath(Path("eclinical_edc_uat_21_20230601071306.sql"))
    tid = SliceFactory.slice(absolute_file_path=file, absolute_out_put_folder=Path("Result"),
                             reader=DumpReader(tables=["eclinical_study_site", "eclinical_study"]))

    # tid = SliceFactory.slice(absolute_file_path=file, absolute_out_put_folder=Path("Result"))
    print(tid)
    print("wait:", time.perf_counter() - start)