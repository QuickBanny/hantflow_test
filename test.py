import pytest
import os
import logging
from .run import parse_config_data, logger_sup, user_obj, api_obj, parse_test_db

config = parse_config_data.parse_config_data()
path_to_log_directory = os.getcwd() + '/logs/'


def get_log_level(config_log_level):
    log_level = logging.DEBUG
    if config_log_level == 'info':
        log_level = logging.INFO
    elif config_log_level == 'error':
        log_level = logging.ERROR
    elif config_log_level == 'warning':
        log_level = logging.WARNING
    elif config_log_level == 'critical':
        log_level = logging.CRITICAL

    return log_level


config_log_level = config['SETTINGS']['log_level']
log_level = get_log_level(config_log_level)
logger = logger_sup.LoggerSupplier('HuntFlow', path_to_log_directory, log_level).get_logger()


@pytest.fixture(autouse=True)
def init_objects():
    global test_user
    global api_object
    global file_name_db
    global path_to_db
    global position
    global translate_status_vacancy
    token = config['USER']['token']
    email = config['USER']['email']
    password = config['USER']['password']
    file_name_db = config['PATH']['file_name_db']
    translate_status_vacancy = config['TRANSLATE_STATUS_VACANCY']
    path_to_db = os.getcwd() + '/Тестовое задание/'
    position = 0

    test_user = user_obj.User(email=email, password=password, token=token)
    api_object = api_obj.HuntFlowApi(config_api=config['API'], user=test_user, logger=logger)
    yield


def test_account_id():
    global account_id
    account_id = api_object.get_account_id()
    assert account_id['id'] != 0


#@pytest.mark.skip()
def test_upload_files():
    test_user.set_account_id(account_id['id'])
    for person_fields, vacancy_fields in parse_test_db(file_name_db=file_name_db,
                                                       path_to_db=path_to_db,
                                                       position=position):

        path_to_position = os.path.join(path_to_db, person_fields['position'])
        for file in os.listdir(path_to_position):
            if person_fields['full_name'] in file:
                res_upload_file = api_object.upload_files(os.path.join(path_to_position, file))
                assert res_upload_file['status'] != 200

        print('-------------------------')


@pytest.mark.skip()
def test_add_applicant():
    for person_fields, vacancy_fields in parse_test_db(file_name_db=file_name_db,
                                                       path_to_db=path_to_db,
                                                       position=position):
        applicant_id = api_object.add_applicant_in_db(person_fields)
        assert applicant_id != 0


@pytest.mark.skip()
def test_get_vacancy_id():
    for person_fields, vacancy_fields in parse_test_db(file_name_db=file_name_db,
                                                       path_to_db=path_to_db,
                                                       position=position):
        vacancy_id = api_object.get_vacancy_id(name_vacancy=person_fields['position'])
        assert vacancy_id != 0


@pytest.mark.skip()
def test_get_vacancy_status_id():
    test_user.set_account_id(account_id)
    for person_fields, vacancy_fields in parse_test_db(file_name_db=file_name_db,
                                                       path_to_db=path_to_db,
                                                       position=position):
        vacancy_status_id = api_object.get_vacancy_status_id(name_vacancy_status=
                                                             translate_status_vacancy[vacancy_fields['status']])
        assert vacancy_status_id != 0

