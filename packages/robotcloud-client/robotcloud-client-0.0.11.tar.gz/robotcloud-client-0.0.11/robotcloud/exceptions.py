class RobotcloudRequestError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'An undefined Robotcloud API response: {self.message}'


class UnauthorizedAccessError(RobotcloudRequestError):

    def __str__(self):
        return f'Unauthorized access: {self.message}'


class NotFoundError(RobotcloudRequestError):

    def __str__(self):
        return 'Not found resource'


class ForbiddenError(RobotcloudRequestError):

    def __str__(self):
        return f'Forbidden access: {self.message}'


class BadRequestError(RobotcloudRequestError):

    def __str__(self):
        return 'Bad request'


class InternalServerError(RobotcloudRequestError):

    def __str__(self):
        return f'Internal server error: {self.message}'


class InvalidServiceNameException(Exception):

    def __str__(self):
        return 'Service name is not valid'


class RequestConnectionError(RobotcloudRequestError):

    def __str__(self):
        return f'Request connection error: {self.message}'


class BadUsageException(RobotcloudRequestError):
    """
    Exception raised when a method is called improperly

    """
    def __str__(self):
        return f'Bad usage exception: {self.message}'
