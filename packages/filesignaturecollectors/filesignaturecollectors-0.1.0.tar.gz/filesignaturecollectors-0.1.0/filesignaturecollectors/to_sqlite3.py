# -*- coding: utf-8 -*-
"""
Class to store data obtained from web pages containing magic file number
information in a SQLite3 file.

The name of the table is `file_signatures`, and the name of the sqlite file is
`file_signatures.sqlite`, if you wish you can give it another name, remember
to add `.sqlite` at the end.

Columns:
    * `id`
    * `hex_signature`
    * `byte_offset`
    * `ascii_signature`
    * `file_extentions`
    * `file_description`
    * `notes`
    * `notes_hex_signs`
"""


import sqlite3
from typing import Tuple, TypeVar


FileMagicDataOBJ = TypeVar('FileMagicDataOBJ')
FileMagicDataDict = TypeVar('FileMagicDataDict')


class ToSqlite3:

    def __init__(
        self,
        db_path: str = 'file_signatures.sqlite'
    ) -> None:
        self.name_table = 'file_signatures'
        self.db_path = self.__db_name(filename=db_path)
        self.connection = None
        self.cursor = None

    def __db_name(
        self,
        filename: str
    ) -> str:
        if not filename.endswith('.sqlite'):
            return filename + '.sqlite'
        else:
            return filename

    def connectDB(self) -> sqlite3.Connection:
        self.connection = sqlite3.connect(self.db_path)
        return self.connection

    def get_cursor(self) -> sqlite3.Cursor:
        self.cursor = self.connection.cursor()
        return self.cursor

    def create_table(self) -> None:
        columns = [
            "id TEXT NOT NULL",
            "hex_signature TEXT",
            "byte_offset TEXT",
            "ascii_signature TEXT",
            "file_extentions TEXT",
            "file_description TEXT",
            "notes TEXT",
            "notes_hex_signs TEXT"
        ]
        self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS %s (%s) " % (
                        self.name_table,
                        ", ".join(columns)
                    )
            )

    def insert_one(
        self,
        fileMagicDict: FileMagicDataDict
    ) -> int:
        sql_query = 'INSERT INTO %s VALUES(?, ?, ?, ?, ?, ?, ?, ?) ' % (
                                    self.name_table
                                )
        self.cursor.execute(sql_query, (
                    fileMagicDict['id'],
                    fileMagicDict['hex_signature'],
                    fileMagicDict['file_extentions'],
                    fileMagicDict['ascii_signature'],
                    fileMagicDict['file_description'],
                    fileMagicDict['byte_offset'],
                    fileMagicDict['notes'],
                    fileMagicDict['notes_hex_signs']
                )
            )
        self.connection.commit()
        return self.cursor.rowcount

    def insert_many(
        self,
        tupleFileMagicDict: Tuple[FileMagicDataDict]
    ) -> int:
        name_columns = (
            ':id',
            ':hex_signature',
            ':byte_offset',
            ':ascii_signature',
            ':file_extentions',
            ':file_description',
            ':notes',
            ':notes_hex_signs'
        )
        sql_query = 'INSERT INTO %s VALUES(%s)' % (
                self.name_table,
                ', '.join(name_columns),
            )
        self.cursor.executemany(sql_query, tupleFileMagicDict)
        self.connection.commit()
        return self.cursor.rowcount

    def get_hex_codes(self) -> list:
        sql = 'SELECT hex_signature FROM %s;' % self.name_table
        self.cursor.execute(sql)
        return [i[0] for i in self.cursor.fetchall()]

    def get_uniques(
        self,
        tupleFileMagicDict: Tuple[FileMagicDataDict]
    ) -> Tuple[FileMagicDataDict]:
        uniques = []
        list_hex = self.get_hex_codes()
        for item in tupleFileMagicDict:
            if item['hex_signature'] not in list_hex:
                uniques.append(item)
        return tuple(uniques)

    def clear_table(self) -> None:
        self.cursor.execute('DROP * FROM %s;' % self.name_table)
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()
