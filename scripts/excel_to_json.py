#!/usr/bin/python3

"""This script extracts data from an xlsx file and
saves it as a Chronophore-compatible json file.
"""

import argparse
import json
import logging
import openpyxl
import pathlib
from collections import OrderedDict
from datetime import datetime


def get_args():
    parser = argparse.ArgumentParser(
        description="Convert Chronophore data from xlsx to json."
    )

    parser.add_argument('input', help="path of excel file to use as input")

    parser.add_argument(
        '-o', '--output',
        help="path of json file to generate (default: ./$(input_file_name).json)"
    )
    parser.add_argument(
        '-s', '--sheet',
        help="name of sheet in excel spreadsheet (default: use first sheet)"
    )
    parser.add_argument(
        '-c', '--clobber', action="store_true",
        help="overwrite output file if it exists"
    )
    parser.add_argument(
        '-S', '--sort-keys', action="store_true",
        help="sort keys in json output"
    )
    parser.add_argument(
        '-v', '--verbose', action="store_true",
        help="print a detailed log"
    )

    return parser.parse_args()


def excel_to_data(worksheet):
    """Extract and return data from an excel worksheet.
    Preserve ordere by useing an OrderedDict. The values
    in the first column are used as keys, and the values
    in the first row are used as headers.
    """

    data = OrderedDict()

    # NOTE(amin): worksheet.rows is a generator because
    # the workbook was opened with read_only=True. Thus,
    # we use next() (instead of a subscript) to get the
    # first row.
    key_header, *headers = tuple(cell.value for cell in next(worksheet.rows))
    logging.debug("Key Header: '{}', Headers: {}".format(key_header, headers))

    # We continue by iterating over all the remaining rows.
    for row_num, row in enumerate(worksheet.rows, 2):
        entry = OrderedDict()
        key_cell, *value_cells = row
        for header, cell in zip(headers, value_cells):
            if (cell.value is not None):  # openpyxl issue #625
                logging.debug(
                    'Header:{}, Row:{}, Column:{}, Value:{}'.format(
                        header, cell.row, cell.column, cell.value
                    )
                )
                if (cell.is_date):
                    value = datetime.strftime(cell.value, "%Y-%m-%d")
                else:
                    value = cell.value
            else:
                logging.debug(
                    'Header:{}, Row:{}, Value:{}'.format(
                        header, row_num, cell.value
                    )
                )
                value = None

            entry[header] = value
        data[key_cell.value] = entry

    return data


if __name__ == '__main__':
    args = get_args()

    if args.verbose:
        LOGGING_LEVEL = logging.DEBUG
    else:
        LOGGING_LEVEL = logging.WARNING

    logging.basicConfig(
        level=LOGGING_LEVEL,
        format='%(levelname)s:%(asctime)s:%(message)s'
    )

    EXCEL_FILE = pathlib.Path(args.input)
    name = EXCEL_FILE.name

    if args.output:
        JSON_FILE = pathlib.Path(args.output)
    else:
        JSON_FILE = pathlib.Path('.', EXCEL_FILE.stem + '.json')

    CLOBBER = args.clobber
    SORT_KEYS = args.sort_keys

    if not CLOBBER and JSON_FILE.exists():
        logging.warning(
            "{} exists. To overwrite it, use '--clobber'.".format(JSON_FILE)
        )
        raise SystemExit

    wb = openpyxl.load_workbook(
        filename=str(EXCEL_FILE),
        read_only=True,
        data_only=True
    )
    logging.info('Workbook loaded: {}.'.format(EXCEL_FILE))

    WS = wb[args.sheet] if args.sheet else wb.worksheets[0]

    data = excel_to_data(WS)

    with JSON_FILE.open('w') as f:
        json.dump(data, f, indent=4, sort_keys=SORT_KEYS)

    if CLOBBER:
        logging.info("Json saved (file overwritten): {}".format(JSON_FILE))
    else:
        logging.info("Json saved: {}".format(JSON_FILE))
