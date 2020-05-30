import sys
import os
import xlrd
from .utils import parse_config_data, logger_sup
from .bin import api_obj, user_obj
import logging
import requests
import http
from googletrans import Translator
from requests import Request
from requests_toolbelt.multipart.encoder import MultipartEncoder


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


config = parse_config_data.parse_config_data()
path_to_log_directory = os.getcwd() + '/logs/'
email = config['USER']['email']
password = config['USER']['password']
file_name_db = config['PATH']['file_name_db']
translate_status_vacancy = config['TRANSLATE_STATUS_VACANCY']
config_log_level = config['SETTINGS']['log_level']
log_level = get_log_level(config_log_level)
logger = logger_sup.LoggerSupplier('HuntFlow', path_to_log_directory, log_level).get_logger()


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
                    logger.error('Нет фамилии: ', sys.exc_info()[0])
                    raise
                try:
                    person_fields['first_name'] = full_name_list[1]
                except Exception:
                    logger.error('Нет имени: ', sys.exc_info()[1])
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
                logger.error('Ошибка при добавлении кандидата на позиции: ', row)
                yield {}, {}
    except Exception as es:
        logger.error('Ошибка при добавлении кандидата на позиции: ', row)
        logger.error(es)


def parse_full_name(full_name: str) -> list:
    return full_name.split()


def find_resume_files(person_fields: dict, api_object: api_obj.HuntFlowApi, path_to_db: str) -> list:
    resume_files = []
    try:
        path_to_position = os.path.join(path_to_db, person_fields['position'])
        for file in os.listdir(path_to_position):
            if person_fields['full_name'] in file:
                res_upload_file = api_object.upload_files(os.path.join(path_to_position, file))
                if res_upload_file['status'] == 200:
                    res_upload_file.pop('status')
                    resume_files.append(res_upload_file)
    except Exception as es:
        logger.error('Ошибка при поиске файла резюме кандидата: {}'.format(person_fields['full_name']))
        logger.error(es)
    return resume_files


def main(argv):
    token = ''
    path_to_db = ''
    position = 0
    try:
        token = argv[0]
        path_to_db = argv[1]
        position = int(argv[2])
    except Exception as es:
        logger.error('Ошибка при вводе начальных параметров')

    token = config['USER']['token']
    path_to_db = config['PATH']['path_to_db_dir']
    test_user = user_obj.User(email=email, password=password, token=token)
    api_object = api_obj.HuntFlowApi(config_api=config['API'], user=test_user, logger=logger)
    account_id = api_object.get_account_id()
    if account_id['status'] != 200:
        logger.error('Ошибка при получении account_id')
    else:
        logger.debug('Успешное получение account_id')
        test_user.set_account_id(account_id['id'])
        for person_fields, vacancy_fields in parse_test_db(file_name_db=file_name_db,
                                                           path_to_db=path_to_db,
                                                           position=position):
            if not person_fields or not vacancy_fields:
                logger.error('Нет персональных данных или данных о вакансии {comment, status}')
            else:
                logger.debug('Успешное получение данных о кандидате: {}'.format(person_fields['full_name']))
                externals = []
                files_resume = find_resume_files(person_fields=person_fields,
                                                 api_object=api_object,
                                                 path_to_db=path_to_db)
                if files_resume:
                    logger.debug('Найдет фаил резюме для кандидата: {}'.format(person_fields['full_name']))
                    externals.append({'files': files_resume})
                    person_fields['externals'] = externals
                applicant_id = api_object.add_applicant_in_db(person_fields)
                if applicant_id['status'] != 200:
                    logger.error('Ошибка при добавлении в базу кандидата: {}'.format(person_fields['full_name']))
                else:
                    logger.debug('Успешное добавления в базу кандидата: {}'.format(person_fields['full_name']))
                    vacancy_id = api_object.get_vacancy_id(name_vacancy=person_fields['position'])
                    vacancy_status_id = api_object.get_vacancy_status_id(name_vacancy_status=
                                                                         translate_status_vacancy
                                                                         [vacancy_fields['status']])
                    if vacancy_id['status'] != 200:
                        logger.error("Нет вакансии в DB")
                    elif vacancy_status_id['status'] != 200:
                        logger.erro("Нет этапа подбора в DB")
                    else:
                        logger.debug("Успешное получение id_вакансии и id_этапа_подбора")
                        vacancy_fields['vacancy'] = vacancy_id['id']
                        vacancy_fields['status'] = vacancy_status_id['id']
                        applicant_in_vacancy_id = api_object.add_applicant_in_vacancy(applicant_id=applicant_id['id'],
                                                                                      vacancy_fields=vacancy_fields)
                        if applicant_in_vacancy_id['status'] != 200:
                            logger.error("Ошибка при добавлении кандидата на вакансию")
                        else:
                            logger.info('Успешное добваление кандидата {} на вакансию {}'.format(
                                person_fields['full_name'], person_fields['position']))

            logger.info('----------------------------------------------------------------------------------------')


if __name__ == '__main__':
    main(sys.argv[1:])