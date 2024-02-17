from robotcloud.api import APIEndPointAuthenticated
from robotcloud.typing import RobotCloudDeviceDetails


class APICallLocationDevices(APIEndPointAuthenticated):
    """
        Implement GET, POST methods
    """
    def __init__(self, token: str, location_id: str):
        self.location_id = location_id
        super().__init__(token)

    def get_endpoint(self):
        return f'locations/{self.location_id}/devices'


class APICallProjectDevices(APIEndPointAuthenticated):
    """
        Only implement GET
    """
    def __init__(self, token: str, project_id: str):
        self.project_id = project_id
        super().__init__(token)

    def get_endpoint(self):
        return f'projects/{self.project_id}/devices'


class APICallDevices(APIEndPointAuthenticated):
    """
        Implement GET, PUT and DELETE methods
    """
    def __init__(self, token: str, device_id: str):
        self.device_id = device_id
        super().__init__(token)

    def get_endpoint(self):
        return f'devices/{self.device_id}'


class APICallDeviceCompatibleConfigTypes(APIEndPointAuthenticated):
    """
        Implement GET methods
    """
    def __init__(self, token: str, device_id: str):
        self.device_id = device_id
        super().__init__(token)

    def get_endpoint(self):
        return f'devices/{self.device_id}/compatibleconfigurationtypes'


def get_location_devices(token, location_id):
    return APICallLocationDevices(token, location_id).get()


def post_location_device(token, location_id, data):
    """ Create a device in location """
    return APICallLocationDevices(token, location_id).post(data)


def get_project_devices(token, project_id, query_params=None):
    query_params = {} if query_params is None else query_params
    return APICallProjectDevices(token, project_id).get(params=query_params)


def get_device(token, device_id) -> RobotCloudDeviceDetails:
    return APICallDevices(token, device_id).get()


def edit_device(token, device_id, data):
    return APICallDevices(token, device_id).put(data)


def delete_device(token, device_id):
    return APICallDevices(token, device_id).delete()


def get_device_compatible_configuration_types(token, device_id):
    return APICallDeviceCompatibleConfigTypes(token, device_id).get()
