import sys
import xlrd
import json


def parse_test_db(path_to_db: str):
    row = 1
    try:
        wb_read = xlrd.open_workbook(path_to_db)
        ws_read = wb_read.sheet_by_name('Лист1')
        for row in range(ws_read.nrows)[1:]:
            pos = ws_read.cell(row, 0).value
            full_name = ws_read.cell(row, 1).value
            salary = ws_read.cell(row, 2).value
            comments = ws_read.cell(row, 3).value
            status = ws_read.cell(row, 4).value
            yield row, pos, full_name, salary, comments, status
    except Exception as es:
        print(es)
        print('POSITION in DB: ', row)


def add_person_in_db(token: str, body: json):
    pass


def add_person_in_vacancy(token: str, body:json):
    pass


def main(argv):
    position = ''
    token = ''
    path_to_db = ''
    try:
        token = argv[0]
        path_to_db = argv[1]
        position = argv[2]
    except Exception as es:
        print(es)

    for row, pos, full_name, salary, comments, status in parse_test_db(path_to_db):
        print(row, pos, full_name, salary, comments, status)


if __name__ == '__main__':
    main(sys.argv[1:])