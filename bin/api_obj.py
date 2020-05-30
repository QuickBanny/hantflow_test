import requests
import json
import http
from googletrans import Translator
from requests import Request
from .user_obj import User


class HuntFlowApi:
    def __init__(self, config_api: dict, user: User, logger):
        self.logger = logger
        self.user = user
        self.host_url = config_api['host_url']
        self.api_get_user_id = config_api['get_user_id']
        self.api_upload_files = config_api['post_upload_files']
        self.api_get_vacancies = config_api['get_vacancies']
        self.api_get_vacancy_statuses = config_api['get_vacancy_statuses']
        self.api_add_applicants = config_api['post_add_applicants']
        self.api_add_applicants_in_vacancy = config_api['post_add_applicants_in_vacancy']

    def upload_files(self, path_to_files: str) -> dict:
        files_id = {"id": 0, 'status': 200}
        url = self.host_url + self.api_upload_files.format(self.user.account_id)
        headers = {
            'Content-Type': 'multipart/form-data',
            'X-File-Parse': 'true',
            'Authorization': 'Bearer {}'.format(self.user.token),
        }
        f = open(path_to_files, 'rb')
        print(path_to_files)
        files = {'file': f}
        #files = {path_to_files: f}
        #files = {os.path.basename(path_to_files): f}
        #print(f.read())
        #print(requests.Request('POST', url, files=files).prepare().body.decode('utf8'))
        #pr = requests.Request('POST', 'http://stackoverflow.com', headers=headers, files=files)
        #self.patch_send()
        print(url)
        response = requests.post(url, files=files, headers=headers)
        #print(response.headers)
        #print(response.request.body)
        #response = Request('POST', url, data=files, headers=headers).prepare()
        #print(response)
        print(response.status_code)
        files_id['status'] = response.status_code
        if response.status_code == 200:
            self.logger.debug('URL: {}, STATUS_CODE: {}'.format(url, response.status_code))
            files_id['id'] = response.json()['id']
            return files_id
        elif response.status_code == 500:
            self.logger.error('URL: {}, STATUS_CODE: {}, BODY:{}'.format(url,
                                                                         response.status_code,
                                                                         response.text))
        return files_id

    def get_account_id(self) -> dict:
        account_id = {"id": 0, 'status': 200}
        headers = {
            'Authorization': 'Bearer {}'.format(self.user.token),
        }
        url = self.host_url + self.api_get_user_id
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            self.logger.debug('URL: {}, STATUS_CODE: {}'.format(url, response.status_code))
            account_id['id'] = int(response.json()['items'][0]['id'])
            return account_id
        else:
            self.logger.error('URL: {}, STATUS_CODE: {}, BODY:{}'.format(url,
                                                                         response.status_code,
                                                                         response.text))
        return account_id

    def get_vacancy_id(self, name_vacancy: str) -> dict:
        vacancy_id = {"id": 0, 'status': 200}
        headers = {
            'Authorization': 'Bearer {}'.format(self.user.token),
        }
        url = self.host_url + self.api_get_vacancies.format(self.user.account_id)
        response = requests.get(url, headers=headers)
        vacancy_id['status'] = response.status_code
        if response.status_code == 200:
            self.logger.debug('URL: {}, STATUS_CODE: {}'.format(url, response.status_code))
            for vacancy in response.json()['items']:
                if vacancy['position'] == name_vacancy:
                    vacancy_id['id'] = vacancy['id']
                    return vacancy_id
        else:
            self.logger.error('URL: {}, STATUS_CODE: {}, BODY:{}'.format(url,
                                                                         response.status_code,
                                                                         response.text))
        return vacancy_id

    def get_vacancy_status_id(self, name_vacancy_status: str) -> dict:
        vacancy_status_id = {"id": 0, 'status': 200}
        headers = {
            'Authorization': 'Bearer {}'.format(self.user.token),
        }
        url = self.host_url + self.api_get_vacancy_statuses.format(self.user.account_id)
        response = requests.get(url, headers=headers)
        vacancy_status_id['status'] = response.status_code
        if response.status_code == 200:
            self.logger.debug('URL: {}, STATUS_CODE: {}'.format(url, response.status_code))
            for vacancy_status in response.json()['items']:
                if vacancy_status['name'] == name_vacancy_status:
                    vacancy_status_id['id'] = vacancy_status['id']
                    return vacancy_status_id
        else:
            self.logger.error('URL: {}, STATUS_CODE: {}, BODY:{}'.format(url,
                                                                         response.status_code,
                                                                         response.text))
        return vacancy_status_id

    def add_applicant_in_db(self, person_fields: dict) -> dict:
        applicant_id = {"id": 0, 'status': 200}
        url = self.host_url + self.api_add_applicants.format(self.user.account_id)
        headers = {
            'Authorization': 'Bearer {}'.format(self.user.token),
        }
        person_fields = person_fields.copy()
        person_fields.pop('full_name')
        data = json.dumps(person_fields)
        response = requests.post(url=url, data=data, headers=headers)
        applicant_id['status'] = response.status_code
        if response.status_code == 200:
            self.logger.debug('URL: {}, STATUS_CODE: {}'.format(url, response.status_code))
            applicant_id['id'] = response.json()['id']
            return applicant_id
        else:
            self.logger.error('URL: {}, STATUS_CODE: {}, BODY:{}'.format(url,
                                                                         response.status_code,
                                                                         response.text))
        return applicant_id

    def add_applicant_in_vacancy(self, applicant_id: int, vacancy_fields: dict) -> dict:
        applicant_in_vacancy_id = {"id": 0, 'status': 200}
        url = self.host_url + self.api_add_applicants_in_vacancy.format(self.user.account_id, applicant_id)
        headers = {
            'Authorization': 'Bearer {}'.format(self.user.token),
        }
        data = json.dumps(vacancy_fields)
        response = requests.post(url=url, data=data, headers=headers)
        applicant_in_vacancy_id['status'] = response.status_code
        if response.status_code == 200:
            self.logger.debug('URL: {}, STATUS_CODE: {}'.format(url, response.status_code))
            applicant_in_vacancy_id['id'] = response.json()['id']
            return applicant_in_vacancy_id
        else:
            self.logger.error('URL: {}, STATUS_CODE: {}, BODY:{}'.format(url,
                                                                         response.status_code,
                                                                         response.text))
        return applicant_in_vacancy_id

