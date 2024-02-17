from robotcloud.api import APIEndPointAuthenticated


class APICallTag(APIEndPointAuthenticated):
    def __init__(self, token: str, tag_id: str):
        self.tag_id = tag_id
        super().__init__(token)

    def get_endpoint(self):
        return f"tags/{self.tag_id}"


class APICallProjectTags(APIEndPointAuthenticated):
    """
        Implement GET, POST methods
    """
    def __init__(self, token: str, project_id: str):
        self.project_id = project_id
        super().__init__(token)

    def get_endpoint(self):
        return f"projects/{self.project_id}/tags"

    def create_tag(self, data):
        return self.post(data)

    def get_tags(self, parent_tag=None, get_all=False):
        query_params = {
            'parent_tag': parent_tag
        }
        if not get_all:
            query_params['no_parent'] = parent_tag is None

        return self.get(params=query_params)


def get_tag(token, tag_id):
    return APICallTag(token, tag_id).get()


def delete_tag(token, tag_id):
    return APICallTag(token, tag_id).delete()


def update_tag(token, tag_id, data):
    return APICallTag(token, tag_id).put(data)
