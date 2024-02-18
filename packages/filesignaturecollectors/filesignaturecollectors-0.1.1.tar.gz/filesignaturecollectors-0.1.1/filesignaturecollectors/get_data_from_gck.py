# -*- coding: utf-8 -*-
"""
Information obtained from `https://www.garykessler.net/library/file_sigs.html`.

>>>  Credits to the authors, thank you very much for your dedication.  <<<


This class just gets the data and saves it in a format for more accessible use
(or that's the idea). --- Kurotom

ISO-8859-1/latin-1
"""


from filesignaturecollectors.models import FileMagicData
from filesignaturecollectors.utils.listfilemagicdata import ListFileMagicData

from uuid import uuid1
from bs4 import BeautifulSoup
from bs4 import Tag
import requests
import re

from typing import List, TypeVar


FileMagicDataDict = TypeVar('FileMagicData')


class GCKFileSignatures:

    def __init__(self) -> None:
        self.url = 'https://www.garykessler.net/library/file_sigs.html'
        self.sopa = None
        self.data = ListFileMagicData()
        self.total = self.data.count

        self.get_sopa()

    def get_page(self) -> bytes:
        r = requests.get(self.url)
        if r.status_code == 200:
            return r.content.decode('ISO-8859-1')

    def get_sopa(self) -> None:
        self.sopa = BeautifulSoup(self.get_page(), 'html.parser')

    def get_table_html(self) -> Tag:
        return self.sopa.find_all('table')[0]

    def get_trs(self) -> List[Tag]:
        return self.get_table_html().find_all('tr')[3:]

    def check_attrs(
        self,
        data: List[Tag]
    ) -> bool:
        for item in data:
            # print(list(item.attrs.values()))
            return list(item.attrs.values()) == []

    def get_values(
        self,
        data: Tag
    ) -> list:
        # print(data)
        try:
            for i in data.find_all('br'):
                i.replace_with('\n')
            new_data = data.get_text(separator='\n').split('\n')
            return new_data
        except AttributeError:
            return data

    def get_clear_data(
        self,
        data: list,
        strip: bool = False
    ) -> list:
        r = []
        new_data = self.get_values(data=data)
        for i in new_data:
            i = i.replace('n/a', '')
            if i != '' and i != 'or':
                i = i.replace('\xa0', '')
                i = i.replace('—', ' ')
                if strip:
                    i = i.strip()
                r.append(i)
        return r

    def clear_file_extentions(
        self,
        data: str
    ) -> list:
        new_data = [
                i.strip().lower()
                for i in data.split(',')
            ]
        new_data = self.get_clear_data(data=new_data)
        if new_data == []:
            return None
        else:
            return new_data

    def clear_hex_sign(
        self,
        data: Tag
    ) -> list:
        # print(data)
        new_data = self.get_values(data=data)
        new_data = self.get_clear_data(data=new_data)
        new_data = [
            re.sub(r'xx', '??', i)
            for i in new_data
        ]
        return new_data

    def get_bytes_offset(
        self,
        data: str
    ) -> list:
        data = data.replace('[', '')
        data = data.replace(']', '')
        data = data.replace('byte offset', '')
        data = data.strip()
        data = data.split(' ')
        return data

    def get_content_trs(self) -> int:
        index = 0
        for content_tr in self.get_trs():
            td_tr = content_tr.find_all('td')
            hex_signs = None
            if len(td_tr) == 3:
                if self.check_attrs(data=td_tr):
                    hex_signs = content_tr.select(
                                        'td:nth-child(1) > font'
                                    )[0]
                    ascii_signs = content_tr.select(
                                        'td:nth-child(3) > font'
                                    )[0]

                    hex_signs_data = self.clear_hex_sign(data=hex_signs)
                    ascii_signs_data = self.get_clear_data(data=ascii_signs)
                    byte_offset_data = None

                    if hex_signs_data[0].startswith('['):
                        byte_offset_data = self.get_bytes_offset(
                                                    data=hex_signs_data[0]
                                                )
                        hex_signs_data = hex_signs_data[1:]
                        ascii_signs_data = ascii_signs_data[1:]

                    fileMagic = FileMagicData(
                                    id=uuid1().hex,
                                    hex_signature=hex_signs_data,
                                    file_extentions=None,
                                    ascii_signature=ascii_signs_data,
                                    file_description=None,
                                    byte_offset=byte_offset_data,
                                    notes=None,
                                    notes_hex_signs=None
                                )

                    self.data.add_item(objInstace=fileMagic)
                    index += 1
                    # print(hex_signs_data, ascii_signs_data, byte_offset_data)
                else:
                    fileMagicLast = self.data.get_item(index=-1)
                    file_extentions = content_tr.select(
                                                'td:nth-child(1)'
                                            )[0].text

                    file_extentions_data = self.clear_file_extentions(
                                                        data=file_extentions
                                                    )

                    file_description = content_tr.select(
                                                'td:nth-child(3)'
                                            )[0].text

                    if fileMagicLast.file_extentions is None:
                        fileMagicLast.file_extentions = file_extentions_data
                    else:
                        newfileMagic = FileMagicData(
                                    id=uuid1().hex,
                                    hex_signature=fileMagic.hex_signature,
                                    file_extentions=file_extentions_data,
                                    ascii_signature=fileMagic.ascii_signature,
                                    file_description=None,
                                    byte_offset=fileMagic.byte_offset,
                                    notes=None,
                                    notes_hex_signs=None
                                )

                        self.data.add_item(objInstace=newfileMagic)
                        index += 1

                    if fileMagicLast.file_description is None:
                        fileMagicLast.file_description = file_description
                    else:
                        fileMagicLast = self.data.get_item(index=-1)
                        fileMagicLast.file_description = file_description

                    n = 1
                    while n < self.data.count:
                        obj = self.data.get_item(index=(n * -1))
                        if obj.file_extentions is None:
                            obj.file_extentions = file_extentions_data
                            obj.file_description = file_description
                            break
                        n += 1

            elif len(td_tr) == 1:
                # <blockquote> NOTES
                blockquote = td_tr[0].select('blockquote')
                if blockquote != []:
                    notes = blockquote[0].text
                    blockquote_hex_signs = self.get_hex_code_notes(
                                                blockquote_data=blockquote[0]
                                            )
                    blockquote_hex_signs_data = self.get_clear_data(
                                                    data=blockquote_hex_signs
                                                )

                    fileMagicLast = self.data.get_item(index=-1)
                    fileMagicLast.notes = notes
                    fileMagicLast.notes_hex_signs = blockquote_hex_signs_data

        return self.data.count

    def get_hex_code_notes(
        self,
        blockquote_data: Tag
    ) -> list:
        result = []
        for line in blockquote_data.text.split('\n'):
            x = re.findall(
                    r'((v.+\(.+\) . )?(0x(..-){2,}.+))',
                    line,
                    re.DOTALL
                )
            if len(x) > 0:
                data = x[0][0]
                result.append(data)
        return result

    def get_data(self) -> List[FileMagicData]:
        return self.data.data
