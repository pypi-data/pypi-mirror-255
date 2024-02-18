# -*- coding: utf-8 -*-
"""
Models
"""

from typing import TypeVar, Union

FileMagicDataInstace = TypeVar('FileMagicDataInstace')
uuid4Hex = TypeVar('uuid4Hex')


class FileMagicData:
    index = 0

    def __init__(
        self,
        id: uuid4Hex,
        hex_signature: str = None,
        file_extentions: str = None,
        ascii_signature: str = None,
        file_description: str = None,
        byte_offset: int = None,
        notes: str = None,
        notes_hex_signs: str = None
    ):
        self.idx = None
        self.id = id
        self.hex_signature = hex_signature
        self.file_extentions = file_extentions
        self.ascii_signature = ascii_signature
        self.file_description = file_description
        self.byte_offset = byte_offset
        self.notes = notes
        self.notes_hex_signs = notes_hex_signs

    def compare(
        self,
        obj: FileMagicDataInstace
    ) -> bool:
        sign = obj.hex_signature.split('|')
        signs_bool = [i_sign in self.hex_signature for i_sign in sign]
        return any(signs_bool)

    def join_items(
        self,
        data: list
    ) -> Union[str | None]:
        if type(data) is list:
            return '|'.join(data)
        else:
            return None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'hex_signature': self.join_items(data=self.hex_signature),
            'byte_offset': self.join_items(self.byte_offset),
            'ascii_signature': self.join_items(self.ascii_signature),
            'file_extentions': self.join_items(self.file_extentions),
            'file_description': self.file_description,
            'notes': self.notes,
            'notes_hex_signs': self.join_items(self.notes_hex_signs)
        }

    def __str__(self) -> str:
        return '<[%s, %s, %s]>' % (
                    self.id,
                    self.file_extentions,
                    self.hex_signature,
                )
