# Copyright 2023 Agnostiq Inc.


from rich.console import Console

"""Covalent Cloud SDK Exception module."""


class CovalentSDKError(Exception):
    """Covalent Cloud SDK Base Exception class.

    Attributes:
        message (str): Explanation of the error.
        code (str): String enum representing error analogous to error code.
    """

    def __init__(self, message: str = "Generic Error", code: str = "error/generic") -> None:
        """
        Initializes a new instance of the CovalentSDKError class.

        Args:
            message (str): Explanation of the error.
            code (str): String enum representing error analogous to error code.

        """
        self.message = message
        self.code = code
        super().__init__(f"[{code}] {message}")

    @staticmethod
    def print_error(e: Exception, level: str = "warning") -> None:
        """Print a CovalentSDKError.

        Args:
            e: The CovalentSDKError to print.
            level: The level of the message to print.  Defaults to "warning".

        """

        message = str(e)
        console = Console()
        if level == "warning":
            console.print(f"[bold yellow1]WARNING: {message}[bold yellow1]")
        elif level == "error":
            console.print(f"[bold red1]ERROR: {message}[bold red1]")

    def rich_print(self, level: str = "warning") -> None:
        CovalentSDKError.print_error(self, level)


class CovalentAPIKeyError(CovalentSDKError):
    """Covalent Cloud SDK API Key Error class."""

    def __init__(self, message, code) -> None:
        super().__init__(message, code)


class CovalentGenericAPIError(CovalentSDKError):
    """Covalent Cloud Server Generic API Error class."""

    def __init__(self, error) -> None:
        try:
            error_message = error.response.json()["detail"]
            error_code = error.response.json()["code"]
        except:
            error_message = "Unknown Error"
            error_code = "error/unknown"

        super().__init__(error_message, error_code)


def handle_error(e):
    """Handle a Covalent Cloud SDK Error.

    Args:
        e: The Covalent Cloud SDK Error to handle.

    """
    if isinstance(e, CovalentSDKError):
        e.rich_print(level="error")
    else:
        CovalentSDKError.rich_print(e, level="error")
