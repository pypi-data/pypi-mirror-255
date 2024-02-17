"""Tools that operates on objects being diffed."""
from dataclasses import dataclass
from enum import Enum
from typing import Any

from classdiff.utils import Font


@dataclass
class Format:
    """Format is a class that knows how to format an object."""

    identifier: str = ""
    _opening_symbol: str = "{"
    _closing_symbol: str = "}"
    _object_type: str = "dict"

    def __init__(
        self,
        *,
        identifier: str | None = None,
        old_object: Any = None,
        new_object: Any = None,
    ):
        """Constructor."""
        self._object_type = "dict"

        if identifier is not None:
            self.identifier = identifier
            self._opening_symbol = "("
            self._closing_symbol = ")"

        # If we have two different objects, treat it as a dict.
        if (
            old_object is not None
            and new_object is not None
            and type(old_object) != type(new_object)
        ):
            self.identifier = (
                f"{Font.STRIKETHROUGH}"
                f"{old_object.__class__.__name__}{Font.NO_STRIKETHROUGH} "
                f"=> {new_object.__class__.__name__}"
            )
            self._opening_symbol = "("
            self._closing_symbol = ")"

            return

        # Or if both were None, just return
        if old_object is None and new_object is None:
            return

        # Use the name from either the old or new object depending on which one
        # is defined, unless it's a dict or enum.
        if (
            new_object is not None
            and not isinstance(new_object, dict)
            and not isinstance(new_object, Enum)
        ):
            self.identifier = new_object.__class__.__name__
            self._object_type = "object"
            self._opening_symbol = "("
            self._closing_symbol = ")"

        if (
            old_object is not None
            and not isinstance(old_object, dict)
            and not isinstance(old_object, Enum)
        ):
            self.identifier = old_object.__class__.__name__
            self._object_type = "object"
            self._opening_symbol = "("
            self._closing_symbol = ")"

    def prefix(self) -> str:
        """Generate prefix for the format type."""
        return f"{self.identifier}{self._opening_symbol}"

    def suffix(self) -> str:
        """Generate suffix for the format type."""
        return self._closing_symbol
