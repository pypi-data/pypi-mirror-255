from typing import List

from robotcloud.api import APIEndPointAuthenticated
from robotcloud.typing import RobotCloudNamedItemData


class APICallLocation(APIEndPointAuthenticated):
    def __init__(self, token: str, location_id: str):
        self.location_id = location_id
        super().__init__(token)

    def get_endpoint(self):
        return f"locations/{self.location_id}"


class ProjectLocationsEndpoint(APIEndPointAuthenticated):
    def __init__(self, token: str, project_id: str):
        self.project_id = project_id
        super().__init__(token)

    def get_endpoint(self):
        return f"projects/{self.project_id}/locations"


def create_location(token, project_id, data: dict):
    if 'project_id' in data:
        data.pop('project_id')
    return ProjectLocationsEndpoint(token, project_id).post(data)


def get_project_locations(token, project_id, query_params: dict = None) -> List[RobotCloudNamedItemData]:
    return ProjectLocationsEndpoint(token, project_id).get(params=query_params)


def get_location(token, location_id):
    return APICallLocation(token, location_id).get()


def update_location(token, location_id, data):
    return APICallLocation(token, location_id).put(data)


def delete_location(token, location_id):
    return APICallLocation(token, location_id).delete()
