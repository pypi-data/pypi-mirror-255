from typing import List
from dataclasses import asdict

from robotcloud.api import APIEndPointAuthenticated
from robotcloud.utils import Pagination
from robotcloud.typing import RobotCloudServiceInstance


class APICallLocationServices(APIEndPointAuthenticated):
    """
        Implement GET methods
    """

    def __init__(self, token: str, project_id: str, location_id: str):
        self.project_id = project_id
        self.location_id = location_id
        super().__init__(token)

    def get_endpoint(self):
        return f'projects/{self.project_id}/locations/{self.location_id}/services'


class APICallLocationServicesInstances(APIEndPointAuthenticated):
    """
        Implement GET, POST methods
    """

    def __init__(self, token: str, project_id: str, location_id: str, service_type: str):
        self.project_id = project_id
        self.location_id = location_id
        self.service_type = service_type
        super().__init__(token)

    def get_endpoint(self):
        return f'projects/{self.project_id}/locations/{self.location_id}/services/{self.service_type}/instances'


class APICallProjectServicesInstances(APIEndPointAuthenticated):
    """
        Implement GET methods
    """

    def __init__(self, token: str, project_id: str):
        self.project_id = project_id
        super().__init__(token)

    def get_endpoint(self):
        return f'projects/{self.project_id}/instances'


class APICallProjectServices(APIEndPointAuthenticated):
    """
        Implement GET methods
    """

    def __init__(self, token: str, project_id: str):
        self.project_id = project_id
        super().__init__(token)

    def get_endpoint(self):
        return f'projects/{self.project_id}/services'


class APICallProjectServiceInstances(APIEndPointAuthenticated):
    """
        Implement GET, PUT, DELETE methods
    """

    def __init__(self, token: str, project_id: str, service_type: str, instance_id: str = None):
        self.project_id = project_id
        self.service_type = service_type
        self.instance_id = instance_id
        super().__init__(token)

    def get_endpoint(self):
        if self.instance_id is None:
            return f'projects/{self.project_id}/services/{self.service_type}/instances'
        else:
            return f'projects/{self.project_id}/services/{self.service_type}/instances/{self.instance_id}'


class APICallCountProjectServiceInstances(APIEndPointAuthenticated):
    """
        Implement GET, PUT, DELETE methods
    """

    def __init__(self, token: str, project_id: str, service_type: str, instance_id: str = None):
        self.project_id = project_id
        self.service_type = service_type
        self.instance_id = instance_id
        super().__init__(token)

    def get_endpoint(self):
        if self.instance_id is None:
            return f'size/projects/{self.project_id}/services/{self.service_type}/instances'
        else:
            return f'size/projects/{self.project_id}/services/{self.service_type}/instances/{self.instance_id}'


class APICallServiceInstanceDeviceConfig(APIEndPointAuthenticated):
    """
        Implement GET, PUT methods
    """

    def __init__(self, token: str, project_id: str, service_type: str, instance_id: str = None):
        self.project_id = project_id
        self.service_type = service_type
        self.instance_id = instance_id
        super().__init__(token)

    def get_endpoint(self):
        return f'projects/{self.project_id}/services/{self.service_type}/instances/{self.instance_id}/deviceconf'


SERVICES_TYPES = [
    {'code': 'AirHandlingUnit_1', 'description': 'Air Handling Unit v1'},
    {'code': 'AirQuality_1', 'description': 'Air Quality v1', 'groups': ['rooms']},
    {'code': 'ChillerHeatingPump_1', 'description': 'Chiller Heating Pump v1'},

    {'code': 'CoolHeatProd_1', 'description': 'Cool & Heat Producer v1'},
    {'code': 'CoolHeatCons_1', 'description': 'Cool & Heat Consumer v1'},
    {'code': 'CoolHeatTemperature_1', 'description': 'Cool & Heat Temperature v1'},

    {'code': 'EnergyCounter_1', 'description': 'Energy Counter v1'},
    {'code': 'EnergyProduction_1', 'description': 'Energy Production v1'},

    {'code': 'GasCounter_1', 'description': 'Gas Counter v1'},

    {'code': 'GenericTemperature_1', 'description': 'Generic Temperature v1'},

    {'code': 'HeatMeter_1', 'description': 'Heat Meter v1'},
    {'code': 'HeatProd_1', 'description': 'Heat Producer v1'},
    {'code': 'OutdoorClime_1', 'description': 'OutdoorClime_1'},
    {'code': 'PowerMeter_1', 'description': 'Power Meter v1'},
    {'code': 'RoomClime_1', 'description': 'Room Clime v1', 'groups': ['rooms']},
    {'code': 'RoomConsumes_1', 'description': 'Room Consumes v1', 'groups': ['rooms']},
    {'code': 'RoomBLEPairing_1', 'description': 'Room Bluetooth Low Energy Pairing v1', 'groups': ['rooms']},
    {'code': 'RoomGrouping_1', 'description': 'Room Grouping v1'},

    {'code': 'RoomDiagnostics_1', 'description': 'Room Diagnostics v1', 'groups': ['rooms']},
    {'code': 'RoomGuestStatus_1', 'description': 'Room Guest Status v1', 'groups': ['rooms']},
    {'code': 'TemporizedOutput_1', 'description': 'Temporized Output v1'},
    {'code': 'WaterCounter_1', 'description': 'Water Counter v1'},
]


def get_services_types(token):
    return SERVICES_TYPES


def get_services_types_by_group(token, group: str):
    return [svc_type for svc_type in SERVICES_TYPES if 'groups' in svc_type and group in svc_type['groups']]


def get_location_services(token, project_id, location_id):
    return APICallLocationServices(token, project_id, location_id).get()


def get_location_services_instances(token, project_id, location_id, service_type):
    return APICallLocationServicesInstances(token, project_id, location_id, service_type).get()


def create_location_services_instance(token, project_id, location_id, service_type, data):
    return APICallLocationServicesInstances(token, project_id, location_id, service_type).post(data)


def get_project_services_instances(token, project_id, params=None) -> List[RobotCloudServiceInstance]:
    if params is None:
        params = {}
    return APICallProjectServicesInstances(token, project_id).get(params=params)


def get_project_services(token, project_id):
    return APICallProjectServices(token, project_id).get()


def get_project_service_instances(token, project_id, service_type, pagination: Pagination = None,
                                  query_params: dict = None) -> List[RobotCloudServiceInstance]:
    params = {} if pagination is None else asdict(pagination)
    if query_params is not None:
        params.update(query_params)
    return APICallProjectServiceInstances(token, project_id, service_type).get(params=params)


def count_project_service_instances(token, project_id, service_type, pagination: Pagination = None,
                                    query_params: dict = None):
    params = {} if pagination is None else asdict(pagination)
    if query_params is not None:
        params.update(query_params)
    return APICallCountProjectServiceInstances(token, project_id, service_type).get(params=params)


def get_service_instance_details(token, project_id, service_type, instance_id):
    return APICallProjectServiceInstances(token, project_id, service_type, instance_id).get()


def edit_service_instance(token, project_id, service_type, instance_id, data):
    return APICallProjectServiceInstances(token, project_id, service_type, instance_id).put(data)


def delete_service_instance(token, project_id, service_type, instance_id):
    return APICallProjectServiceInstances(token, project_id, service_type, instance_id).delete()


def get_service_instance_dev_conf(token, project_id, service_type, instance_id):
    return APICallServiceInstanceDeviceConfig(token, project_id, service_type, instance_id).get()


def edit_service_instance_dev_conf(token, project_id, service_type, instance_id, data):
    return APICallServiceInstanceDeviceConfig(token, project_id, service_type, instance_id).put(data)
