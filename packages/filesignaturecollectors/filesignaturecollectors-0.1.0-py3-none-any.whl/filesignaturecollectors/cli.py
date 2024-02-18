# -*- coding: utf-8 -*-
"""
Run command line interface of PyConcatSRT.
"""


import sys
import argparse

from filesignaturecollectors.controller import Controller


def main():
    parser = argparse.ArgumentParser(
                    prog='collectfilesignatures',
                    description='Collect file signatures from sources.',
                    epilog='An easy way to get file signatures.'
                )

    parser.add_argument(
        '-a',
        '--all',
        action='store_true',
        help='Gets data from all collectors.',
    )
    parser.add_argument(
        '-w',
        '--wiki',
        action='store_true',
        help='Gets data from all collectors.',
    )
    parser.add_argument(
        '-g',
        '--gck',
        action='store_true',
        help='Gets data from all collectors.',
    )

    parser.add_argument(
        '-f',
        '--to_file',
        action='store_true',
        default='file_signatures',
        help='Save the data into a file.',
    )

    parser.add_argument(
        '-db',
        '--to_db',
        action='store_true',
        default='file_signatures.sqlite',
        help='Save the data into a sqlite db.',
    )

    args = parser.parse_args()

    all = args.all
    wiki = args.wiki
    gck = args.gck
    to_file = args.to_file
    to_db = args.to_db

    # print(all, wiki, gck, to_file, to_db)

    # Initializes the counter.
    control = Controller()

    # gets data from source.
    if all or wiki and gck:
        # no_continue = True
        data1 = control.get_data_wiki()
        data2 = control.get_data_gck()
        # filters and concatenates the elements into a single list.
        control.consolidate_data(data1, data2)
    elif wiki:
        data = control.get_data_wiki()
        # single list, it is stored.
        control.consolidate_data(data)
    elif gck:
        data = control.get_data_gck()
        # single list, it is stored.
        control.consolidate_data(data)
    else:
        parser.print_help()
        sys.exit()

    # gets the list of formatted items for storage.
    data_formatted = control.get_dict_data()

    if to_file:
        # saves to normal file.
        control.to_file(data=data_formatted)

    if to_db:
        # saves to sqlite file.
        control.to_db(data=data_formatted)


if __name__ == '__main__':
    main()
