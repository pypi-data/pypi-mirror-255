import json
from pathlib import Path


class FileInfoWriter:
    def __init__(self, out_put: Path):
        self.content = dict(CREATE=[], INSERT=[], DROP=[], ALTER=[],
                            UPDATE=[], MODIFY=[], CALL=[], DELETE=[],
                            TRUNCATE=[], id=-1)
        self._out_put = out_put

    def set_id(self, value):
        self.content["id"] = value

    def add_sql(self, file_id, statement, size, no):
        _name = statement.file_name()
        file_name = f'{_name}-{file_id}'
        self.content[statement.operate()].append(dict(sqlType=statement.operate(),
                                                      name=file_name,
                                                      id=file_id,
                                                      table=statement.table(),
                                                      view=statement.view(),
                                                      procedure=statement.procedure(),
                                                      index=statement.index(),
                                                      operate_object=statement.operate_object(),
                                                      size=size,
                                                      no=no.get()))

    def write(self):
        if Path.exists(self._out_put):
            with open(self._out_put.joinpath("file_list.json"), 'w') as f:
                json.dump(self.content, f)
