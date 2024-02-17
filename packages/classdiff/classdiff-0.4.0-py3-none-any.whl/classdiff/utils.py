"""Utils for producing diff."""
from typing import ClassVar, Protocol


# https://stackoverflow.com/a/55240861/2274551
class IsDataclass(Protocol):
    """IsDataclass is the most reliable way to check for a dataclass."""

    __dataclass_fields__: ClassVar[dict]


class Font:
    """
    Font is a class container for available colors and text formatting.

    It's important to reset the value with ENDC to reset to default formatting.
    """

    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    NO_BOLD = "\033[22m"
    UNDERLINE = "\033[4m"
    NO_UNDERLINE = "\033[24m"
    STRIKETHROUGH = "\033[9m"
    NO_STRIKETHROUGH = "\033[29m"
