from robotcloud.api import APIEndPointAuthenticated


class APICallProjectConfigTypes(APIEndPointAuthenticated):
    """
        Implement GET, POST methods
    """
    def __init__(self, token: str, project_id: str):
        self.project_id = project_id
        super().__init__(token)

    def get_endpoint(self):
        return f'projects/{self.project_id}/configurationtypes'


class APICallConfigType(APIEndPointAuthenticated):
    """
        Implement GET, PUT, DELETE methods
    """
    def __init__(self, token: str, configuration_type_id: str):
        self.configuration_type_id = configuration_type_id
        super().__init__(token)

    def get_endpoint(self):
        return f'configurationtypes/{self.configuration_type_id}'


class APICallConfigTypeServices(APIEndPointAuthenticated):
    """
        Implement GET method
    """
    def __init__(self, token: str, configuration_type_id: str):
        self.configuration_type_id = configuration_type_id
        super().__init__(token)

    def get_endpoint(self):
        return f'configurationtypes/{self.configuration_type_id}/services'


class APICallConfigTypeServiceConfig(APIEndPointAuthenticated):
    """
        Implement GET, PUT methods
    """
    def __init__(self, token: str, configuration_type_id: str, service_configuration_id: str):
        self.configuration_type_id = configuration_type_id
        self.service_configuration_id = service_configuration_id
        super().__init__(token)

    def get_endpoint(self):
        return f'configurationtypes/{self.configuration_type_id}/services/{self.service_configuration_id}'


def get_project_config_types(token, project_id):
    return APICallProjectConfigTypes(token, project_id).get()


def post_project_config_types(token, project_id, data):
    return APICallProjectConfigTypes(token, project_id).post(data)


def get_config_type(token, configuration_type_id):
    return APICallConfigType(token, configuration_type_id).get()


def put_config_type(token, configuration_type_id, data):
    return APICallConfigType(token, configuration_type_id).put(data)


def delete_config_type(token, configuration_type_id):
    return APICallConfigType(token, configuration_type_id).delete()


def get_config_type_services(token, configuration_type_id):
    return APICallConfigTypeServices(token, configuration_type_id).get()


def get_config_type_service_config(token, configuration_type_id, service_configuration_id):
    return APICallConfigTypeServiceConfig(token, configuration_type_id, service_configuration_id).get()


def put_config_type_service_config(token, configuration_type_id, service_configuration_id, data):
    return APICallConfigTypeServiceConfig(token, configuration_type_id, service_configuration_id).put(data)
