# -*- coding: utf-8 -*-
"""
Utils
"""

from typing import (
    TypeVar,
    Union,
    List
)


FileMagicDataObj = TypeVar('FileMagicDataObj')


class ListFileMagicData(list):

    def __init__(self):
        self.index = -1
        self.id_obj = 1
        self.data = []
        self.hex_codes = []
        self.indexes_obj = []

        super().__init__()

    @property
    def count(self) -> int:
        return len(self.data)

    def get_codex(
        self,
        file_extention: str
    ) -> list:
        return self.codec[file_extention]

    def to_save(
        self,
        file_extentions: Union[List[str] | None],
        fileMagic: FileMagicDataObj,
    ) -> None:
        if file_extentions is None:
            self.__iter_hex_codes(
                        fileMagic=fileMagic,
                        file_extention=None
                    )
        else:
            for file_extention in file_extentions:
                self.__iter_hex_codes(
                        fileMagic=fileMagic,
                        file_extention=file_extention
                    )

    def __iter_hex_codes(
        self,
        fileMagic: FileMagicDataObj,
        file_extention: str
    ) -> None:
        for hexsign in fileMagic.hex_signature:
            if hexsign not in self.hex_codes:
                self.hex_codes.append(hexsign)
                self.add_item(objInstace=fileMagic)

    def add_item(
        self,
        objInstace: FileMagicDataObj
    ) -> int:
        self.index += 1
        self.indexes_obj.append(self.index)
        self.data.append(objInstace)
        return self.index

    def get_item(
        self,
        index: int = 0
    ) -> FileMagicDataObj:
        return self.data[index]

    def search(
        self,
        type_attribute: str,
        data_attribute: str
    ) -> Union[FileMagicDataObj | None]:
        if self.count <= 0:
            return None
        for item in self.data:
            if data_attribute in item.type_attribute:
                return item
        else:
            return None
