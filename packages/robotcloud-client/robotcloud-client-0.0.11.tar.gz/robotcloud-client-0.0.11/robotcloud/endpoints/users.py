from dataclasses import asdict

from robotcloud.api import APIEndPointAuthenticated
from robotcloud.endpoints.organizations import APICallOrganizationUsers
from robotcloud.utils import Pagination


class APICallUser(APIEndPointAuthenticated):
    """
        Implement GET, PUT and DELETE methods
    """
    def __init__(self, token: str, username: str = ''):
        self.username = username
        super().__init__(token)

    def get_endpoint(self):
        return f'users/{self.username}'


class APICallUserProjects(APIEndPointAuthenticated):
    """
        Implement GET, PUT and DELETE methods
    """
    def __init__(self, token: str, username: str, project_id: str = ''):
        self.username = username
        self.project_id = project_id
        super().__init__(token)

    def get_endpoint(self):
        return f'users/{self.username}/projects/{self.project_id}'


class APICallUserOrganizations(APIEndPointAuthenticated):
    def __init__(self, token: str, username: str):
        self.username = username
        super().__init__(token)

    def get_endpoint(self):
        return f"users/{self.username}/organizations"


def get_all_users(token, pagination: Pagination = None, query_params: dict = None):
    params = {} if pagination is None else asdict(pagination)
    if query_params is not None:
        params.update(query_params)
    return APICallUser(token).get(params=params)


def get_user(token, username):
    return APICallUser(token, username).get()


def put_user(token, username, data):
    return APICallUser(token, username).put(data)


def delete_user(token, username):
    return APICallUser(token, username).delete()


def get_user_projects(token, username):
    return APICallUserProjects(token, username).get()


def post_user_project(token, username, data):
    return APICallUserProjects(token, username).post(data)


def update_user_project(token, username, project_id, data):
    return APICallUserProjects(token, username, project_id).put(data)


def delete_user_project(token, username, project_id):
    return APICallUserProjects(token, username, project_id).delete()


def create_user(token, organization_id, data):
    return APICallOrganizationUsers(token, organization_id).post(data)


def get_user_organizations(token, username):
    return APICallUserOrganizations(token, username).get()
