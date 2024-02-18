from dataclasses import dataclass


@dataclass(frozen=True)
class Error:
    """Error returned from API endpoints

    Attributes:
        status_code: Response status code
        code: Error code
        message: Error description
    """

    status_code: int | None
    code: str
    message: str
