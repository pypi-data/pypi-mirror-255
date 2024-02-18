from airfold_common.error import AirfoldError


class APIError(AirfoldError):
    pass


class ForbiddenError(APIError):
    pass


class UnauthorizedError(APIError):
    pass


class ProjectNotFoundError(APIError):
    pass


class ConflictError(APIError):
    pass


class InternalServerError(APIError):
    pass
