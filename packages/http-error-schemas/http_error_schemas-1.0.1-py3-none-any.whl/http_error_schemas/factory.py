from typing import TypedDict, Type
from . import schemas

HTTP_ERRORS = {
    401: schemas.UnauthorizedError,
    404: schemas.NotFoundError,
    409: schemas.ConflictError,
    422: schemas.RequestValidationError,
    500: TypedDict("InternalServerError", {"detail": str}),
}


def get_error_class(status_code: int) -> Type[dict]:
    try:
        return HTTP_ERRORS[status_code]
    except KeyError:
        raise ValueError(f"Status code no in schemas: {status_code}")

