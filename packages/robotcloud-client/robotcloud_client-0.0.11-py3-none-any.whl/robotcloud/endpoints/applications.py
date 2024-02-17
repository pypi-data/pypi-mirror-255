from robotcloud.api import APIEndPointAuthenticated


class ApplicationRegisterListAPICall(APIEndPointAuthenticated):
    def __init__(self, token: str):
        super().__init__(token)

    def get_endpoint(self):
        return f"application/register/"


class ApplicationRegisterItemAPICall(APIEndPointAuthenticated):
    def __init__(self, token: str, application_id: str):
        self.application_id = application_id
        super().__init__(token)

    def get_endpoint(self):
        return f"application/register/{self.application_id}"


class ApplicationGlobalConfigAPIEndpoint(APIEndPointAuthenticated):
    def __init__(self, token: str):
        super().__init__(token)

    def get_endpoint(self):
        return f"application/configuration/global"


class ApplicationUserConfigAPIEndpoint(APIEndPointAuthenticated):
    def __init__(self, token: str):
        super().__init__(token)

    def get_endpoint(self):
        return f"application/configuration/currentuser"


class ApplicationProjectConfigAPIEndpoint(APIEndPointAuthenticated):
    def __init__(self, token: str, project_id: str):
        self.project_id = project_id
        super().__init__(token)

    def get_endpoint(self):
        return f"application/projects/{self.project_id}/configuration/"


class ApplicationProjectUserConfigAPIEndpoint(APIEndPointAuthenticated):
    def __init__(self, token: str, project_id: str):
        self.project_id = project_id
        super().__init__(token)

    def get_endpoint(self):
        return f"application/projects/{self.project_id}/configuration/currentuser"


def create_application(token, data):
    return ApplicationRegisterListAPICall(token).post(data)


def get_applications(token):
    return ApplicationRegisterListAPICall(token).get()


def get_application(token, application_id):
    return ApplicationRegisterItemAPICall(token, application_id).get()


def update_application(token, application_id, data):
    return ApplicationRegisterItemAPICall(token, application_id).put(data)


def delete_application(token, application_id):
    return ApplicationRegisterItemAPICall(token, application_id).delete()


def get_application_global_config(token: str) -> dict:
    return ApplicationGlobalConfigAPIEndpoint(token).get()


def post_application_global_config(token: str, data: dict):
    return ApplicationGlobalConfigAPIEndpoint(token).post(data)


def get_application_user_config(token: str) -> dict:
    return ApplicationUserConfigAPIEndpoint(token).get()


def post_application_user_config(token: str, data: dict):
    return ApplicationUserConfigAPIEndpoint(token).post(data)


def get_application_project_config(token: str, project_id: str) -> dict:
    return ApplicationProjectConfigAPIEndpoint(token, project_id).get()


def post_application_project_config(token: str, project_id: str, data: dict):
    return ApplicationProjectConfigAPIEndpoint(token, project_id).post(data)


def get_application_user_project_config(token: str, project_id: str):
    return ApplicationProjectUserConfigAPIEndpoint(token, project_id).get()


def post_application_user_project_config(token: str, project_id: str, data: dict):
    return ApplicationProjectUserConfigAPIEndpoint(token, project_id).post(data)
