class User:
    def __init__(self, email: str = '', password: str = '', token: str = ''):
        self.email = email
        self.password = password
        self.token = token
        self.account_id = 0

    def set_account_id(self, account_id):
        self.account_id = account_id
