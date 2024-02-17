from robotcloud.api import APIEndPointAuthenticated


class APICallProjectSubsystems(APIEndPointAuthenticated):
    def __init__(self, token: str, project_id: str, subsystem_id: str = None):
        self.project_id = project_id
        self.subsystem_id = subsystem_id
        super().__init__(token)

    def get_endpoint(self):
        if self.subsystem_id is None:
            return f"projects/{self.project_id}/subsystems"
        else:
            return f"projects/{self.project_id}/subsystems/{self.subsystem_id}"


def get_project_subsystems(token, project_id) -> list:
    return APICallProjectSubsystems(token, project_id).get()


def create_subsystem(token, project_id, data):
    return APICallProjectSubsystems(token, project_id).post(data)


def get_subsystem_details(token, project_id, subsystem_id):
    return APICallProjectSubsystems(token, project_id, subsystem_id).get()


def edit_subsystem(token, project_id, subsystem_id, data):
    return APICallProjectSubsystems(token, project_id, subsystem_id).put(data)


def delete_subsystem(token, project_id, subsystem_id):
    return APICallProjectSubsystems(token, project_id, subsystem_id).delete()
