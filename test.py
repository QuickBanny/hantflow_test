import pytest

from main import UseApi, User
from utils import parse_config_data

config = parse_config_data.parse_config_data()
@pytest.fixture(autouse=True)
def init_objects():
    global test_user
    global api_object
    token = config['USER']['token']
    email = config['USER']['email']
    password = config['USER']['password']

    test_user = User(email=email, password=password, token=token)
    api_object = UseApi(config_api=config['API'], user=test_user)
    yield


def test_account_id():
    account_id = api_object.get_account_id()
    assert account_id != 0
