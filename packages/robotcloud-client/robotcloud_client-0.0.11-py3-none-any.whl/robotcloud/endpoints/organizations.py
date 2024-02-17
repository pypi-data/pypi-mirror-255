from robotcloud.constants import SYSTEM_ORGANIZATION_ID
from robotcloud.api import APIEndPointAuthenticated


class APICallOrganization(APIEndPointAuthenticated):
    """
        Implement GET, PUT and DELETE methods
    """
    def __init__(self, token: str, organization_id: str = ''):
        self.organization_id = organization_id
        super().__init__(token)

    def get_endpoint(self):
        return f'organizations/{self.organization_id}'


class APICallOrganizationProjects(APIEndPointAuthenticated):
    def __init__(self, token: str, organization_id: str):
        self.organization_id = organization_id
        super().__init__(token)

    def get_endpoint(self):
        return f"organizations/{self.organization_id}/projects"


class APICallOrganizationUsers(APIEndPointAuthenticated):
    def __init__(self, token: str, organization_id: str):
        self.organization_id = organization_id
        super().__init__(token)

    def get_endpoint(self):
        return f'organizations/{self.organization_id}/users'


def get_organizations(token, with_system: bool = True):
    organizations = APICallOrganization(token).get()
    if not with_system:
        for i, org in enumerate(organizations):
            if org["id"] == SYSTEM_ORGANIZATION_ID:
                del organizations[i]
    return organizations


def create_organization(token, data):
    return APICallOrganization(token).post(data)


def get_organization(token, org_id):
    return APICallOrganization(token, org_id).get()


def update_organization(token, org_id, data):
    return APICallOrganization(token, org_id).put(data)


def delete_organization(token, org_id):
    return APICallOrganization(token, org_id).delete()


def get_organization_projects(token, org_id) -> list:
    return APICallOrganizationProjects(token, org_id).get()


def get_organization_users(token, org_id) -> list:
    return APICallOrganizationUsers(token, org_id).get()
