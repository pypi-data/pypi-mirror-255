from robotcloud.api import APIEndPointAuthenticated, APIEndPointUnAuthenticated


class LoginEndpoint(APIEndPointUnAuthenticated):
    def __init__(self, username: str, password: str):
        super().__init__(username, password)

    def get_endpoint(self):
        return "login"


class LoginRenewEndpoint(APIEndPointAuthenticated):
    def __init__(self, token: str):
        super().__init__(token)

    def get_endpoint(self):
        return "login/renew"


def login_user(username: str, password: str):
    return LoginEndpoint(username, password).get()


def login_renew(token):
    return LoginRenewEndpoint(token).get()
