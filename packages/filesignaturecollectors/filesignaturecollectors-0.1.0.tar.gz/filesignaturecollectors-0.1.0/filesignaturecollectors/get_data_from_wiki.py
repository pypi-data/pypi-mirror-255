# -*- coding: utf-8 -*-
"""
Class gets information from:
`https://en.wikipedia.org/wiki/List_of_file_signatures`.

ISO-8859-1/latin-1
"""


from filesignaturecollectors.models import FileMagicData
from filesignaturecollectors.utils.listfilemagicdata import ListFileMagicData

from uuid import uuid1
import requests
from bs4 import BeautifulSoup
from bs4 import Tag
import re

from typing import List, TypeVar, Union


FileMagicDataDict = TypeVar('FileMagicData')


class WikiFileSignatures:

    def __init__(self) -> None:
        self.url = 'https://en.wikipedia.org/wiki/List_of_file_signatures'
        self.sopa = None
        self.data = ListFileMagicData()
        self.total = self.data.count

        self.get_sopa()

    def get_page(self) -> str:
        r = requests.get(self.url)
        if r.status_code == 200:
            return r.content.decode('ISO-8859-1')

    def get_sopa(self) -> None:
        self.sopa = BeautifulSoup(self.get_page(), 'html.parser')

    def get_table_html(self) -> Tag:
        return self.sopa.find('table', {'class': 'wikitable sortable'})

    def headers_table(self) -> List[str]:
        return [i.text.strip() for i in self.get_table_html().find_all('th')]

    def get_tbody(self) -> Tag:
        return self.get_table_html().find_all('tbody')[0]

    def get_content_tbody_trs(self) -> List[Tag]:
        trs = self.get_table_html().find_all('tr')[1:]
        self.total = len(trs)
        return trs

    def clear_data(
        self,
        data: list
    ) -> list:
        res = []
        for item in data:
            item = item.strip()
            item = item.replace('(', '')
            item = item.replace(')', '')
            if item != '' and item != 'format':
                res.append(item)
        return res

    def encode_and_clear(
        self,
        data: list
    ) -> list:
        x = [
                i.encode('latin-1').decode('utf-8')
                for i in data
                if i != ''
            ]
        return self.clear_data(data=x)

    def clear_file_extentions(
        self,
        data: list
    ) -> Union[list | None]:
        new_data = self.clear_data(data=data)
        if new_data == []:
            return None
        else:
            return new_data

    def clear_ascii_sign(
        self,
        data: list
    ) -> Union[list | None]:
        new_data = self.encode_and_clear(data=data)
        if new_data == []:
            return None
        else:
            return new_data

    def clear_hex_sign(
        self,
        data: list
    ) -> list:
        new_data = [
            re.sub(r'[^\x20-\x7E]', ' ', i)
            for i in data
        ]
        return self.clear_data(data=new_data)

    def getting_data_trs(self) -> int:
        index = 0
        for item in self.get_content_tbody_trs():
            tds = item.find_all('td')[:5]
            if len(tds) == 5:
                hexsign = tds[0].get_text(separator='\n').split('\n')
                ascii_sign = tds[1].get_text(separator='\n').split('\n')
                offset = tds[2].get_text(separator='\n').split('\n')
                file_extention = tds[3].get_text(separator='\n').split('\n')
                description = tds[4].text

                hexsign_data = self.clear_hex_sign(data=hexsign)
                file_extention_data = self.clear_file_extentions(
                                                    data=file_extention
                                                )
                ascii_sign_data = self.clear_ascii_sign(data=ascii_sign)

                offset_data = self.encode_and_clear(data=offset)

                fileMagic = FileMagicData(
                                id=uuid1().hex,
                                hex_signature=hexsign_data,
                                file_extentions=file_extention_data,
                                ascii_signature=ascii_sign_data,
                                file_description=description,
                                byte_offset=offset_data,
                                notes=None,
                                notes_hex_signs=None
                            )

                self.data.add_item(objInstace=fileMagic)

            elif len(tds) == 3:
                hexsign = tds[0].get_text(separator='\n').split('\n')
                ascii_sign = tds[1].get_text(separator='\n').split('\n')
                description = tds[2].text

                hexsign_data = self.clear_hex_sign(data=hexsign)
                ascii_sign_data = self.clear_ascii_sign(data=ascii_sign)

                fileMagicPrev = self.data.get_item(index=-1)
                fileMagic = FileMagicData(
                                id=uuid1().hex,
                                hex_signature=hexsign_data,
                                file_extentions=fileMagicPrev.file_extentions,
                                ascii_signature=ascii_sign_data,
                                file_description=description,
                                byte_offset=fileMagicPrev.byte_offset,
                                notes=None,
                                notes_hex_signs=None
                            )

                self.data.add_item(objInstace=fileMagic)

            elif len(tds) == 2:
                hexsign = tds[0].get_text(separator='\n').split('\n')
                ascii_sign = tds[1].get_text(separator='\n').split('\n')

                hexsign_data = self.clear_hex_sign(data=hexsign)
                ascii_sign_data = self.clear_ascii_sign(data=ascii_sign)

                fileMagicPrev = self.data.get_item(index=-1)
                fileMagic = FileMagicData(
                            id=uuid1().hex,
                            hex_signature=hexsign_data,
                            file_extentions=fileMagicPrev.file_extentions,
                            ascii_signature=ascii_sign_data,
                            file_description=fileMagicPrev.file_description,
                            byte_offset=fileMagicPrev.byte_offset,
                            notes=None,
                            notes_hex_signs=None
                        )

                self.data.add_item(objInstace=fileMagic)

            index += 1

        return self.data.count

    def get_data(self) -> List[FileMagicData]:
        return self.data.data
