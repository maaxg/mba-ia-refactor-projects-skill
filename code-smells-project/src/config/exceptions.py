"""Domain exceptions — raised by controllers/models, mapped to HTTP by the error handler.

This removes the need for per-route try/except that leaked internal error text (str(e)).
"""


class AppError(Exception):
    status_code = 500

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


class ValidationError(AppError):
    status_code = 400


class NotFoundError(AppError):
    status_code = 404


class UnauthorizedError(AppError):
    status_code = 401
