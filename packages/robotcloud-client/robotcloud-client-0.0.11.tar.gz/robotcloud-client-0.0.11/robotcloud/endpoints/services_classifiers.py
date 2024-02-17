from dataclasses import asdict

from robotcloud.api import APIEndPointAuthenticated
from robotcloud.utils import Pagination


class ProjectServiceClassifiersAPIEndpoint(APIEndPointAuthenticated):
    def __init__(self, token: str, project_id: str):
        self.project_id = project_id
        super().__init__(token)

    def get_endpoint(self):
        return f"projects/{self.project_id}/classifiers"


class ProjectServiceClassifiersItemAPIEndpoint(APIEndPointAuthenticated):
    def __init__(self, token: str, classifier_id: str):
        self.classifier_id = classifier_id
        super().__init__(token)

    def get_endpoint(self):
        return f"classifiers/{self.classifier_id}"


def get_project_service_classifiers(token, project_id, pagination: Pagination = None,
                                    query_params: dict = None):
    params = {} if pagination is None else asdict(pagination)
    if query_params is not None:
        params.update(query_params)
    return ProjectServiceClassifiersAPIEndpoint(token, project_id).get(params=params)


def post_project_service_classifiers(token, project_id, data: dict):
    return ProjectServiceClassifiersAPIEndpoint(token, project_id).post(data)


def get_classifier(token, classifier_id):
    return ProjectServiceClassifiersItemAPIEndpoint(token, classifier_id).get()


def put_classifier(token, classifier_id, data: dict):
    return ProjectServiceClassifiersItemAPIEndpoint(token, classifier_id).put(data)


def delete_classifier(token, classifier_id):
    return ProjectServiceClassifiersItemAPIEndpoint(token, classifier_id).delete()

