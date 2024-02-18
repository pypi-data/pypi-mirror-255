# -*- coding: utf-8 -*-
"""
Class to save data into a file with format:

The file generated have 5 columns and separates using tabulation.

Columns:
    * `hex_signature`
    * `file_extentions`
    * `ascii_signature`
    * `file_description`
    * `byte_offset`

The file is saved with the name `file_signatures` default, and you can give
another filename if you wish.
"""

from typing import Tuple, TypeVar


FileMagicDataDict = TypeVar('FileMagicDataDict')


class ToFile:
    def __init__(
        self,
        filename: str = 'file_signatures'
    ):
        self.filename = filename

    def to_file(
        self,
        tupleFileMagicDict: Tuple[FileMagicDataDict]
    ) -> None:
        data_string = ''

        data_string += '%s\t%s\t%s\t%s\t%s\n' % (
                    'hex_signature',
                    'byte_offset',
                    'ascii_signature',
                    'file_extentions',
                    'file_description'
                )

        for item in tupleFileMagicDict:
            hex_signature = item['hex_signature']
            byte_offset = item['byte_offset']
            ascii_signature = item['ascii_signature']
            file_extentions = item['file_extentions']
            file_description = item['file_description']

            s = '%s\t%s\t%s\t%s\t%s' % (
                            hex_signature,
                            byte_offset,
                            ascii_signature,
                            file_extentions,
                            file_description
                        )
            data_string += s.strip() + '\n'

        self.write(file_name=self.filename, data=data_string)

    def write(
        self,
        file_name: str,
        data: str
    ) -> None:
        with open(file_name, 'w') as file:
            file.write(data)
