import json
from pathlib import Path

from slicing.constant import ListFileInfo, DOO
from slicing.info.file_info import FileInfo


class FileInfoList:
    def __init__(self, where: Path):
        self._where = where

    def id(self):
        return self.read().get("id")

    def read(self):
        with open(self._where.joinpath("file_list.json")) as f:
            return json.load(f)

    def create_files(self) -> list[FileInfo]:
        return self.files(ListFileInfo.CREATE)

    def insert_files(self) -> list[FileInfo]:
        return self.files(ListFileInfo.INSERT)

    def files(self, list_type: ListFileInfo) -> list[FileInfo]:
        return sorted([FileInfo(file.get("sqlType"),
                                file.get("name"),
                                file.get("table"),
                                file.get("id"),
                                file.get("size"),
                                file.get("no"),
                                file.get("view"),
                                file.get("procedure"),
                                file.get("index"),
                                file.get("operate_object"))
                       for file in self.read().get(list_type.name)], key=lambda fileinfo: fileinfo.no)

    def modify_files(self):
        return self.files(ListFileInfo.MODIFY)

    def alter_files(self):
        return self.files(ListFileInfo.ALTER)

    def drop_files(self):
        return self.files(ListFileInfo.DROP)

    def update_files(self):
        return self.files(ListFileInfo.UPDATE)

    def call_files(self):
        return self.files(ListFileInfo.CALL)

    def delete_files(self):
        return self.files(ListFileInfo.DELETE)

    def truncate_files(self):
        return self.files(ListFileInfo.TRUNCATE)

    def lists(self, mode: ListFileInfo = ListFileInfo.ALL) -> list[FileInfo]:
        """
        返回 SQL 的文件名列表
        :param mode:
        FileInfoList.INSERT_LIST 插入数据的 SQL
        FileInfoList.CREATE_LIST 创建表单的 SQL
        FileInfoList.ALL_LIST 创建和插入数据的 SQL

        :type mode:
        :return: sql 文件的列表
        :rtype:
        """
        if mode == ListFileInfo.ALL:
            all_list = []
            for list_type in [ListFileInfo.CREATE,
                              ListFileInfo.UPDATE,
                              ListFileInfo.DROP,
                              ListFileInfo.MODIFY,
                              ListFileInfo.ALTER,
                              ListFileInfo.INSERT,
                              ListFileInfo.CALL,
                              ]:
                all_list.extend(self.files(list_type))
            return all_list
        else:
            return self.files(mode)

    def table(self, list_type: ListFileInfo = ListFileInfo.INSERT) -> list[str]:
        """
        返回 表名,
        如果参数为 ALL_LIST, 会自动去重
        :param list_type:
        FileInfoList.INSERT_LIST 插入数据的 SQL 的表名
        FileInfoList.CREATE_LIST 创建表单的 SQL 的表名
        FileInfoList.ALL_LIST 创建和插入数据的 SQL交集 的表名
        :type list_type:
        :return: 表名的列表
        :rtype:
        """
        tables = set()
        for f in self.lists(list_type):
            if f.operate_object == DOO.Table.name:
                tables.add(f.table)
        return list(tables)

    def view(self, list_type: ListFileInfo = ListFileInfo.CREATE):
        """
        返回视图名
        如果参数为 ALL_LIST, 会自动去重
        :param list_type:
        :type list_type:
        :return:
        :rtype:
        """
        views = set()
        for f in self.lists(list_type):
            if f.operate_object == DOO.View.name:
                views.add(f.view)
        return list(views)

    def index(self, list_type: ListFileInfo = ListFileInfo.CREATE):
        """
        返回索引名
        如果参数为 ALL_LIST, 会自动去重
        :param list_type:
        :type list_type:
        :return:
        :rtype:
        """
        indexes = set()
        for f in self.lists(list_type):
            if f.operate_object == DOO.Index.name:
                indexes.add(f.index)
        return list(indexes)

    def procedure(self, list_type: ListFileInfo = ListFileInfo.CREATE):
        """
        返回生成的存储过程名
        如果参数为 ALL_LIST, 会自动去重
        :param list_type:
        :type list_type:
        :return:
        :rtype:
        """
        procedures = set()
        for f in self.lists(list_type):
            if f.operate_object == DOO.Procedure.name:
                procedures.add(f.procedure)
        return list(procedures)

    def find(self, name: str, list_type: ListFileInfo = ListFileInfo.INSERT) -> list[FileInfo]:
        """
        查询符合名字的所有 File

        :param name: 操作对象名，表名 | 索引名 | 存储过程名 | 视图名
        :type name:
        :param list_type: 操作类型
        :type list_type:
        :return:
        :rtype:
        """
        files = self.lists(mode=list_type)
        return list(filter(lambda info: info.table == name or info.view == name or info.procedure == name, files))

    def orders(self)->list[FileInfo]:
        """
        所有的 SQL File 语句 针对文件中的先后数序排序
        :return:
        :rtype:
        """
        return sorted(self.lists(ListFileInfo.ALL), key=lambda fileinfo: fileinfo.no)
