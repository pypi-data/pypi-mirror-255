# -*- coding: utf-8 -*-


class UnknownTokenError(Exception):
    """401 error when server cannot find the token"""

    def __init__(self, msg="Invalid token"):
        self.msg = msg
        super().__init__(self.msg)


class NoAuthorizationError(Exception):
    """403 error when server won't allow the upload"""

    def __init__(self, msg="No authorization"):
        self.msg = msg
        super().__init__(self.msg)


class BucketNotFoundError(Exception):
    """404 error when server can't find the reqeusted bucket"""

    def __init__(self, msg="Cannot find requested bucket"):
        self.msg = msg
        super().__init__(self.msg)


class BadMethodError(Exception):
    """405 error when called with an unsupported method"""

    def __init__(self, msg="Unsupported method called"):
        self.msg = msg
        super().__init__(self.msg)


class FileConflictError(Exception):
    """409 error when file already on the server"""

    def __init__(self, msg="Conflict: file already on server"):
        self.msg = msg
        super().__init__(self.msg)
