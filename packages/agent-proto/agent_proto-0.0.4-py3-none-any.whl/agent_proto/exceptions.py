"""
Recreated from `fastapi.exceptions` to allow for custom exceptions avoiding installation of the entire FastAPI package.
"""

from http import HTTPStatus
from typing import Any, Dict, Optional

from typing_extensions import Annotated, Doc


class _HTTPException(Exception):
    def __init__(
        self,
        status_code: int,
        detail: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Initializes a new instance of the _HTTPException class.

        Args:
                status_code (int): The HTTP status code.
                detail (str, optional): The detailed error message. Defaults to None.
                headers (Dict[str, str], optional): The HTTP headers. Defaults to None.
        """
        if detail is None:
            detail = HTTPStatus(status_code).phrase
        self.status_code = status_code
        self.detail = detail
        self.headers = headers

    def __str__(self) -> str:
        return f"{self.status_code}: {self.detail}"

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, detail={self.detail!r})"


class HTTPException(_HTTPException):
    """
    Represents an HTTP exception that can be raised to send a specific status code,
    detail, and headers in the response to the client.
    """

    def __init__(
        self,
        status_code: Annotated[
            int,
            Doc(
                """
				HTTP status code to send to the client.
				"""
            ),
        ],
        detail: Annotated[
            Any,
            Doc(
                """
				Any data to be sent to the client in the `detail` key of the JSON
				response.
				"""
            ),
        ] = None,
        headers: Annotated[
            Optional[Dict[str, str]],
            Doc(
                """
				Any headers to send to the client in the response.
				"""
            ),
        ] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
