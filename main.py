import sys
import os
import xlrd
import json
from utils import parse_config_data
import requests

config = parse_config_data.parse_config_data()


def print_error_msg(url, status_code):
    print(url, status_code)


class User:
    def __init__(self, email: str = '', password: str = '', token: str = ''):
        self.email = email
        self.password = password
        self.token = token
        self.account_id = 0

    def set_account_id(self, account_id):
        self.account_id = account_id


class UseApi:
    def __init__(self, config_api: dict, user: User):
        self.config = config
        self.user = user
        self.host_url = config_api['host_url']
        self.api_get_user_id = config_api['get_user_id']
        self.api_upload_files = config_api['post_upload_files']
        self.api_get_vacancies = config_api['get_vacancies']
        self.api_get_vacancy_statuses = config_api['get_vacancy_statuses']
        self.api_add_applicants = config_api['post_add_applicants']
        self.api_add_applicants_in_vacancy = config_api['post_add_applicants_in_vacancy']

    def upload_files(self, path_to_files: str) -> dict:
        files_id = {"id": 0}
        url = self.host_url + self.api_upload_files.format(self.user.account_id)
        headers = {
            'Content-Type': 'multipart/form-data',
            'X-File-Parse': 'true',
            'Authorization': 'Bearer {}'.format(self.user.token),
        }
        files = {'file': open(path_to_files, 'rb')}
        response = requests.post(url, headers=headers, files=files,)
        if response.status_code == 200:
            files_id = {'id': response.json()['id']}
        else:
            print_error_msg(url, response.status_code)
        return files_id

    def get_account_id(self) -> int:
        account_id = 0
        headers = {
            'User-Agent': 'App/1.0 (maiorovpavel@gmail.com)',
            'Host': 'api.huntflow.ru',
            'Accept': '*/*',
            'Authorization': 'Bearer {}'.format(self.user.token)
        }
        url = self.host_url + self.api_get_user_id
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            account_id = response.json()['id']
            return account_id
        else:
            print_error_msg(url, response.status_code)
        return account_id

    def get_vacancy_id(self, name_vacancy: str) -> int:
        vacancy_id = 0
        url = self.host_url + self.api_get_vacancies.format(self.user.account_id)
        response = requests.get(url)
        if response.status_code == 200:
            for vacancy in response.json():
                if vacancy['position'] == name_vacancy:
                    return vacancy['id']
        else:
            print_error_msg(url, response.status_code)
        return vacancy_id

    def get_vacancy_status_id(self, name_vacancy_status: str) -> int:
        vacancy_status_id = 0
        url = self.host_url + self.api_get_vacancy_statuses.format(self.user.account_id)
        response = requests.get(url)
        if response.status_code == 200:
            for vacancy_status in response.json():
                if vacancy_status['name'] == name_vacancy_status:
                    return vacancy_status['id']
        else:
            print_error_msg(url, response.status_code)
        return vacancy_status_id

    def add_applicant_in_db(self, person_fields: dict) -> int:
        applicant_id = 0
        url = self.host_url + self.api_add_applicants.format(self.user.account_id)
        person_fields = person_fields.copy()
        person_fields.pop('full_name')
        params = person_fields

        response = requests.post(url=url, params=params)
        if response.status_code == 200:
            for applicant in response.json():
                applicant_id = applicant['id']
                return applicant_id
        else:
            print_error_msg(url, response.status_code)
        return applicant_id

    def add_applicant_in_vacancy(self, applicant_id: int, vacancy_fields: dict):
        applicant_in_vacancy_id = 0
        url = self.host_url + self.api_add_applicants_in_vacancy.format(self.user.account_id, applicant_id)
        params = vacancy_fields
        response = requests.post(url=url, params=params)
        if response.status_code == 200:
            for applicant_in_vacancy in response.json():
                applicant_in_vacancy_id = applicant_in_vacancy['id']
                return applicant_in_vacancy_id
        else:
            print_error_msg(url, response.status_code)
        return applicant_in_vacancy_id


def parse_test_db(file_name_db: str, path_to_db: str, position: int):
    row = 0
    try:
        wb_read = xlrd.open_workbook(os.path.join(path_to_db, file_name_db))
        ws_read = wb_read.sheet_by_name('Лист1')
        for row in range(ws_read.nrows)[position+1:]:
            person_fields = {}
            vacancy_fields = {}
            try:
                person_fields['position'] = ws_read.cell(row, 0).value
                full_name = ws_read.cell(row, 1).value
                full_name_list = parse_full_name(full_name)
                try:
                    person_fields['last_name'] = full_name_list[0]
                except Exception:
                    print("NO Last_name:", sys.exc_info()[0])
                    raise
                try:
                    person_fields['first_name'] = full_name_list[1]
                except Exception:
                    print("NO First_name:", sys.exc_info()[0])
                    raise
                try:
                    person_fields['middle_name'] = full_name_list[2]
                except Exception:
                    pass
                person_fields['full_name'] = full_name
                person_fields['money'] = str(ws_read.cell(row, 2).value)
                vacancy_fields['comment'] = ws_read.cell(row, 3).value
                vacancy_fields['status'] = ws_read.cell(row, 4).value
                yield person_fields, vacancy_fields
            except:
                print('ERROR: POSITION in DB: ', row)
                yield {}, {}
    except Exception as es:
        print(es)
        print('ERROR: POSITION in DB: ', row)


def parse_full_name(full_name: str) -> list:
    return full_name.split()


def find_resume_files(person_fields: dict, api_object: UseApi, path_to_db: str) -> list:
    resume_files = []
    try:
        path_to_position = os.path.join(path_to_db, person_fields['position'])
        for file in os.listdir(path_to_position):
            if person_fields['full_name'] in file:
                resume_files.append(api_object.upload_files(os.path.join(path_to_position, file)))
    except Exception as es:
        print('FILES')
        print(es)
    return resume_files


def main(argv):
    token = ''
    path_to_db = ''
    position = 0
    email = config['USER']['email']
    password = config['USER']['password']
    file_name_db = config['PATH']['file_name_db']
    try:
        token = argv[0]
        path_to_db = argv[1]
        position = int(argv[2])
    except Exception as es:
        print(es)
    token = config['USER']['token']

    test_user = User(email=email, password=password, token=token)
    api_object = UseApi(config_api=config['API'], user=test_user)
    account_id = api_object.get_account_id()
    test_user.set_account_id(account_id)
    for person_fields, vacancy_fields in parse_test_db(file_name_db=file_name_db, path_to_db=path_to_db, position=position):
        if not person_fields or not vacancy_fields:
            print('Not person_fields or vacancy_fields')
        else:
            externals = []
            files_resume = find_resume_files(person_fields=person_fields, api_object=api_object, path_to_db=path_to_db)
            if files_resume:
                externals.append({'files': files_resume})
                person_fields['externals'] = externals
            applicant_id = api_object.add_applicant_in_db(person_fields)
            if not applicant_id:
                print("Error with add applicant")
            else:
                pass
            vacancy_id = api_object.get_vacancy_id(name_vacancy=person_fields['position'])
            vacancy_status_id = api_object.get_vacancy_status_id(name_vacancy_status=vacancy_fields['status'])
            if not vacancy_id or not vacancy_status_id:
                print("Not vacancy or Not vacancy_status in DB")
            else:
                vacancy_fields['vacancy'] = vacancy_id
                vacancy_fields['status'] = vacancy_status_id
                api_object.add_applicant_in_vacancy(applicant_id=applicant_id, vacancy_fields=vacancy_fields)
        print('----------------------------------------------------------------------------------------')


if __name__ == '__main__':
    main(sys.argv[1:])