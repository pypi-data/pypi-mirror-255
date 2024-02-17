from robotcloud.api import APIEndPointAuthenticated
from robotcloud.endpoints.organizations import APICallOrganizationProjects
from robotcloud.exceptions import BadUsageException
from robotcloud.typing import RobotCloudProjectDetails


class APICallProjects(APIEndPointAuthenticated):
    def __init__(self, token: str, project_id: str = None):
        self.project_id = project_id
        super().__init__(token)

    def get_endpoint(self):
        if self.project_id is None:
            return "projects/"
        else:
            return f"projects/{self.project_id}"


class APICallProjectUsers(APIEndPointAuthenticated):
    def __init__(self, token: str, project_id: str):
        self.project_id = project_id
        super().__init__(token)

    def get_endpoint(self):
        return f"projects/{self.project_id}/users"


class APIEndpointProjectDevices(APIEndPointAuthenticated):
    def __init__(self, token: str, project_id: str):
        self.project_id = project_id
        super().__init__(token)

    def get_endpoint(self):
        return f"projects/{self.project_id}/devices"


class ProjectApplicationsListAPIEndpoint(APIEndPointAuthenticated):
    def __init__(self, token: str, project_id: str):
        self.project_id = project_id
        super().__init__(token)

    def get_endpoint(self):
        return f"projects/{self.project_id}/applications"


class ProjectApplicationsItemAPIEndpoint(APIEndPointAuthenticated):
    def __init__(self, token: str, project_id: str, application_id: str):
        self.project_id = project_id
        self.application_id = application_id
        super().__init__(token)

    def get_endpoint(self):
        return f"projects/{self.project_id}/applications/{self.application_id}"


def get_project(token, project_id) -> RobotCloudProjectDetails:
    return APICallProjects(token, project_id).get()


def get_projects(token):
    return APICallProjects(token).get()


def update_project(token, project_id, new_data):
    return APICallProjects(token, project_id).put(new_data)


def get_project_users(token, project_id):
    return APICallProjectUsers(token, project_id).get()


def get_project_devices(token, project_id):
    return APIEndpointProjectDevices(token, project_id).get()


def create_project(token, data) -> dict:
    if 'organization_id' not in data or not isinstance(data['organization_id'], str):
        raise BadUsageException("")
    org_id = data['organization_id']
    data.pop('organization_id')
    return APICallOrganizationProjects(token, org_id).post(data)


def delete_project(token, project_id) -> dict:
    return APICallProjects(token, project_id).delete()


def get_project_applications(token, project_id) -> list:
    return ProjectApplicationsListAPIEndpoint(token, project_id).get()


def get_project_application(token, project_id, application_id) -> list:
    return ProjectApplicationsItemAPIEndpoint(token, project_id, application_id).get()


def update_project_application(token, project_id, application_id, data: dict) -> list:
    return ProjectApplicationsItemAPIEndpoint(token, project_id, application_id).put(data)
