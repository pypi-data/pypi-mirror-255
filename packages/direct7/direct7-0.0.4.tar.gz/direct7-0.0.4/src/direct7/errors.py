class AuthenticationError(Exception):
    def __init__(self, message):
        super().__init__(message)
        
        
class ClientError(Exception):
    pass


class ValidationError(Exception):
    pass


class InsufficientCreditError(Exception):
    pass

class NotFoundError(Exception):
    pass


class ServerError(Exception):
    pass

class BadRequest(Exception):
    pass