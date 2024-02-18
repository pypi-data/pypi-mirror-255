# -*- coding: utf-8 -*-
"""
Controller.
Responsible for managing the workflow between the collection and storage
classes.
"""

from filesignaturecollectors.get_data_from_gck import GCKFileSignatures
from filesignaturecollectors.get_data_from_wiki import WikiFileSignatures
from filesignaturecollectors.to_sqlite3 import ToSqlite3
from filesignaturecollectors.to_file import ToFile
from filesignaturecollectors.models import FileMagicData
from filesignaturecollectors.utils.listfilemagicdata import ListFileMagicData

from typing import List, Tuple, TypeVar, Union


FileMagicDataDict = TypeVar('FileMagicDataDict')


class Controller:

    def __init__(self):
        self.db = ToSqlite3()
        self.file = ToFile()
        self.data = ListFileMagicData()
        self.total = 0

    def get_data_gck(self) -> List[FileMagicData]:
        g = GCKFileSignatures()
        count = g.get_content_trs()
        self.total = self.total + count
        return g.get_data()

    def get_data_wiki(self) -> List[FileMagicData]:
        w = WikiFileSignatures()
        count = w.getting_data_trs()
        self.total = self.total + count
        return w.get_data()

    def consolidate_data(
        self,
        *listsFileMagicData: List[FileMagicData]
    ) -> int:
        if len(listsFileMagicData) >= 2:
            listData = []
            for listItem in listsFileMagicData:
                listData += listItem
            for item in listData:
                self.data.to_save(
                        file_extentions=item.file_extentions,
                        fileMagic=item
                    )

            return len(self.data.data)
        else:
            self.data.data = listsFileMagicData[0]
            return len(self.data.data)

    def get_consolidate_data(self) -> tuple:
        return self.data.data

    def get_dict_data(
        self,
        listFileMagicData: List[FileMagicData] = None
    ) -> Tuple[FileMagicDataDict]:
        if listFileMagicData is None:
            return tuple(i.to_dict() for i in self.data.data)
        else:
            return tuple(i.to_dict() for i in listFileMagicData)

    def to_db(
        self,
        data: Union[FileMagicDataDict | Tuple[FileMagicDataDict]]
    ) -> int:
        self.db.connectDB()
        self.db.get_cursor()
        self.db.create_table()
        rows_affected = -1

        if type(data) is dict:
            if data['hex_signature'] not in self.db.get_hex_codes():
                rows_affected = self.db.insert_one(fileMagicDict=data)
        elif type(data) is tuple:
            unique_data = self.db.get_uniques(tupleFileMagicDict=data)
            if len(unique_data) > 0:
                rows_affected = self.db.insert_many(
                                            tupleFileMagicDict=unique_data
                                        )
        self.db.close()
        return rows_affected

    def to_file(
        self,
        data: Tuple[FileMagicDataDict]
    ) -> None:
        self.file.to_file(tupleFileMagicDict=data)
