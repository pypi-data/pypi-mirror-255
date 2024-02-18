import re
import tempfile
import time
from pathlib import Path

from slicing.reader.reader import Reader
from slicing.stmt.condition.always_true import AlwaysTrue
from slicing.stmt.condition.condition import Condition
from slicing.stype.gz_slice import GZSlice
from slicing.stype.sql_slice import SQLSlice
from slicing.stype.zip_slice import ZipSlice


class SliceFactory:

    @staticmethod
    def zip(file_path,
            reader=Reader(),
            before_condition: Condition = AlwaysTrue(),
            after_condition: Condition = AlwaysTrue()):
        if file_path.name.endswith(".zip") and ZipSlice.magic(file_path):
            return ZipSlice(reader, before_condition, after_condition)

    @staticmethod
    def gz(file_path,
           reader=Reader(),
           before_condition: Condition = AlwaysTrue(),
           after_condition: Condition = AlwaysTrue()):
        if file_path.name.endswith(".gz") and GZSlice.magic(file_path):
            return GZSlice(reader, before_condition, after_condition)

    @staticmethod
    def sql(file_path,
            reader=Reader(),
            before_condition: Condition = AlwaysTrue(),
            after_condition: Condition = AlwaysTrue()):
        if file_path.name.endswith(".sql"):
            return SQLSlice(reader, before_condition, after_condition)

    @staticmethod
    def is_valid_folder_name(absolute_out_put_folder: Path):
        # TODO 临时修复加了Linux路径判断，但没有分系统和特殊字符的判断
        patterns = [r'^[^<>:""/|\?*]*[^<>:""/|\?*]$',
                    r'^([a-zA-Z]:\\(?:[^<>:\"\\\\|?*]+\\)*[^<>:\"\\\\|?*]+)$',
                    r'^\/[\w\-.]+(\/[\w\-.]+)*\/?$']
        for pattern in patterns:
            if re.match(pattern, str(absolute_out_put_folder)):
                return True
        return False

    @staticmethod
    def slice(absolute_file_path: Path, absolute_out_put_folder: Path,
              reader=Reader(),
              before_condition: Condition = AlwaysTrue(),
              after_condition: Condition = AlwaysTrue()):
        """
        分割文件
        :param before_condition: 只支持 BytesConditional , 原理是文本匹配
        :type before_condition:
        :param after_condition: 对象的参数匹配
        :type after_condition:
        :param absolute_file_path: 文件的绝对路径
        :type absolute_file_path: pathlib.Path
        :param absolute_out_put_folder: 输出文件夹的绝对路径
        :type absolute_out_put_folder: pathlib.Path
        :return: 任务的ID
        :rtype: uuid
        """
        if not absolute_file_path.exists(): raise Exception(f'{absolute_file_path} is not exist')
        if not SliceFactory.is_valid_folder_name(absolute_out_put_folder):
            raise Exception(f'{absolute_out_put_folder} is not folder name')
        if absolute_file_path.is_file():
            slicer = SliceFactory.zip(absolute_file_path, reader, before_condition, after_condition) \
                     or SliceFactory.gz(absolute_file_path, reader, before_condition, after_condition) \
                     or SliceFactory.sql(absolute_file_path, reader, before_condition, after_condition)
            slicer.ready(out_put=absolute_out_put_folder)
            slicer.slice(file=absolute_file_path)
            if slicer is None:
                raise Exception(f"Unknown format {absolute_file_path}")
            return slicer.task_id
        else:
            raise Exception(f'{absolute_file_path} is not file')



