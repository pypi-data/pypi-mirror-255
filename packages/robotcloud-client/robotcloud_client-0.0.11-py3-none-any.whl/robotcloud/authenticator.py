from abc import ABC, abstractmethod
from base64 import b64encode


class Authenticator(ABC):
    @abstractmethod
    def compute_string(self):
        pass


class BasicAuthenticator(Authenticator):
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def compute_string(self):
        s = f"{self.username}:{self.password}"
        encoding = "utf-8"
        encoded = s.encode(encoding)
        base64_encoded = b64encode(encoded)
        decoded = base64_encoded.decode(encoding)
        return f"Basic {decoded}"


class BearerAuthenticator(Authenticator):
    def __init__(self, token: str):
        self.token = token

    def compute_string(self):
        return f"Bearer {self.token}"
