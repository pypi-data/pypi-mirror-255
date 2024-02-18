from typing import Any, TypedDict


class RequestValidationError(TypedDict):  # 422
    loc: list[str]
    msg: str
    type: str


class ConflictError(TypedDict):  # 409
    loc: list[str]
    type: str
    msg: str
    info: dict[str, Any]


class UnauthorizedError(TypedDict):  # 401
    loc: list[str]
    type: str
    msg: str


class NotFoundInfo(TypedDict):
    collection: str
    filters: dict[str, Any]


class NotFoundError(TypedDict):  # 404
    loc: list[str]
    type: str
    msg: str
    info: NotFoundInfo


class HTTPErrorDetails(TypedDict):
    detail: list[
        RequestValidationError | ConflictError | UnauthorizedError | NotFoundError
    ]
