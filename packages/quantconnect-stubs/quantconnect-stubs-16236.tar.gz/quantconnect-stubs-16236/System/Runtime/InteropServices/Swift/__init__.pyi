from typing import overload
import typing

import System.Runtime.InteropServices.Swift


class SwiftSelf:
    """Represents the Swift 'self' context, indicating that the argument is the self context."""

    @property
    def Value(self) -> typing.Any:
        """Gets the pointer of the self context."""
        ...

    def __init__(self, value: typing.Any) -> None:
        """
        Creates a new instance of the SwiftSelf struct with the specified pointer value.
        
        :param value: The pointer value representing the self context.
        """
        ...


class SwiftError:
    """Represents the Swift error context, indicating that the argument is the error context."""

    @property
    def Value(self) -> typing.Any:
        """Gets the pointer of the error context."""
        ...

    def __init__(self, value: typing.Any) -> None:
        """
        Creates a new instance of the SwiftError struct with the specified pointer value.
        
        :param value: The pointer value representing the error context.
        """
        ...


